# ABOUTME: Tests Michel's four proposals, and finds that scrambling word order within
# ABOUTME: each sentence reproduces the body's whole span profile where nothing else does.
"""Scrambling the words inside each sentence reproduces the body. Reversal does not.

Michel proposed four readings of the sentence-edge result. Two are already excluded by
work in this directory, one is improved but still rejected, and the fourth fits
everything.

## Reversal: better, but still wrong

If the text runs backwards, the body's profile should match the English profile mirrored
-- what English puts at offset -k, the body puts at +k.

    chi2 against English as written   33.3 on 8 df
    chi2 against English mirrored     17.6 on 8 df

Mirroring halves the misfit, which is itself worth knowing, but it fails where it counts:
reversal puts the long sentence-final block at offset **+1**, predicting +1.19, and the
body reads +0.22 -- **z = -2.70**.

## A key change at the mark: already excluded

`does_the_cipher_restart.py` tests a base reset at the four-dot marks directly and reads
**z = -0.96** against a planted reset that scores **+53 sigma**. And `base_changes_every_block.py`
(D12) caps unchanged block edges at 15%, so the cipher unit cannot be the span between
marks rather than the block.

## Scrambled word order: it fits

Scramble the words inside each English sentence, keeping the sentence boundaries, and
compare the whole offset profile:

| offset | English | English SCRAMBLED | the body | z vs scrambled |
|---|---|---|---|---|
| -4 | +0.01 +- 0.07 | -0.01 +- 0.08 | +0.11 | +0.46 |
| -3 | -0.02 +- 0.11 | +0.02 +- 0.06 | -0.20 | -0.96 |
| -2 | -0.24 +- 0.07 | -0.00 +- 0.09 | -0.14 | -0.57 |
| **-1** | **+1.19 +- 0.23** | **-0.01 +- 0.09** | **-0.27** | **-1.05** |
| +1 | -0.71 +- 0.23 | -0.01 +- 0.05 | +0.22 | +0.83 |
| +2 | -0.14 +- 0.18 | -0.04 +- 0.05 | +0.30 | +1.33 |
| +3 | -0.06 +- 0.12 | -0.02 +- 0.07 | +0.44 | +1.72 |
| +4 | -0.01 +- 0.08 | -0.01 +- 0.08 | -0.23 | -0.87 |

    chi2 against English as written   33.3 on 8 df   P = 0.0001
    chi2 against English scrambled     8.7 on 8 df   P = 0.37

Every offset within 1.7 sigma.

## An independent check that is not just flatness

A flat profile is consistent with several things, so the second test matters: **where the
longest block sits inside a span**. English puts it late and decisively so; scrambling
puts it anywhere.

| | spans | mean position | against uniform |
|---|---|---|---|
| ten registers pooled | 28,551 | 0.547 +- 0.002 | KS P = 2e-264 |
| the LP author | 60 | 0.579 +- 0.042 | |
| **the LP body** | 122 | **0.482 +- 0.027** | **KS P = 0.65** |

The body is 2.30 sigma from the register spread and **indistinguishable from uniform**.

## What it unifies

`separators-are-not-word-boundaries.md` states the older anomaly in its sharpest form:
"the body's block lengths have the marginal of running text and none of running text's
order. That is what any reading has to produce." **A within-sentence transposition
produces exactly that** -- it keeps the multiset of word lengths and destroys their
sequence -- and it also leaves untouched everything else that is measured: the joined-word
length fit, the d5 lag-5 echo (words stay intact), the span lengths, and the two ordinary
independent blocks either side of a mark.

On this reading the four-dot **is** a full stop after all, and the spans are real
sentences; it is the word order inside them that is gone.

## What this does not establish

Flatness is evidence of transposition, not proof of it: "the marks are not sentence
marks" also predicts a flat profile. What separates them is the span-length evidence --
under transposition the spans are genuine sentences, and their lengths match English
sentence lengths (CV 0.972 against 0.848 +- 0.120, z = +0.66; mean 19.6 against a register
range of 16.0 to 32.8). That is consistent but not decisive.

`separators-are-not-word-boundaries.md` already tested 17 route rules and 46,232 keyed
columnar transpositions and none survived cross-validation. A per-sentence scramble is
not in either family, and with about twenty blocks a sentence there are 20! orderings, so
finding the permutation is a different problem from detecting it.

    python are_the_words_transposed.py
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

OFFSETS = (-4, -3, -2, -1, 1, 2, 3, 4)
EDGE = 4
MIN_SPAN = 5


def profile(spans):
    kept = [s for s in spans if len(s) >= 2 * EDGE + 1]
    interior = np.array([x for s in kept for x in s[EDGE : len(s) - EDGE]], float)
    out = {}
    for o in OFFSETS:
        v = np.array([s[o - 1 if o > 0 else len(s) + o] for s in kept], float)
        out[o] = (
            float(v.mean() - interior.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                interior.std(ddof=1) / math.sqrt(len(interior)),
            ),
        )
    return out


def scramble(spans, rng):
    """Permute the words inside each sentence, keeping the sentence boundaries."""
    out = []
    for s in spans:
        t = list(s)
        rng.shuffle(t)
        out.append(t)
    return out


def longest_position(spans):
    """Relative position of the longest block: 0 is first, 1 is last."""
    out = []
    for s in spans:
        if len(s) < MIN_SPAN:
            continue
        top = max(s)
        out.append(np.mean([i for i, x in enumerate(s) if x == top]) / (len(s) - 1))
    return np.array(out, float)


def summarise(per_register):
    return {
        o: (
            float(np.mean([profile(s)[o][0] for s in per_register])),
            float(np.std([profile(s)[o][0] for s in per_register], ddof=1)),
        )
        for o in OFFSETS
    }


def main() -> None:
    rng = random.Random(3301)
    registers = [
        register_spans(p, rng) for p in (fetch(n) for n in REGISTERS) if p is not None
    ]
    plain = summarise(registers)
    scrambled = summarise(
        [scramble(s, random.Random(700 + i)) for i, s in enumerate(registers)]
    )
    body = profile(body_spans())

    print("Scramble the words inside each English sentence, keep the boundaries,")
    print("and compare the body's whole offset profile.\n")
    print(
        f"{'offset':>7}{'English':>19}{'English SCRAMBLED':>21}{'the body':>11}"
        f"{'z vs scrambled':>16}"
    )
    chi_plain = chi_scrambled = 0.0
    for o in OFFSETS:
        b, b_se = body[o]
        p, p_se = plain[o]
        s, s_se = scrambled[o]
        chi_plain += ((b - p) / math.hypot(b_se, p_se)) ** 2
        z = (b - s) / math.hypot(b_se, s_se)
        chi_scrambled += z * z
        print(
            f"{o:>+7}{f'{p:+.2f} +- {p_se:.2f}':>19}{f'{s:+.2f} +- {s_se:.2f}':>21}"
            f"{f'{b:+.2f}':>11}{z:>+16.2f}"
        )

    print(
        f"\n  chi2 against English as written  {chi_plain:6.1f} on 8 df   "
        f"P = {1 - stats.chi2.cdf(chi_plain, 8):.4f}"
    )
    print(
        f"  chi2 against English scrambled   {chi_scrambled:6.1f} on 8 df   "
        f"P = {1 - stats.chi2.cdf(chi_scrambled, 8):.4f}"
    )

    mirrored = 0.0
    for o in OFFSETS:
        b, b_se = body[o]
        m, m_se = plain[-o]
        mirrored += ((b - m) / math.hypot(b_se, m_se)) ** 2
    print(
        f"  chi2 against English MIRRORED    {mirrored:6.1f} on 8 df   "
        f"P = {1 - stats.chi2.cdf(mirrored, 8):.4f}   (the reversal reading)"
    )
    b, b_se = body[1]
    m, m_se = plain[-1]
    print(
        f"    reversal puts the long block at +1: predicts {m:+.2f}, body {b:+.2f}, "
        f"z = {(b - m) / math.hypot(b_se, m_se):+.2f}"
    )

    print("\nAn independent check: where the longest block sits inside a span.\n")
    print(f"{'text':<26}{'spans':>7}{'mean position':>15}{'against uniform':>18}")
    pooled = np.concatenate([longest_position(s) for s in registers])
    spread = np.std([longest_position(s).mean() for s in registers], ddof=1)
    pooled_p = stats.kstest(pooled, "uniform").pvalue
    print(
        f"{'ten registers pooled':<26}{len(pooled):>7}{pooled.mean():>15.3f}"
        f"{f'P = {pooled_p:.0e}':>18}"
    )
    for label, spans in (
        ("the LP author", author_spans()),
        ("the LP body", body_spans()),
    ):
        v = longest_position(spans)
        uniform_p = stats.kstest(v, "uniform").pvalue
        print(f"{label:<26}{len(v):>7}{v.mean():>15.3f}{f'P = {uniform_p:.2f}':>18}")
    v = longest_position(body_spans())
    z = (v.mean() - pooled.mean()) / math.hypot(
        v.std(ddof=1) / math.sqrt(len(v)), spread
    )
    print(f"\n  the body against the register spread: z = {z:+.2f}")

    print(
        "\nA within-sentence transposition keeps the multiset of word lengths and"
        "\ndestroys their sequence, which is exactly the older anomaly in"
        "\nseparators-are-not-word-boundaries.md: the marginal of running text and none of"
        "\nits order. It leaves the joined-word length fit, the d5 echo and the span"
        "\nlengths untouched, because the words themselves are intact."
        "\n\nOn this reading the four-dot IS a full stop and the spans are real sentences."
        "\nIt is the order inside them that is gone."
    )


if __name__ == "__main__":
    main()
