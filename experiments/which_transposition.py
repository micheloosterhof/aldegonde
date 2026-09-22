# ABOUTME: Corrects the uniform null for the longest-block test and shows the data say the
# ABOUTME: word order is not the original, without identifying which permutation.
"""The order is not the original. Which permutation it is, these statistics cannot say.

`are_the_words_transposed.py` reported the body's longest-block position as
"indistinguishable from uniform, KS P = 0.65" and read that as support for scrambling.
**Uniform is the wrong null**, and the test has less power than that number suggests.

## Why uniform is wrong

The position is `i / (n - 1)` for a span of n blocks, so under a random permutation it is
uniform on a *discrete* grid whose spacing depends on n. Pooling across span lengths gives
a lumpy distribution, not a flat one. Applying each rule to English and testing against
uniform:

    identity   D = 0.103   P = 2e-264
    reverse    D = 0.103   P = 2e-264
    scramble   D = 0.051   P = 4e-65

**Even scrambling is not uniform.** And the body has 122 spans, so a two-sided KS can only
see D above about 0.123 -- the body's own D of 0.066 against uniform was never going to
reject anything.

## Done properly

Comparing the body against what each rule actually produces:

| rule | longest-block position | | sentence-final gap | |
|---|---|---|---|---|
| | KS D | P | English gap | z vs body |
| **identity** | **0.128** | **0.034** | +1.19 +- 0.23 | **-4.42** |
| reverse | 0.077 | 0.445 | -0.71 +- 0.23 | +1.36 |
| rotate 1 | 0.105 | 0.130 | -0.72 +- 0.23 | +1.36 |
| rotate 3 | 0.083 | 0.356 | -0.05 +- 0.13 | -0.82 |
| scramble | 0.080 | 0.393 | -0.03 +- 0.06 | -0.99 |

Both statistics reject the **identity** and nothing else. The longest-block test rejects
it at P = 0.034, which is much weaker than the P = 0.65 previously quoted implied, and it
cannot separate reversal from rotation from scrambling.

## What still stands, and what does not

**Stands**: the word order inside a span is not the order English would give. That comes
from the full offset profile, where the identity fails at chi2 33.3 on 8 df (P = 0.0001)
and a scramble fits at 8.7 (P = 0.37), and it is confirmed here by a second statistic.

**Does not stand**: that the longest-block position is uniform, or that it supports
scrambling specifically over any other permutation.

**Reversal** remains disfavoured, but by the full profile rather than by this test:
mirrored English gives chi2 17.6 on 8 df, P = 0.024, driven by the offset +1 cell where
reversal predicts +1.19 and the body reads +0.22. On the single final-block cell reversal
actually fits (z = +1.36), so the two cells disagree and the profile is the summary to
quote.

A permutation that differs from sentence to sentence and one fixed for the whole book are
not separated by anything measured here.

    python which_transposition.py
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

from are_the_words_transposed import longest_position  # noqa: E402
from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import body_spans  # noqa: E402

EDGE = 4
RULES = ("identity", "reverse", "rotate 1", "rotate 3", "scramble")


def apply_rule(spans, rule, rng):
    out = []
    for s in spans:
        t = list(s)
        if rule == "reverse":
            t = t[::-1]
        elif rule.startswith("rotate"):
            k = int(rule.split()[1])
            t = t[k:] + t[:k]
        elif rule == "scramble":
            rng.shuffle(t)
        out.append(t)
    return out


def final_gap(spans):
    kept = [s for s in spans if len(s) >= 2 * EDGE + 1]
    interior = np.array([x for s in kept for x in s[EDGE : len(s) - EDGE]], float)
    v = np.array([s[-1] for s in kept], float)
    return (
        float(v.mean() - interior.mean()),
        math.hypot(
            v.std(ddof=1) / math.sqrt(len(v)),
            interior.std(ddof=1) / math.sqrt(len(interior)),
        ),
    )


def main() -> None:
    rng = random.Random(3301)
    registers = [
        register_spans(p, rng) for p in (fetch(n) for n in REGISTERS) if p is not None
    ]
    body = body_spans()
    positions = longest_position(body)
    body_gap, body_se = final_gap(body)

    print("Uniform is the wrong null for the longest-block position: the position is")
    print("i/(n-1), so pooling across span lengths is lumpy even under a scramble.\n")
    print(f"{'rule applied to English':<26}{'D vs uniform':>14}{'P':>11}")
    for rule in RULES:
        r = random.Random(11)
        v = np.concatenate(
            [longest_position(apply_rule(s, rule, r)) for s in registers]
        )
        ks = stats.kstest(v, "uniform")
        print(f"{rule:<26}{ks.statistic:>14.3f}{ks.pvalue:>11.1e}")
    print(
        f"\n  the body has {len(positions)} spans, so a KS can only see D above "
        f"{1.36 / math.sqrt(len(positions)):.3f}"
    )

    print("\nDone properly: the body against what each rule actually produces.\n")
    print(f"{'rule':<20}{'position D':>12}{'P':>8}{'English gap':>18}{'gap z':>9}")
    for rule in RULES:
        r = random.Random(11)
        reference = np.concatenate(
            [longest_position(apply_rule(s, rule, r)) for s in registers]
        )
        ks = stats.ks_2samp(positions, reference)
        r = random.Random(11)
        gaps = [final_gap(apply_rule(s, rule, r))[0] for s in registers]
        mean, spread = float(np.mean(gaps)), float(np.std(gaps, ddof=1))
        z = (body_gap - mean) / math.hypot(body_se, spread)
        print(
            f"{rule:<20}{ks.statistic:>12.3f}{ks.pvalue:>8.3f}"
            f"{f'{mean:+.2f} +- {spread:.2f}':>18}{z:>+9.2f}"
        )
    print(f"\n  the body: gap {body_gap:+.2f} +- {body_se:.2f}")

    print(
        "\nBoth statistics reject the identity and nothing else. The order inside a span"
        "\nis not the order English would give -- that stands, from the full offset"
        "\nprofile (identity chi2 33.3, P = 0.0001; scramble 8.7, P = 0.37) and from the"
        "\nsecond statistic here."
        "\n\nWhat does not stand is the earlier claim that the longest-block position is"
        "\nuniform, or that it supports scrambling over any other permutation. Reversal,"
        "\nrotation and scrambling are not separated by anything measured here; reversal"
        "\nis disfavoured only by the full profile, at P = 0.024."
    )


if __name__ == "__main__":
    main()
