# ABOUTME: Shows no block-length statistic can separate "spans are transposed sentences"
# ABOUTME: from "the marks are not sentence marks", and says what would be needed instead.
"""Two readings survive, and the length channel cannot tell them apart. Here is why.

`the-words-are-transposed-within-sentences.md` and the older "the marks are not sentence
marks" both predict a flat sentence-edge profile. They differ in what a span *is*:

- **transposition**: the span is a real sentence whose word order has been permuted, so it
  carries exactly that sentence's multiset of word lengths;
- **arbitrary marks**: the span is a run of words cut at points unrelated to the syntax.

That difference sounds measurable, and it is not. Two attempts:

## Span length against internal word length

If a span is a sentence, any link between how long a sentence is and what kind of words it
holds survives transposition, because the multiset is untouched. Measured across ten
registers, English has no such link to preserve:

    r ranges -0.130 to +0.154 over the ten, mean 0.034 +- 0.087

The body reads r = 0.075 (z = +0.33) and arbitrary cuts of the body's own stream read
-0.077. Nothing to detect, because the reference has nothing.

*(One side-finding: the LP author reads r = -0.278, z = -2.07 -- his longer sentences use
slightly shorter words. On 68 spans that is a curiosity, not a result.)*

## The longest block in a span

The sharper version. A sentence contains exactly one sentence-final word; an arbitrary run
of the same length contains a random number of them, so the distribution of the span
maximum should differ. Taking each register's sentences, then cutting the same word stream
into runs of the same lengths at arbitrary points:

    ten registers, sentences        mean max 9.72
    ten registers, cut at random    mean max 9.78
    difference                      -0.058   (spread across registers 0.081)

**The two are the same to within a fifteenth of a rune.** Matched by span length the
picture does not change:

| span length | the body | sentences | cut at random |
|---|---|---|---|
| 4-8 | 7.39 +- 0.48 | 7.87 | 7.96 |
| 9-14 | 8.55 +- 0.36 | 8.94 | 9.05 |
| 15-24 | 9.86 +- 0.33 | 9.82 | 9.81 |
| 25+ | 10.44 +- 0.26 | 10.80 | 10.83 |

## Why no length statistic can work

A sentence and an equally long run of the same text are both samples of the same
word-length distribution. Sentence boundaries carry information about **order** -- which
word is last -- and almost none about the **multiset**. Transposition destroys exactly the
order and keeps exactly the multiset, so it removes the only thing that distinguished
them.

That is not a failure of these two tests. It is why the readings have resisted separation
through every length statistic tried: the edge profile, the longest-block position, the
span dispersion, the span shape.

## What would separate them

**NARROWED, September 2026.** The blanket claim above is too wide. The argument covers
statistics computed inside one span, and the **lag-1 serial correlation of the length
stream** is not one: it is a property of the order, which transposition destroys and
arbitrary marks leave alone. `order_survives_in_the_lengths.py` measures it. The fork is
real; the body sits +0.64 sigma from order intact and -0.08 from transposed, the two arms
are 0.026 apart, and three-sigma separation needs 4.7 times this corpus. So the lengths
still do not separate the readings -- because the surviving statistic is throttled by the
joining nuisance, not because no such statistic exists.

Otherwise: something that is not a length statistic. The only key-free window onto the
plaintext itself is d5 (`d5_across_registers.py`), and it reads *inside* a block, where
transposition changes nothing. Cross-block plaintext structure is hidden because the base changes at
every block edge (D12). So the distinction needs a key, or a channel this corpus does not
have.

    python lengths_cannot_separate_the_readings.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

MIN_SPAN = 4
BANDS = ((4, 8), (9, 14), (15, 24), (25, 99))


def cut_at_random(spans, seed):
    """The same words and the same span lengths, cut at points unrelated to syntax."""
    rng = random.Random(seed)
    flat = [x for s in spans for x in s]
    lengths = [len(s) for s in spans]
    rng.shuffle(lengths)
    out, i = [], 0
    for length in lengths:
        if i + length > len(flat):
            break
        out.append(flat[i : i + length])
        i += length
    return out


def length_relation(spans):
    kept = [s for s in spans if len(s) >= MIN_SPAN]
    n = np.array([len(s) for s in kept], float)
    m = np.array([np.mean(s) for s in kept], float)
    r, p = stats.pearsonr(n, m)
    return float(r), float(p), len(kept)


def maxima(spans):
    return np.array([max(s) for s in spans if len(s) >= MIN_SPAN], float)


def main() -> None:
    rng = random.Random(3301)
    registers = [
        (n, register_spans(p, rng))
        for n, p in ((n, fetch(n)) for n in REGISTERS)
        if p is not None
    ]

    print("Attempt 1: does a span's length predict the words inside it?\n")
    print(f"{'text':<28}{'spans':>8}{'r':>9}{'P':>10}")
    rs = []
    for n, spans in registers:
        r, p, k = length_relation(spans)
        rs.append(r)
        print(f"pg{n:<26}{k:>8,}{r:>9.3f}{p:>10.2e}")
    rs = np.array(rs)
    print(
        f"{'across ten':<28}{'':>8}{rs.mean():>9.3f}   spread +- {rs.std(ddof=1):.3f}"
    )
    for label, spans in (
        ("the LP author", author_spans()),
        ("the LP body", body_spans()),
    ):
        r, p, k = length_relation(spans)
        z = (r - rs.mean()) / math.hypot(rs.std(ddof=1), 1 / math.sqrt(max(k - 3, 1)))
        print(f"{label:<28}{k:>8}{r:>9.3f}{p:>10.3f}   z = {z:+.2f}")
    print("  English has no consistent link, so there is nothing for the body to fail.")

    print("\nAttempt 2: the longest block in a span.\n")
    sentence_max, cut_max = [], []
    for n, spans in registers:
        sentence_max.append(maxima(spans).mean())
        cut_max.append(maxima(cut_at_random(spans, n)).mean())
    sentence_max, cut_max = np.array(sentence_max), np.array(cut_max)
    print(f"{'ten registers, sentences':<32}{sentence_max.mean():>9.2f}")
    print(f"{'ten registers, cut at random':<32}{cut_max.mean():>9.2f}")
    print(
        f"{'difference':<32}{sentence_max.mean() - cut_max.mean():>9.3f}"
        f"   spread {np.std(sentence_max - cut_max, ddof=1):.3f}"
    )

    print("\nMatched by span length.\n")
    print(f"{'span length':<14}{'the body':>16}{'sentences':>12}{'cut at random':>15}")
    for lo, hi in BANDS:
        b = np.array([max(s) for s in body_spans() if lo <= len(s) <= hi], float)
        if len(b) < 8:
            continue
        s_means, c_means = [], []
        for n, spans in registers:
            s_means.append(np.mean([max(s) for s in spans if lo <= len(s) <= hi]))
            c_means.append(
                np.mean([max(s) for s in cut_at_random(spans, n) if lo <= len(s) <= hi])
            )
        print(
            f"{f'{lo}-{hi}':<14}"
            f"{f'{b.mean():.2f} +- {b.std(ddof=1) / math.sqrt(len(b)):.2f}':>16}"
            f"{np.mean(s_means):>12.2f}{np.mean(c_means):>15.2f}"
        )

    print(
        "\nA sentence and an equally long run of the same text are both samples of one"
        "\nword-length distribution. Sentence boundaries carry information about ORDER --"
        "\nwhich word is last -- and almost none about the multiset. Transposition destroys"
        "\nexactly the order and keeps exactly the multiset, so it removes the only thing"
        "\nthat told the two readings apart."
        "\n\nSeparating them needs something that is not a length statistic. d5 reads"
        "\ninside a block, where transposition changes nothing, and cross-block plaintext"
        "\nstructure is hidden by the base changing at every block edge."
    )


if __name__ == "__main__":
    main()
