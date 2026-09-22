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

## Result: the statistic does not work in this book, and the author shows why

Share of blocks at 7+ runes, by offset from a mark, minus the span interior:

| offset | ten registers | **the LP author** | the LP body |
|---|---|---|---|
| -5 | -0.003 +- 0.009 | **+0.054** | -0.020 +- 0.044 |
| -3 | +0.001 +- 0.015 | **+0.054** | -0.047 +- 0.041 |
| -2 | -0.020 +- 0.010 | **+0.054** | -0.020 +- 0.044 |
| **-1** | **+0.160 +- 0.034** | **+0.054** | -0.087 +- 0.036 |
| +1 | -0.071 +- 0.034 | -0.029 | +0.034 +- 0.049 |
| +3 | -0.005 +- 0.017 | -0.113 | +0.156 +- 0.055 |

**The author's sentence-final column is +0.054, exactly what he reads at offsets -5, -3
and -2.** His profile is flat in the long-block share. Yet his sentence-final *mean*
lengthening is +1.32 +- 0.26, matching English's +1.19.

So in this book's register the lengthening lives in the middle of the length distribution,
not in the long tail. A count of 7+ blocks measures the tail, and the matched reference
predicts **no excess at all**.

| window | ten registers | the LP author | the LP body |
|---|---|---|---|
| +-1 blocks | +8.7 +- 3.0 | +0.6 | -3.9 +- 4.8 |
| +-2 blocks | +5.2 +- 4.2 | -0.8 | -2.9 +- 6.8 |
| +-3 blocks | +4.7 +- 5.7 | -2.2 | +5.2 +- 8.4 |

The English column predicts +8.7 extra long blocks near a mark and the body shows -3.9,
z = -2.23. **That number should not be quoted.** English is the wrong register for a tail
statistic here: the author predicts +0.6 and the body reads -3.9 +- 4.8, which is nothing.

**So this test cannot separate a displaced stop from a transposition**, and the failure is
in the instrument rather than in the data. It joins the window mean and the window maximum
(`a_shifted_stop_or_a_switched_key.py`) as the third statistic to die on this question.

## The one recurring bump is noise

The body reads +0.156 +- 0.055 at offset +3 in the long-block share, and +0.47 +- 0.27
there in the mean (`the_long_block_is_nowhere.py` records +0.44 as its largest value
anywhere). Two statistics peaking at the same offset looks like something.

Priced against a scan over all ten offsets, with a null that shuffles the blocks inside
each span -- which is what the transposition reading says happened:

    largest |z| over the ten offsets          2.81
    the same on within-span shuffles     1.96 +- 0.67
    P(null >= observed)                       0.117

**Not significant.** The offset +3 bump is what a ten-offset scan produces by chance, and
should be dropped rather than carried forward.

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
MIN_SPAN = 8


def at_offset(spans, o):
    """The block at offset o from each mark; negative counts back, positive forward."""
    out = []
    for i in range(len(spans) - 1):
        a, b = spans[i], spans[i + 1]
        if len(a) < MIN_SPAN or len(b) < MIN_SPAN:
            continue
        out.append(a[o] if o < 0 else b[o - 1])
    return np.array(out, float)


def interior_rate(spans) -> float:
    a = np.array([x for s in spans if len(s) >= MIN_SPAN for x in s[1:-1]], float)
    return float((a >= LONG).mean())


def window_excess(spans, half) -> tuple[float, float, int]:
    """Long blocks within `half` either side of a mark, minus the interior expectation."""
    base = interior_rate(spans)
    total = seen = 0
    for i in range(len(spans) - 1):
        a, b = spans[i], spans[i + 1]
        if len(a) < MIN_SPAN or len(b) < MIN_SPAN:
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
        ref = np.array(
            [(at_offset(s, o) >= LONG).mean() - interior_rate(s) for s in registers]
        )
        ba, au = at_offset(body, o), at_offset(author, o)
        pb = float((ba >= LONG).mean()) - interior_rate(body)
        se = math.sqrt(max((ba >= LONG).mean() * (1 - (ba >= LONG).mean()), 1e-9) / len(ba))
        print(
            f"{o:>8}{f'{ref.mean():+.3f} +- {ref.std(ddof=1):.3f}':>20}"
            f"{f'{float((au >= LONG).mean()) - interior_rate(author):+.3f}':>14}"
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
