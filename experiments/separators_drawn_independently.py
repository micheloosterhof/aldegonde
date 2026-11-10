# ABOUTME: Tests the null that the body's separators carry no plaintext: placed without
# ABOUTME: regard to the rune stream, or drawn independently from one length marginal.
"""Are the separators independent draws laid over a keyed stream?

The record reads the flat adjacency of block lengths inside a span as a word
permutation (`the-words-are-transposed-within-sentences.md`). A cheaper reading gives the
same flat table with no permutation at all: the block lengths are independent draws from
one marginal and the spans hold no sentences. Two forms, two tests.

**N1, decorative separators.** The separators were laid over a finished rune stream and
the cipher never saw them. Then the within-block lag-5 echo cannot know where the
boundaries are, and re-cutting the same stream with the same block lengths in another
order keeps it. Test A re-cuts the stream with the lengths shuffled, over the whole body
and inside each span, and counts the within-block coincidences at lags 4, 5 and 6. The
number of pairs at each lag is the same in every draw, so the counts compare directly.

**N2, cipher units of independent length.** The cipher does use the separators, but the
lengths come from one marginal, independently, so no sentence exists. A span is then a
random sample of the marginal and the spans differ from each other only by sampling.
Sentences of a language differ by more than that: one is made of long words, the next of
short ones. Test B measures the between-span dispersion of block length (a one-way
between-groups sum of squares over the grand variance, and the same on the share of
blocks of two runes or less) against a shuffle of all lengths across spans, which keeps
every span's block count. The statistic does not depend on the order inside a span, so a
text with its words permuted inside each sentence reads the same as the intact text. It
therefore separates "sentences, permuted inside" from "independent lengths", which the
adjacency table cannot. The calibration runs it on joined prose windows cut to the body's
span count and on the author's solved pages.

    python experiments/separators_drawn_independently.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
from the_gap_depends_on_span_length import author_spans, english_spans  # noqa: E402

from aldegonde.analysis import boundary_permutation_test  # noqa: E402
from aldegonde.stats import z_score  # noqa: E402

SEED = 20261110
DRAWS = 2000
LAGS = (4, 5, 6)
ECHO_LAG = 5
SENTENCE_MARK = "④"
SHORT = 2
WINDOWS = 8


def body_structure() -> tuple[list[list[int]], list[list[int]]]:
    """The blocks and their lengths grouped into four-dot spans."""
    tok = lp_corpus.load_tokenized(join_pages=True)
    words = tok.words()
    lengths = [len(w) for w in words]
    spans: list[list[int]] = []
    current: list[int] = []
    for length, closing in zip(lengths, tok.closing, strict=True):
        current.append(length)
        if closing == SENTENCE_MARK:
            spans.append(current)
            current = []
    if current:
        spans.append(current)
    return words, spans


def recut(words: list[list[int]], spans: list[list[int]], rng: random.Random) -> None:
    """Test A: the echo under the same lengths in another order.

    The null keeps the rune stream and the multiset of block lengths (of the whole body,
    or of every span) and destroys only which boundary falls where."""
    by_span, i = [], 0
    for s in spans:
        by_span.append(words[i : i + len(s)])
        i += len(s)
    print("A. Re-cut the stream with the same block lengths in another order")
    print(f"   {DRAWS} draws; pairs per lag are the same in every draw\n")
    echo_p: list[float] = []
    for scope, sections in (("whole body", [words]), ("inside spans", by_span)):
        print(f"   {'lag':<5}{'body':>7}{f'{scope} shuffle':>26}{'z':>7}{'P>=':>8}")
        for lag in LAGS:
            r = boundary_permutation_test(sections, lag, DRAWS, rng)
            z = z_score(r.observed, r.null_mean, r.null_sd)
            print(
                f"   {lag:<5}{r.observed:>7}"
                f"{f'{r.null_mean:.1f} +- {r.null_sd:.1f}':>26}{z:>+7.2f}{r.p_value:>8.4f}"
            )
            if lag == ECHO_LAG:
                echo_p.append(r.p_value)
        print()
    worst = max(echo_p)
    verdict = "rejected" if worst < 0.01 else "not rejected"
    print(
        f"   Decorative separators (N1): {verdict}. At lag {ECHO_LAG}, the one lag named "
        f"in advance, the\n   weaker of the two re-cuts reads P = {worst:.4f}."
    )


def dispersion(spans: list[list[int]]) -> tuple[float, float]:
    """Between-span sum of squares over the grand variance, for the block length and for
    the indicator of a block of SHORT runes or less. Each is about (spans - 1) when the
    spans are random samples of one marginal."""
    out = []
    flat = np.array([x for s in spans for x in s], float)
    for values in (flat, (flat <= SHORT).astype(float)):
        grand, var = values.mean(), values.var(ddof=1)
        total, i = 0.0, 0
        for s in spans:
            part = values[i : i + len(s)]
            total += len(s) * (part.mean() - grand) ** 2
            i += len(s)
        out.append(total / var)
    return out[0], out[1]


def reshuffled(spans: list[list[int]], rng: random.Random) -> list[list[int]]:
    """All lengths shuffled across spans; every span keeps its block count."""
    flat = [x for s in spans for x in s]
    rng.shuffle(flat)
    out, i = [], 0
    for s in spans:
        out.append(flat[i : i + len(s)])
        i += len(s)
    return out


def dispersion_z(spans: list[list[int]], rng: random.Random, draws: int) -> tuple:
    obs = dispersion(spans)
    null = np.array([dispersion(reshuffled(spans, rng)) for _ in range(draws)])
    res = []
    for k in range(2):
        d = null[:, k]
        z = z_score(obs[k], float(d.mean()), float(d.std(ddof=1)))
        p = (int((d >= obs[k]).sum()) + 1) / (draws + 1)
        res.append((obs[k], float(d.mean()), z, p))
    return tuple(res)


def matched_window(
    pool: list[list[int]], target: list[list[int]], rng: random.Random
) -> list[list[int]]:
    """A run of consecutive prose sentences, as many as the body has spans, each the
    nearest in block count to the body's span at that rank, so the calibration has the
    body's span sizes. Sentences are drawn without replacement from the pool."""
    by_len: dict[int, list[list[int]]] = {}
    for s in pool:
        by_len.setdefault(len(s), []).append(s)
    for v in by_len.values():
        rng.shuffle(v)
    sizes = sorted(by_len)
    out = []
    for t in target:
        want = len(t)
        got: list[int] = []
        # concatenating consecutive sentences would mix compositions, so a long span
        # takes the longest sentences available and is cut to length
        for size in sorted(sizes, key=lambda n: (abs(n - want), -n)):
            if by_len[size]:
                got = by_len[size].pop()
                break
        out.append(got[:want] if len(got) >= want else got)
    return out


