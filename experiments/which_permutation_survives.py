# ABOUTME: Narrows the within-sentence transposition by testing fixed rules against the
# ABOUTME: exact edge cells and a deep scan, excluding reversal and every small rotation.
"""The order is permuted, and it is not a reversal or a small rotation.

`which_transposition.py` left the permutation unidentified: reversal, rotation and
scrambling all fitted. That was a power problem, and it had two causes -- the longest-block
position collapses a span to one number, and the +-4 offset profile was computed only on
spans of nine blocks or more.

Two sharper statistics separate them.

## The exact edge cells, over every span of three blocks or more

Binning dilutes the thing that discriminates: a ten-bin curve smears English's single long
final word from +1.17 down to +0.35 in the first bin, and then every rule fits. The exact
first and last blocks keep the contrast, and 133 spans carry them:

    the body   FIRST +0.07 +- 0.23   LAST -0.29 +- 0.20

| rule | FIRST | z | LAST | z | chi2(2) |
|---|---|---|---|---|---|
| **identity** | -0.66 +- 0.26 | +2.08 | +1.17 +- 0.27 | **-4.31** | **22.9** |
| **reverse** | +1.17 +- 0.27 | **-3.06** | -0.66 +- 0.26 | +1.11 | **10.6** |
| rotate 1 | -0.19 +- 0.17 | +0.92 | -0.72 +- 0.25 | +1.32 | 2.6 |
| rotate 2 | -0.07 +- 0.12 | +0.53 | -0.17 +- 0.18 | -0.47 | 0.5 |
| scramble | +0.00 +- 0.08 | +0.28 | -0.01 +- 0.08 | -1.27 | 1.7 |

The edge cells reject the identity and the reversal. They cannot reach a rotation, which
moves the long word off **both** edges.

## The full profile reaches the small rotations

A rotation by k parks the long word at offset -(1+k), so the +-4 window sees k up to 3:

| rule | chi2(8) | P |
|---|---|---|
| identity | 33.3 | **0.0001** |
| reverse | 17.6 | **0.024** |
| rotate 1 | 25.5 | **0.0013** |
| rotate 2 | 29.6 | **0.0002** |
| rotate 3 | 18.1 | **0.021** |
| rotate 6 | 7.9 | 0.447 |
| scramble | 7.6 | 0.472 |

## The deep scan reaches the rest

Scanning from the span end as far as the spans allow, using every span long enough at
each offset:

    offset   -1    -2    -3    -4    -5    -6    -7    -8    -9   -10   -11   -12
    body   -0.25 -0.00 -0.22 +0.11 -0.11 -0.20 +0.17 +0.05 -0.18 -0.08 -0.47 +0.37
    spans   128   122   114   108   102    97    89    85    83    79    74    68

**No offset carries a parked long word.** The largest gap anywhere in the window is
+0.37 +- 0.30 at offset -12, which is 2.1 sigma below the +1.19 a rotation parking the
word there would give. Rotations by 0 through 11 are all disfavoured, most of them
strongly.

## What survives

A permutation that leaves the sentence-final word more than twelve blocks from the end --
which for a median span of 13 blocks is most of them -- or one that **varies from sentence
to sentence**. A single fixed rule applied to every sentence is out.

That matters for inverting it: a fixed rule would be recoverable from the statistics
alone, and a varying one needs a key.

    python which_permutation_survives.py
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

from are_the_words_transposed import OFFSETS, profile  # noqa: E402
from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import body_spans  # noqa: E402
from which_transposition import apply_rule  # noqa: E402

RULES = (
    "identity",
    "reverse",
    "rotate 1",
    "rotate 2",
    "rotate 3",
    "rotate 6",
    "scramble",
)
ENGLISH_FINAL = 1.19
MAX_OFFSET = 12
MIN_SPANS = 25


def edges(spans):
    kept = [s for s in spans if len(s) >= 3]
    interior = np.array([x for s in kept for x in s[1:-1]], float)

    def gap(values):
        v = np.array(values, float)
        return (
            float(v.mean() - interior.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                interior.std(ddof=1) / math.sqrt(len(interior)),
            ),
        )

    return gap([s[0] for s in kept]), gap([s[-1] for s in kept]), len(kept)


def deep_profile(spans):
    """Gap at offset -j from the span end, using every span long enough."""
    out = {}
    for j in range(1, MAX_OFFSET + 1):
        kept = [s for s in spans if len(s) >= j + 3]
        if len(kept) < MIN_SPANS:
            continue
        v = np.array([s[len(s) - j] for s in kept], float)
        interior = np.array([x for s in kept for x in s[1 : len(s) - j]], float)
        out[-j] = (
            float(v.mean() - interior.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                interior.std(ddof=1) / math.sqrt(len(interior)),
            ),
            len(kept),
        )
    return out


def main() -> None:
    rng = random.Random(3301)
    registers = [
        register_spans(p, rng) for p in (fetch(n) for n in REGISTERS) if p is not None
    ]
    body = body_spans()
    (bf, bf_se), (bl, bl_se), n = edges(body)

    print(f"The exact edge cells, {n} spans.\n")
    print(
        f"the body   FIRST {bf:+.2f} +- {bf_se:.2f}   LAST {bl:+.2f} +- {bl_se:.2f}\n"
    )
    print(f"{'rule':<14}{'FIRST':>18}{'z':>8}{'LAST':>18}{'z':>8}{'chi2(2)':>9}")
    for rule in RULES:
        r = random.Random(11)
        firsts, lasts = [], []
        for spans in registers:
            (f, _), (l, _), _ = edges(apply_rule(spans, rule, r))
            firsts.append(f)
            lasts.append(l)
        fm, fsd = float(np.mean(firsts)), float(np.std(firsts, ddof=1))
        lm, lsd = float(np.mean(lasts)), float(np.std(lasts, ddof=1))
        zf = (bf - fm) / math.hypot(bf_se, fsd)
        zl = (bl - lm) / math.hypot(bl_se, lsd)
        print(
            f"{rule:<14}{f'{fm:+.2f} +- {fsd:.2f}':>18}{zf:>+8.2f}"
            f"{f'{lm:+.2f} +- {lsd:.2f}':>18}{zl:>+8.2f}{zf * zf + zl * zl:>9.1f}"
        )

    print("\nThe full +-4 profile, which reaches rotations up to k = 3.\n")
    body_profile = profile(body)
    print(f"{'rule':<14}{'chi2(8)':>9}{'P':>9}")
    for rule in RULES:
        r = random.Random(11)
        per = [profile(apply_rule(s, rule, r)) for s in registers]
        chi = 0.0
        for o in OFFSETS:
            m = float(np.mean([p[o][0] for p in per]))
            sd = float(np.std([p[o][0] for p in per], ddof=1))
            chi += ((body_profile[o][0] - m) / math.hypot(body_profile[o][1], sd)) ** 2
        print(f"{rule:<14}{chi:>9.1f}{1 - stats.chi2.cdf(chi, len(OFFSETS)):>9.4f}")

    print("\nThe deep scan, for rotations the window above cannot reach.\n")
    deep = deep_profile(body)
    print(f"{'offset':>7}{'spans':>7}{'body gap':>17}{'z vs a parked long word':>26}")
    best = None
    for j in sorted(deep, reverse=True):
        g, se, spans = deep[j]
        z = (g - ENGLISH_FINAL) / math.hypot(se, 0.26)
        if best is None or g > best[1]:
            best = (j, g, se, z)
        print(f"{j:>+7}{spans:>7}{f'{g:+.2f} +- {se:.2f}':>17}{z:>+26.2f}")
    print(
        f"\n  largest gap anywhere: {best[1]:+.2f} +- {best[2]:.2f} at offset "
        f"{best[0]:+d}, which is {best[3]:+.2f} from +{ENGLISH_FINAL:.2f}"
    )

    print(
        "\nIdentity, reversal and rotations by one to three are rejected by the profile;"
        "\nthe deep scan finds no parked long word out to offset -12. What survives is a"
        "\npermutation that varies from sentence to sentence, or one fixed rule that"
        "\nmoves the final word more than twelve blocks from the end."
        "\n\nThat matters for inverting it: a fixed rule is recoverable from statistics"
        "\nalone, a varying one needs a key."
    )


if __name__ == "__main__":
    main()
