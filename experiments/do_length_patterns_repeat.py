# ABOUTME: Searches for repeated block-length n-grams, which a formulaic plaintext phrase
# ABOUTME: leaves behind even though the cipher gives the phrase a fresh base each time.
"""A repeated plaintext phrase leaves no repeated ciphertext. It leaves repeated lengths.

Reading the author's own koan pages for the first time this session made something plain:
he repeats whole phrases verbatim. *WHO ARE YOU WHO WISHES TO STUDY HERE* occurs three
times across pages 4 to 6, and *THAT IS ONLY WHAT YOU ARE CALLED* echoes it.

Under the walk a repeated phrase produces **nothing** in the ciphertext, because the base
changes at every block and the second occurrence is enciphered under an unrelated
alphabet. `repeated-phrase-dju-bei.md` looks for repeated ciphertext and finds one
six-gram; `word-repeat-accounting.md` prices repeated ciphertext words against a shuffle.

But the cipher is length-preserving, so a repeated phrase **does** leave a repeated
block-length n-gram, and nothing has looked for those.

## The prediction is sharp both ways

`block-lengths-are-detached.md` establishes the body's block lengths are i.i.d. and
"attached to nothing". That predicts the repeated-n-gram count to sit exactly on a shuffle
of the body's own lengths, which preserves the marginal exactly and destroys only the
order.

If instead the body's plaintext is formulaic in the author's manner, it should show an
excess over that shuffle -- and the author's own pages say how big an excess to expect,
because his koan repeats are real and in the corpus.

## Why long n-grams carry the test

At n = 5 the chance floor is about a thousand collisions and a real phrase adds tens: the
signal drowns. By n = 8 the floor is single digits, so one genuine eight-word repeat is
visible. The table therefore runs to n = 10 and the verdict lives at the long end.

## Result: the author's repeats are blatant and the body has none

Repeated length-n patterns, against a shuffle of the same corpus's own lengths.

**The LP author, 719 blocks** -- the power check:

| n | observed | shuffled | z |
|---|---|---|---|
| 5 | 71 | 29.6 +- 6.0 | +6.87 |
| 6 | 41 | 5.0 +- 2.8 | +12.87 |
| 7 | 28 | 0.9 +- 1.1 | +24.82 |
| 8 | 19 | 0.1 +- 0.4 | **+47.16** |
| 9 | 13 | 0.0 +- 0.2 | **+70.37** |
| 10 | 6 | 0.0 +- 0.1 | +60.05 |

**The LP body, 2,896 blocks** -- four times the author's length:

| n | observed | shuffled | z |
|---|---|---|---|
| 5 | 231 | 240.2 +- 14.6 | -0.63 |
| 6 | 37 | 40.0 +- 7.2 | -0.42 |
| 7 | 12 | 5.7 +- 2.8 | +2.28 |
| 8 | **0** | 0.9 +- 1.1 | -0.82 |
| 9 | **0** | 0.2 +- 0.5 | -0.35 |
| 10 | **0** | 0.1 +- 0.2 | -0.25 |

One English register cut to the same length gives +1.69 and +1.84 at n = 5 and 6 and
nothing beyond.

**The body has no formulaic repetition whatever.** Not one repeated eight-block pattern
where the author has nineteen, in a corpus four times as long. The +2.28 at n = 7 is one
cell of six and does not survive its own multiple testing.

## What it settles

**The body's plaintext is not written in the author's koan style.** That style is
detectable here at forty-seven sigma, so this is a decisive difference and not a null for
want of power. It is also an independent confirmation of
`block-lengths-are-detached.md`: the length sequence carries no phrase structure.

For the crib programme it is a closure: there are no repeated long phrases in the body to
exploit, which removes a route `crib-budget-for-g.md` leaves nominally open.

## One caveat it raises against earlier work

`which_edge_is_anomalous.py` argues the sentence-final anomaly cannot be a register effect
because the author's own register lengthens, and that "a register explanation requires the
body to be a different register from the front matter". **This is measured evidence that
the body IS a different register from the author in at least one respect.** The argument
survives because the lengthening is not an author-specific trait -- ten independent
English registers give +0.75 to +1.50 -- but the premise is now weaker than stated and
should not be leaned on.

    python do_length_patterns_repeat.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

LENGTHS = (5, 6, 7, 8, 9, 10)
DRAWS = 200


def stream(spans) -> list[int]:
    return [x for s in spans for x in s]


def repeats(seq, n: int) -> int:
    """Occurrences beyond the first of every length-n pattern that appears again."""
    counts = Counter(tuple(seq[i : i + n]) for i in range(len(seq) - n + 1))
    return sum(c - 1 for c in counts.values() if c > 1)


def null(seq, n: int, rng, draws=DRAWS):
    out = []
    shuffled = list(seq)
    for _ in range(draws):
        rng.shuffle(shuffled)
        out.append(repeats(shuffled, n))
    return np.array(out, float)


def report(label, seq, rng):
    print(f"\n{label}: {len(seq):,} blocks\n")
    print(f"{'n':>4}{'observed':>11}{'shuffled':>20}{'excess':>10}{'z':>8}")
    for n in LENGTHS:
        obs = repeats(seq, n)
        ref = null(seq, n, rng)
        sd = ref.std(ddof=1)
        z = (obs - ref.mean()) / sd if sd > 0 else float("nan")
        print(
            f"{n:>4}{obs:>11,}"
            f"{f'{ref.mean():,.1f} +- {sd:.1f}':>20}{obs - ref.mean():>+10.1f}{z:>+8.2f}"
        )


def main() -> None:
    rng = random.Random(3301)
    body = stream(body_spans())
    author = stream(author_spans())
    registers = [
        stream(register_spans(p, rng))
        for p in (fetch(n) for n in REGISTERS)
        if p is not None
    ]

    print("A shuffle keeps the length marginal exactly and destroys only the order.")
    report("THE LP AUTHOR (his koan repeats phrases verbatim)", author, rng)
    report("THE LP BODY", body, rng)
    trimmed = registers[0][: len(body)]
    report("one English register, cut to the body's length", trimmed, rng)

    print(
        "\n\nThe author's row is the power check. If his known repeats do not show"
        "\nthere, the body's row means nothing either way."
    )


if __name__ == "__main__":
    main()
