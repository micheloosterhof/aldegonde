# ABOUTME: Asks whether a rule-based word shuffle hides behind the wrong unit: the catalogue of
# ABOUTME: sentence shuffles undone on displaced marks, all marks, fixed word blocks, pages, sections.
"""Does a rule restore the order if the sentence boundaries are somewhere else?

The adjacency of block lengths is flat whatever the boundaries (no cuts, cuts at every
mark, cuts at the four-dot), so moving the sentence ends cannot make the order more
English by itself. It can change the unit a rule acts on. `catalogue_of_sentence_
shuffles.py` undid each rule on the four-dot spans only; a rule applied inside a
different unit would be missed. This scans units times rules:

- the four-dot spans with every boundary moved d words, d = -3..3 (a displaced stop);
- spans closed by any cluster mark (four-dot, thirteen-dot, three-dot, ten-dot, quote);
- fixed blocks of k words from each section start, k = 2..24, at every offset;
- pages; sections.

Each (unit, rule) cell undoes the rule on every unit and scores the lag-1 transition
table of length classes against the record's null, words shuffled within the four-dot
spans; one family p-value covers all cells, from the same shuffle draws scored under every
cell. A within-unit shuffle is not a usable null for a unit other than the sentence:
sentences differ in word-length composition, and a block straddling two sentences reads
that difference as order (a prose window shuffled within its sentences scored +9 that way). Rules are the catalogue with keyed column orders up to
width 5. Calibrated on a joined prose window at the body's size with a rule planted
inside fixed blocks of 7 at offset 3 and inside sentences whose stop is two words late,
neither of which the four-dot spans would see.

    python experiments/sentence_boundaries_elsewhere.py [--draws 60] [--quick]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from catalogue_of_sentence_shuffles import (  # noqa: E402
    FIT_DRAWS,
    Corpus,
    catalogue,
    columnar,
    inverse,
)
from frame_feature_nulls import Layout  # noqa: E402
from length_adjacency_self_null import JOIN_RATE, windows  # noqa: E402
from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from within_word_d5 import parse_clean_sections  # noqa: E402

SEED = 20261029
SENTENCE_MARK = "④"
CLUSTER = {"④", "⑬", "③", "⑩", '"'}
PAGE = "%"
MAX_BLOCK = 24


class Text:
    """Word lengths and closers, section by section."""

    def __init__(self, lengths: list[list[int]], closers: list[list[str]]) -> None:
        self.lengths = lengths
        self.closers = closers

    def flat(self) -> list[int]:
        return [x for sec in self.lengths for x in sec]

    def ranges_at(self, closes, shift: int = 0) -> list[tuple[int, int]]:
        """Unit ranges (global indices) ending after each closing word, moved by `shift`."""
        out, base = [], 0
        for lens, cls in zip(self.lengths, self.closers):
            n = len(lens)
            ends = sorted(
                {min(n, max(1, i + 1 + shift)) for i, c in enumerate(cls) if closes(c)}
                | {n}
            )
            start = 0
            for e in ends:
                if e > start:
                    out.append((base + start, base + e))
                    start = e
            base += n
        return out

    def blocks(self, k: int, offset: int) -> list[tuple[int, int]]:
        out, base = [], 0
        for lens in self.lengths:
            n = len(lens)
            cuts = (
                ([offset] if 0 < offset < n else [])
                + list(range(offset + k, n, k))
                + [n]
            )
            start = 0
            for e in cuts:
                if e > start:
                    out.append((base + start, base + e))
                    start = e
            base += n
        return out

    def sections(self) -> list[tuple[int, int]]:
        out, base = [], 0
        for lens in self.lengths:
            out.append((base, base + len(lens)))
            base += len(lens)
        return out


def units_of(text: Text) -> list[tuple[str, list[tuple[int, int]]]]:
    out = []
    for shift in range(-3, 4):
        out.append(
            (
                f"four-dot spans, stops moved {shift:+d}",
                text.ranges_at(lambda c: c == SENTENCE_MARK, shift),
            )
        )
    out.append(("spans at every cluster mark", text.ranges_at(lambda c: c in CLUSTER)))
    out.append(("pages", text.ranges_at(lambda c: c == PAGE)))
    out.append(("sections", text.sections()))
    for k in range(2, MAX_BLOCK + 1):
        for offset in range(k):
            out.append((f"blocks of {k}, offset {offset}", text.blocks(k, offset)))
    return out


def spans_from(flat: list[int], ranges) -> list[list[int]]:
    return [flat[a:b] for a, b in ranges if b - a >= 2]


def plant(flat: list[int], ranges, fn) -> list[int]:
    out = list(flat)
    for a, b in ranges:
        perm = fn(b - a)
        out[a:b] = [flat[a + i] for i in perm]
    return out


def body_text() -> Text:
    path = ROOT / "data/page0-56.txt"
    layout = Layout(path)
    sections = parse_clean_sections(str(path))
    lengths, closers, w = [], [], 0
    for sec in sections:
        lengths.append([len(x) for x in sec])
        closers.append(layout.closer[w : w + len(sec)])
        w += len(sec)
    return Text(lengths, closers)


def rules_subset():
    keep = []
    for label, fn in catalogue():
        if "columnar width 6, columns" in label and not (
            "(0, 1, 2, 3, 4, 5)" in label or "(5, 4, 3, 2, 1, 0)" in label
        ):
            continue
        keep.append((label, fn))
    return keep


class Scan:
    """Chi-square per (unit set, rule), every cell scored against the one null the record
    holds: words shuffled within the four-dot spans. A within-unit shuffle will not do as
    a null for a unit that is not the sentence, because sentences differ in word-length
    composition and pairs inside a block that straddles sentences carry that difference
    as if it were order."""

    def __init__(self, rules, draws: int) -> None:
        self.rules = rules
        self.draws = draws

    @staticmethod
    def shuffled_within(classes: np.ndarray, sentence_ranges, rng) -> np.ndarray:
        out = classes.copy()
        for a, b in sentence_ranges:
            rng.shuffle(out[a:b])
        return out

    def cells(
        self, flat, unit_sets, sentence_ranges, rng
    ) -> tuple[np.ndarray, np.ndarray]:
        """obs (units, rules) and null (draws, units, rules)."""
        from length_adjacency_self_null import length_class  # noqa: PLC0415

        classes = np.array([length_class(x) for x in flat])
        corpora, gathers, indices = [], [], []
        for _, ranges in unit_sets:
            corpus = Corpus(spans_from(flat, ranges))
            corpora.append(corpus)
            gathers.append(
                np.concatenate([np.arange(a, b) for a, b in ranges if b - a >= 2])
            )
            indices.append([corpus.recovery_index(fn) for _, fn in self.rules])
        fit = [
            self.shuffled_within(classes, sentence_ranges, rng)
            for _ in range(FIT_DRAWS)
        ]
        # two separate draw sets: the first standardises every cell, the second is the
        # family null; a draw standardised by a set it belongs to is capped at
        # (n - 1) / sqrt(n) while the observed data is not, which fakes a signal
        null_draws = [
            self.shuffled_within(classes, sentence_ranges, rng)
            for _ in range(2 * self.draws)
        ]
        obs = np.empty((len(unit_sets), len(self.rules)))
        null = np.empty((2 * self.draws, len(unit_sets), len(self.rules)))
        for u, (corpus, gather, idxs) in enumerate(zip(corpora, gathers, indices)):
            tables = np.array([corpus.table(f[gather]) for f in fit])
            mean, sd = tables.mean(axis=0), tables.std(axis=0, ddof=1)
            live = sd > 0

            def chi(t, mean=mean, sd=sd, live=live):
                return float((((t - mean)[live] / sd[live]) ** 2).sum())

            own = classes[gather]
            obs[u] = [chi(corpus.table(own[idx])) for idx in idxs]
            for d, draw in enumerate(null_draws):
                dc = draw[gather]
                null[d, u] = [chi(corpus.table(dc[idx])) for idx in idxs]
        return obs, null

    def report(self, label, flat, unit_sets, sentence_ranges, rng):
        obs, draws = self.cells(flat, unit_sets, sentence_ranges, rng)
        scale, null = draws[: self.draws], draws[self.draws :]
        mean, sd = scale.mean(axis=0), scale.std(axis=0, ddof=1)
        z = (obs - mean) / sd
        z_null = (null - mean) / sd
        top = np.unravel_index(np.argmax(z), z.shape)
        null_top = z_null.reshape(self.draws, -1).max(axis=1)
        print(
            f"\n{label}: {z.size} cells ({len(unit_sets)} unit sets x {len(self.rules)} rules)"
        )
        flat_order = np.argsort(-z, axis=None)[:3]
        for i in flat_order:
            u, r = np.unravel_index(i, z.shape)
            print(f"  {z[u, r]:+6.2f}  {unit_sets[u][0]}; {self.rules[r][0]}")
        print(
            f"  largest z {z[top]:+.2f}; family P = {(null_top >= z[top]).mean():.3f}"
            f" (null largest {null_top.mean():.2f} +- {null_top.std():.2f})"
        )
        best_unit = z.max(axis=1)
        order = np.argsort(-best_unit)[:5]
        print(
            "  best unit sets: "
            + "; ".join(f"{unit_sets[u][0]} {best_unit[u]:+.1f}" for u in order)
        )
        # the smaller families a displaced stop or a mark-defined unit belong to
        winner = None
        for name, pick in (
            (
                "four-dot spans with the stops moved",
                lambda lab: lab.startswith("four-dot"),
            ),
            (
                "mark, page and section units",
                lambda lab: lab.startswith(("spans at", "pages", "sections")),
            ),
        ):
            sel = [u for u, (lab, _) in enumerate(unit_sets) if pick(lab)]
            sub_top = z[sel].max()
            sub_null = z_null[:, sel, :].reshape(len(null), -1).max(axis=1)
            u, r = np.unravel_index(np.argmax(z[sel]), z[sel].shape)
            if winner is None:
                winner = (unit_sets[sel[u]], self.rules[r])
            print(
                f"  family of {name} ({len(sel) * len(self.rules)} cells): largest z {sub_top:+.2f}"
                f" at {unit_sets[sel[u]][0]}; {self.rules[r][0]}; family P = {(sub_null >= sub_top).mean():.3f}"
                f" (null largest {sub_null.mean():.2f} +- {sub_null.std():.2f})"
            )
        return winner


def final_block_check(flat, ranges, fn, label: str, rng: np.random.Generator) -> None:
    """The channel the scan did not use: under the right unit and rule the unit-final
    long block returns (joined prose +1.28 +- 0.24, the author +0.42 +- 0.29)."""
    units = [flat[a:b] for a, b in ranges if b - a >= 6]
    undone = []
    for u in units:
        inv = inverse(fn(len(u)))
        undone.append([u[inv[i]] for i in range(len(u))])
    print(f"\nUnit-final block under {label}, {len(units)} units of 6+ blocks")
    for name, rows in (("as written", units), ("undone", undone)):
        e = np.array([r[-1] - np.mean(r) for r in rows])
        null = []
        for _ in range(2000):
            draw = [rng.permutation(r) for r in rows]
            null.append(np.mean([r[-1] - r.mean() for r in draw]))
        null = np.array(null)
        print(
            f"  {name:<11} last block minus unit mean {e.mean():+.3f} +- {e.std(ddof=1) / len(e) ** 0.5:.3f};"
            f" within-unit shuffle {null.mean():+.3f} +- {null.std(ddof=1):.3f};"
            f" z {(e.mean() - null.mean()) / null.std(ddof=1):+.2f}"
        )


def main() -> None:
    draws = 60
    quick = "--quick" in sys.argv  # the shuffled control and the body only
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])
    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    rules = rules_subset()
    body = body_text()
    size = len(body.flat())
    print(f"body: {size} words in {len(body.lengths)} sections; {len(rules)} rules")

    prose = []
    for number in REGISTERS[:3]:
        path = fetch(number)
        if path is not None:
            prose += [s for s in register_spans(path, rng, JOIN_RATE) if len(s) >= 2]
    window = windows(prose, size, 1, rng)[0]
    # the window as one section with a four-dot after each sentence
    ptext = Text(
        [[x for s in window for x in s]],
        [
            [
                SENTENCE_MARK if i == len(s) - 1 else "①"
                for s in window
                for i in range(len(s))
            ]
        ],
    )
    punits = units_of(ptext)
    scan = Scan(rules, draws)

    print("\nCalibration on a joined prose window at the body's size")
    rule = lambda n: columnar(n, 4, (2, 0, 3, 1), "up")  # noqa: E731
    flat = ptext.flat()
    shuffled = plant(
        flat,
        ptext.ranges_at(lambda c: c == SENTENCE_MARK),
        lambda n: rng.sample(range(n), n),  # a fresh draw per sentence
    )
    psent = ptext.ranges_at(lambda c: c == SENTENCE_MARK)
    scan.report("shuffled within sentences", shuffled, punits, psent, nrng)
    if quick:
        scan.report(
            "planted: keyed columnar width 4 inside sentences whose stop is two words late",
            plant(flat, ptext.ranges_at(lambda c: c == SENTENCE_MARK, 2), rule),
            punits,
            psent,
            nrng,
        )
        print("\nThe body")
        (unit_label, ranges), (rule_label, fn) = scan.report(
            "body",
            body.flat(),
            units_of(body),
            body.ranges_at(lambda c: c == SENTENCE_MARK),
            nrng,
        )
        final_block_check(body.flat(), ranges, fn, f"{unit_label}; {rule_label}", nrng)
        return
    scan.report(
        "planted: keyed columnar width 4 inside blocks of 7, offset 3",
        plant(flat, ptext.blocks(7, 3), rule),
        punits,
        psent,
        nrng,
    )
    scan.report(
        "planted: the same rule inside sentences whose stop is two words late",
        plant(flat, ptext.ranges_at(lambda c: c == SENTENCE_MARK, 2), rule),
        punits,
        psent,
        nrng,
    )

    print("\nThe body")
    (unit_label, ranges), (rule_label, fn) = scan.report(
        "body",
        body.flat(),
        units_of(body),
        body.ranges_at(lambda c: c == SENTENCE_MARK),
        nrng,
    )
    final_block_check(body.flat(), ranges, fn, f"{unit_label}; {rule_label}", nrng)


if __name__ == "__main__":
    main()
