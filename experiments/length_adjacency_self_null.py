# ABOUTME: Tests whether adjacent block lengths inside a span depend on each other, scored
# ABOUTME: against the corpus's own within-span shuffle, with a power calibration on prose.
"""Do neighbouring block lengths inside a span depend on each other?

Every positional test of the spans (first block, last block, relative-position profile)
needed a reference or was answered by the body's own within-span shuffle. Adjacency is the
one order property left: under "the marks are sentence ends and the words are permuted
within each span" the length of block i+1 is independent of block i; under "the order is
intact" it carries English's word-length dependence. `order_survives_in_the_lengths.py`
measured a Pearson lag-1 against references and found the fork six times too small for
the corpus. This measures the dependence as a transition table over five length classes,
which sees what Pearson cannot (after a two-rune block the next is rarely two runes; after
a long block the next is often short), and scores it against the corpus's OWN within-span
shuffle, which keeps every span's multiset and destroys only adjacency. No reference enters.

The statistic is the chi-square of the observed table against the shuffle's cell means and
sds; its null distribution comes from a second set of shuffles. The calibration runs the
same statistic on prose and on the author's solved pages with the body's joining applied
(q = 0.40), each cut to the body's block count, so the question "how many sigma does
intact order give at this corpus size" is answered before the body is read.

    python experiments/length_adjacency_self_null.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import spans  # noqa: E402
from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402
from within_word_d5 import parse_clean_sections  # noqa: E402

from aldegonde import c3301  # noqa: E402

SEED = 20261027
JOIN_RATE = 0.40
DRAWS = 400
EDGES = (2, 3, 4, 6)  # classes: 1-2, 3, 4, 5-6, 7+
WINDOWS = 6
# other class cuts, and the same table over pairs whose blocks are both 3+ runes, which
# removes every pair the joining model could have touched
VARIANTS = (
    ("classes 1-2/3/4/5-6/7+", EDGES, 1),
    ("classes 1/2/3/4-5/6+", (1, 2, 3, 5), 1),
    ("classes 1-2/3-4/5-6/7+", (2, 4, 6), 1),
    ("classes 1-3/4-5/6-8/9+", (3, 5, 8), 1),
    ("both blocks 3+, classes 3/4/5-6/7+", (3, 4, 6), 3),
)


def length_class(n: int, edges=EDGES) -> int:
    return sum(n > e for e in edges)


def table(spans, edges=EDGES, floor: int = 1) -> np.ndarray:
    """Counts of (class of block i, class of block i+1) over adjacent pairs inside spans
    whose blocks are both at least `floor` runes."""
    k = len(edges) + 1
    t = np.zeros((k, k))
    for s in spans:
        for a, b in zip(s, s[1:]):
            if a >= floor and b >= floor:
                t[length_class(a, edges), length_class(b, edges)] += 1
    return t


def shuffled(spans, rng):
    out = []
    for s in spans:
        s = list(s)
        rng.shuffle(s)
        out.append(s)
    return out


def lag1(spans) -> float:
    left = [x for s in spans for x in s[:-1]]
    right = [x for s in spans for x in s[1:]]
    return float(np.corrcoef(left, right)[0, 1])


def score(spans, rng, draws=DRAWS, edges=EDGES, floor: int = 1) -> dict:
    """Chi-square of the adjacency table against the within-span shuffle, with its null."""

    def table_of(rows):
        return table(rows, edges, floor)

    fit = np.array([table_of(shuffled(spans, rng)) for _ in range(draws)])
    mean, sd = fit.mean(axis=0), fit.std(axis=0, ddof=1)
    live = sd > 0

    def chi(t):
        return float((((t - mean)[live] / sd[live]) ** 2).sum())

    null = np.array([chi(table_of(shuffled(spans, rng))) for _ in range(draws)])
    obs = chi(table_of(spans))
    r_null = np.array([lag1(shuffled(spans, rng)) for _ in range(draws)])
    r = lag1(spans)
    return {
        "blocks": sum(len(s) for s in spans),
        "pairs": int(table_of(spans).sum()),
        "chi": obs,
        "null_mean": float(null.mean()),
        "null_sd": float(null.std(ddof=1)),
        "z": (obs - null.mean()) / null.std(ddof=1),
        "p": float((null >= obs).mean()),
        "lag1": r,
        "lag1_z": (r - r_null.mean()) / r_null.std(ddof=1),
        "table": table_of(spans),
        "mean": mean,
        "sd": sd,
    }


def windows(spans, blocks: int, count: int, rng) -> list[list[list[int]]]:
    """`count` contiguous runs of spans holding about `blocks` blocks each."""
    total = sum(len(s) for s in spans)
    out = []
    for _ in range(count):
        start = rng.randrange(len(spans))
        run, n = [], 0
        for s in spans[start:]:
            if n >= blocks:
                break
            run.append(s)
            n += len(s)
        if n >= blocks * 0.9 or total < blocks:
            out.append(run)
    return out


def row(label: str, r: dict) -> None:
    print(
        f"{label:<44}{r['blocks']:>7}{r['pairs']:>7}{r['chi']:>8.1f}"
        f"{r['null_mean']:>8.1f}{r['null_sd']:>6.1f}{r['z']:>7.2f}{r['p']:>8.3f}"
        f"{r['lag1']:>8.3f}{r['lag1_z']:>7.2f}"
    )


def header() -> None:
    print(
        f"{'corpus':<44}{'blocks':>7}{'pairs':>7}{'chi2':>8}{'null':>8}{'sd':>6}"
        f"{'z':>7}{'P':>8}{'lag-1':>8}{'z':>7}"
    )


def main() -> None:
    rng = random.Random(SEED)
    body = [s for s in body_spans() if len(s) >= 2]
    size = sum(len(s) for s in body)
    author = [s for s in author_spans() if len(s) >= 2]
    author_joined = [
        s
        for s in (join(list(s), JOIN_RATE, rng, forward=True) for s in author)
        if len(s) >= 2
    ]

    print("Calibration: intact order, scored against its own within-span shuffle\n")
    header()
    row("the author, raw", score(author, rng))
    row(f"the author, joined q={JOIN_RATE}", score(author_joined, rng))
    print()

    zs = []
    for number in REGISTERS[:5]:
        path = fetch(number)
        if path is None:
            continue
        prose = [s for s in register_spans(path, rng, JOIN_RATE) if len(s) >= 2]
        for i, w in enumerate(windows(prose, size, WINDOWS, rng)):
            r = score(w, rng, draws=200)
            zs.append(r["z"])
            row(f"pg{number} joined, window {i} at the body's size", r)
    zs = np.array(zs)
    print(
        f"\nprose at the body's size: z = {zs.mean():.2f} +- {zs.std(ddof=1):.2f} over {len(zs)} windows"
        f" (min {zs.min():.2f}, max {zs.max():.2f})"
    )

    print("\nTransposed control: the author's joined spans, shuffled once\n")
    header()
    row("the author, joined, then shuffled", score(shuffled(author_joined, rng), rng))

    print("\nThe body\n")
    header()
    r = score(body, rng)
    row("the body, four-dot spans", r)
    sections = [
        [len(w) for w in sec]
        for sec in parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    ]
    row("the body, cut at sections only", score(sections, rng))
    row(
        "the body, cut at every cluster mark",
        score(spans(set(c3301.CLUSTER_MARKS), minimum=2), rng),
    )
    print(
        "\nbody adjacency table (observed / shuffle mean), rows = class of block i, cols = block i+1"
    )
    names = ["1-2", "3", "4", "5-6", "7+"]
    print(f"{'':>6}" + "".join(f"{n:>14}" for n in names))
    for i in range(len(names)):
        cells = "".join(
            f"{int(r['table'][i, j]):>6}/{r['mean'][i, j]:>7.1f}"
            for j in range(len(names))
        )
        print(f"{names[i]:>6}{cells}")

    print(
        "\nOther class cuts, and pairs of 3+ rune blocks only (joining cannot reach them)\n"
    )
    print(f"{'variant':<40}{'author joined z':>16}{'prose window z':>16}{'body z':>10}")
    prose = [
        s for s in register_spans(fetch(REGISTERS[0]), rng, JOIN_RATE) if len(s) >= 2
    ]
    window = windows(prose, size, 1, rng)[0]
    for label, edges, floor in VARIANTS:
        za = score(author_joined, rng, 200, edges, floor)["z"]
        zp = score(window, rng, 200, edges, floor)["z"]
        zb = score(body, rng, 200, edges, floor)["z"]
        print(f"{label:<40}{za:>16.2f}{zp:>16.2f}{zb:>10.2f}")


if __name__ == "__main__":
    main()
