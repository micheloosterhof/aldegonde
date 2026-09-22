# ABOUTME: Counts long blocks in a window around each four-dot, which separates a displaced
# ABOUTME: stop from a within-span transposition where the mean profile cannot.
"""Displacement keeps the long block near the mark. Transposition scatters it.

Two readings of the four-dot survive that both tie it to a sentence end
(`are_the_four_dot_gaps_memoryless.py` shows the gap law fits thinned sentence ends, which
the third reading has no account of):

- **a variably displaced stop** -- the mark is written a block or two off the true stop, so
  the sentence's long final block is still within a short window of it;
- **within-span transposition** -- the words were permuted before encipherment, so that
  long block is somewhere in a span of 21 blocks and nowhere in particular.

`the_long_block_is_nowhere.py` scores each offset's **mean** and finds nothing. A mean
cannot do this: English puts +1.19 at offset -1 and -0.71 at +1, so a window containing
both averages them away, which is why the window-mean and window-maximum attempts in
`a_shifted_stop_or_a_switched_key.py` had no power (planting a shift moved the statistic
by 0.03).

A **count of long blocks** does not cancel. English's sentence-final word raises the share
of blocks at 7+ runes by 0.152 over the span interior and its sentence-initial word lowers
it by only 0.066, so the net over a window is positive and roughly conserved as the window
widens. Under displacement that whole excess sits inside a window of 2k+1 blocks; under
transposition it is spread over the ~21 blocks of a span and is invisible at any window.

## A correction: the first version of this file chose a span floor that broke it

It required spans of **8 blocks or more**. The LP author's spans average 7.65, so that
filter kept only 40 of his 75 and those were his longest. Under it his sentence-final 7+
lift read +0.037 +- 0.058 -- flat -- and the file concluded that this register lengthens
in the mean but not in the tail, and that the whole statistic was unusable here.

**That was the filter, not the register.**

| span floor | author's spans kept | his sentence-final 7+ lift | his mean lift |
|---|---|---|---|
| 3 | 75 | **+0.140 +- 0.052** | +1.32 |
| 4 | 68 | +0.150 +- 0.055 | +1.39 |
| 6 | 54 | +0.093 +- 0.057 | +0.98 |
| 8 | 40 | +0.037 +- 0.058 | +0.90 |

The floor is now the smallest that can supply each offset, never a fixed number.

## Result: the statistic works, and the body is low in the tail too

Share of blocks at 7+ runes, by offset from a mark, minus the span interior:

| offset | ten registers | the LP author | the LP body |
|---|---|---|---|
| -3 | -0.004 +- 0.012 | +0.028 (49) | -0.025 +- 0.035 |
| -2 | -0.021 +- 0.013 | -0.026 (57) | -0.045 +- 0.031 |
| **-1** | **+0.152 +- 0.038** | **+0.114 (57)** | **-0.030 +- 0.033** |
| +1 | -0.066 +- 0.045 | +0.009 (57) | +0.025 +- 0.037 |
| +3 | -0.007 +- 0.019 | +0.007 (49) | +0.069 +- 0.041 |

**The author carries the tail signature**, +0.114 against English's +0.152. On the full
span set his sentence-final 7+ lift is +0.140 +- 0.052 against the body's -0.036 +- 0.033:
**z = -2.85.** That is the central anomaly showing in the long tail as well as the mean,
which had not been measured.

## What it still cannot do

| window | ten registers | the LP author | the LP body |
|---|---|---|---|
| +-1 blocks | +11.7 +- 6.8 | +7.1 | -0.6 +- 6.3 |
| +-2 blocks | +6.1 +- 8.2 | +5.1 | -3.2 +- 8.9 |
| +-3 blocks | +4.3 +- 8.4 | +6.2 | +3.6 +- 10.5 |

The window counts are about 1.2 sigma below the author at +-1 and nothing beyond. So the
displaced-stop and transposition readings are still not separated -- but by lack of power,
not because the instrument is invalid. English overstates the effect (+11.7 against the
author's +7.1), so the author is the reference to use.

## The recurring bump is noise

The body's +0.069 at offset +3 in the long-block share, and +0.47 +- 0.27 there in the
mean, looked like a signal. Priced against a scan over all ten offsets with a null that
shuffles blocks inside each span:

    largest |z| over the ten offsets          1.70
    the same on within-span shuffles     2.03 +- 0.67
    P(null >= observed)                       0.684

Noise, and more clearly so than under the broken floor, which gave 2.81 and P = 0.117.

    python is_the_long_block_near_the_mark.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

LONG = 7
OFFSETS = (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)
WINDOWS = (1, 2, 3, 5)
MIN_SPAN = 3  # the author's spans average 7.65 blocks; a higher floor truncates him


def at_offset(spans, o):
    """The block at offset o from each mark; negative counts back, positive forward.

    The span floor is the smallest that can supply the offset, never a fixed number.
    A floor of 8 keeps only 40 of the author's 75 spans -- his longest -- and that
    truncation alone drops his sentence-final 7+ lift from +0.140 to +0.037.
    """
    need = abs(o) + 1
    out = []
    for i in range(len(spans) - 1):
        a, b = spans[i], spans[i + 1]
        if len(a) < max(MIN_SPAN, need) or len(b) < max(MIN_SPAN, need):
            continue
        out.append(a[o] if o < 0 else b[o - 1])
    return np.array(out, float)


def interior_rate(spans, need=MIN_SPAN) -> float:
    a = np.array([x for s in spans if len(s) >= need for x in s[1:-1]], float)
    return float((a >= LONG).mean())


def window_excess(spans, half) -> tuple[float, float, int]:
    """Long blocks within `half` either side of a mark, minus the interior expectation."""
    need = max(MIN_SPAN, half + 1)
    base = interior_rate(spans, need)
    total = seen = 0
    for i in range(len(spans) - 1):
        a, b = spans[i], spans[i + 1]
        if len(a) < need or len(b) < need:
            continue
        cells = a[-half:] + b[:half]
        total += len(cells)
        seen += sum(1 for x in cells if x >= LONG)
    expected = total * base
    return seen - expected, math.sqrt(expected * (1 - base)), total


def main() -> None:
    rng = random.Random(3301)
    registers = [
        register_spans(p, rng) for p in (fetch(n) for n in REGISTERS) if p is not None
    ]
    body, author = body_spans(), author_spans()

    print(f"Share of blocks at {LONG}+ runes, by offset, minus the span interior.\n")
    print(f"{'offset':>8}{'ten registers':>20}{'the author':>14}{'the body':>18}")
    for o in OFFSETS:
        need = max(MIN_SPAN, abs(o) + 1)
        ref = np.array(
            [(at_offset(s, o) >= LONG).mean() - interior_rate(s, need) for s in registers]
        )
        ba, au = at_offset(body, o), at_offset(author, o)
        pb = float((ba >= LONG).mean()) - interior_rate(body, need)
        se = math.sqrt(max((ba >= LONG).mean() * (1 - (ba >= LONG).mean()), 1e-9) / len(ba))
        print(
            f"{o:>8}{f'{ref.mean():+.3f} +- {ref.std(ddof=1):.3f}':>20}"
            f"{f'{float((au >= LONG).mean()) - interior_rate(author, need):+.3f} ({len(au)})':>20}"
            f"{f'{pb:+.3f} +- {se:.3f}':>18}"
        )

    print("\nExtra long blocks inside a window spanning the mark.\n")
    print(
        f"{'window':<14}{'ten registers':>22}{'the author':>14}"
        f"{'the body':>20}{'z vs English':>14}"
    )
    for half in WINDOWS:
        refs = np.array([window_excess(s, half)[0] / len(s) for s in registers])
        eb, se_b, total_b = window_excess(body, half)
        ea, _, _ = window_excess(author, half)
        per_mark_ref = refs.mean() * (len(body) - 1)
        spread = refs.std(ddof=1) * (len(body) - 1)
        z = (eb - per_mark_ref) / math.hypot(se_b, spread)
        print(
            f"{f'+-{half} blocks':<14}{f'{per_mark_ref:+.1f} +- {spread:.1f}':>22}"
            f"{f'{ea:+.1f}':>14}{f'{eb:+.1f} +- {se_b:.1f}':>20}{z:>+14.2f}"
        )
    print(
        "\n  (the register column is scaled to the body's mark count so the three are"
        "\n   on the same footing; 'the author' is his own count, not rescaled)"
    )

    print("\nThe body peaks at offset +3 in both statistics. Is that more than noise?")
    print("Null: shuffle the blocks inside each span, which is what the transposition")
    print("reading says happened, and rescan all ten offsets for the largest |z|.\n")
    base = interior_rate(body)
    def scan(spans):
        best = 0.0
        for o in OFFSETS:
            v = at_offset(spans, o)
            p_hat = float((v >= LONG).mean())
            se = math.sqrt(max(p_hat * (1 - p_hat), 1e-9) / len(v))
            best = max(best, abs(p_hat - base) / se)
        return best

    observed_max = scan(body)
    null = []
    for _ in range(2000):
        shuffled = []
        for s in body:
            s = list(s)
            rng.shuffle(s)
            shuffled.append(s)
        null.append(scan(shuffled))
    null = np.array(null)
    print(f"{'largest |z| over the ten offsets':<40}{observed_max:>10.2f}")
    print(
        f"{'the same on within-span shuffles':<40}"
        f"{f'{null.mean():.2f} +- {null.std(ddof=1):.2f}':>10}"
    )
    print(f"{'P(null >= observed)':<40}{float((null >= observed_max).mean()):>10.3f}")


if __name__ == "__main__":
    main()