def composition(spans: list[list[int]], rng: random.Random) -> None:
    """Test B: do the spans differ in composition by more than sampling?"""
    print("\nB. Between-span dispersion of block length, against all lengths shuffled")
    print("   across spans (every span keeps its block count)\n")
    print(
        f"   {'text':<34}{'spans':>6}{'blocks':>8}"
        f"{'length: stat / null':>22}{'z':>7}{'P>=':>8}"
        f"{'short share: z':>16}{'P>=':>8}"
    )

    def row(name: str, sp: list[list[int]], draws: int) -> tuple[float, float]:
        (o1, m1, z1, p1), (_o2, _m2, z2, p2) = dispersion_z(sp, rng, draws)
        print(
            f"   {name:<34}{len(sp):>6}{sum(map(len, sp)):>8}"
            f"{f'{o1:.1f} / {m1:.1f}':>22}{z1:>+7.2f}{p1:>8.4f}{z2:>+16.2f}{p2:>8.4f}"
        )
        return z1, z2

    body_z = row("the body, four-dot spans", spans, DRAWS)
    row("the body, spans of 3+ blocks", [s for s in spans if len(s) >= 3], DRAWS)
    author = author_spans()
    row("the author's solved pages", author, DRAWS)

    prose = english_spans(rng)
    zs = []
    for i in range(WINDOWS):
        window = matched_window(prose, spans, rng)
        zs.append(row(f"joined prose, body's span sizes #{i + 1}", window, 400))
    zs = np.array(zs)
    print(
        f"\n   joined prose at the body's span sizes: length z {zs[:, 0].mean():+.1f} "
        f"+- {zs[:, 0].std(ddof=1):.1f}, short share z {zs[:, 1].mean():+.1f} "
        f"+- {zs[:, 1].std(ddof=1):.1f} over {WINDOWS} windows"
    )

    # the same windows with independent lengths planted: the test's size
    planted = []
    for _ in range(200):
        (_, _, z1, _), (_, _, z2, _) = dispersion_z(reshuffled(spans, rng), rng, 200)
        planted.append((z1, z2))
    planted = np.array(planted)
    print(
        f"   independent lengths planted on the body's spans: length z "
        f"{planted[:, 0].mean():+.2f} +- {planted[:, 0].std(ddof=1):.2f}, "
        f"short share z {planted[:, 1].mean():+.2f} +- {planted[:, 1].std(ddof=1):.2f}"
    )

    # power: how far apart do sentences and independent lengths sit, in the spread of both
    gap = (zs[:, 0].mean() - planted[:, 0].mean()) / float(
        np.hypot(zs[:, 0].std(ddof=1), planted[:, 0].std(ddof=1))
    )
    power = "has no power" if abs(gap) < 2 else "separates the two"
    side = (
        "inside"
        if abs(body_z[0] - planted[:, 0].mean()) < 2 * planted[:, 0].std(ddof=1)
        else "outside"
    )
    print(
        f"\n   Sentences and independent lengths sit {gap:+.2f} sigma apart on this "
        f"statistic, so it {power}.\n   The body reads {body_z[0]:+.2f}, {side} the "
        f"independent-length band. Independent lengths (N2) are "
        f"{'not tested' if abs(gap) < 2 else 'tested'} by the lengths."
    )


def main() -> None:
    rng = random.Random(SEED)
    words, spans = body_structure()
    print(
        f"body: {sum(map(len, words)):,} runes, {len(words):,} blocks, "
        f"{len(spans)} four-dot spans\n"
    )
    recut(words, spans, rng)
    composition(spans, rng)


if __name__ == "__main__":
    main()
