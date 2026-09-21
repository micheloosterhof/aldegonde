---
type: hypothesis
---
# Hypothesis: The Doublet Preventer Moves the Clock, Forward or Back

## Claim

The preventer does two separable things — it re-emits with a neighbouring alphabet, and
it changes how far the clock moves. Michel's negative skip (September 2026) is the
second job run backwards: instead of advancing an extra step, the clock holds, so the
same alphabet is used one more time.

Four combinations, all of which suppress doublets by the same mechanism:

| name | escape emits | clock on a fire | fails when | drift per rune |
|---|---|---|---|---|
| advance (the dodge) | `A(k+1)` | `k + 2` | `offsets[k+1] = 0` | +0.032 |
| re-emit | `A(k+1)` | `k + 1` | `offsets[k+1] = 0` | 0 |
| **hold** (Michel's negative) | `A(k−1)` | `k` | `offsets[k] = 0` | −0.034 |
| back | `A(k−1)` | `k + 1` | `offsets[k] = 0` | 0 |

The failure condition is one zero offset in every case, so the doublet rate is
(1/5) × a diagonal throughout. Only which offset carries the zero changes, and that is
a relabelling.

## Status

**The two drift-free variants are disproved. The two drifting ones survive**, and they
survive precisely because their drift makes them untestable by this route.

## The measurement

On a simulated corpus, all four reach the corpus's doublet rate. The negative skip is
the closest of the four.

| variant | fires | d1w | drift/rune | phase spread of its own doublets |
|---|---|---|---|---|
| advance | 111 | 0.00868 | +0.0323 | [18, 21, 26, 24, 22] smeared |
| re-emit | 94 | 0.00758 | 0.0000 | [0, 0, 0, 0, 94] concentrated |
| hold | 85 | **0.00588** | −0.0341 | [10, 23, 17, 17, 18] smeared |
| back | 96 | 0.00758 | 0.0000 | [96, 0, 0, 0, 0] concentrated |

The corpus reads 0.00628.

## The test the drift-free pair admits

With the clock undisturbed, the phase of position `j` is `(start + j + k×word) mod 5`
for a space eating `k` steps. A one-zero schedule then puts **every** surviving doublet
at one phase. The corpus holds 86 of them, 63 inside words and 23 at the seam, so the
prediction is one class of 86 and four of zero.

The test is decisive where it applies. On ciphertext this model made, with the space
eating two steps, the counts are [0, 0, 0, 0, 94], χ² = 376. Read with the wrong skip
they smear to [15, 20, 19, 20, 20].

Against the LP, at every skip:

| space skip | phase counts | χ² | p |
|---|---|---|---|
| 0 | [18, 21, 16, 11, 20] | 3.7 | 0.455 |
| 1 | [14, 19, 15, 20, 18] | 1.6 | 0.816 |
| 2 | [24, 15, 17, 13, 17] | 4.0 | 0.406 |
| 3 | [15, 14, 25, 16, 16] | 4.6 | 0.333 |
| 4 | [18, 20, 11, 19, 18] | 3.0 | 0.566 |

Flat everywhere. A flat spread puts 17.2 in each class, and that is what the corpus
shows.

**This covers both drift-free variants at once.** The negative escape only changes which
offset must be zero, which rotates the class labels, and a concentration test ignores
rotation.

**And it covers positive and negative SPACE skips at once**, because the phase is taken
mod 5: `k = 4` is `k = −1`, `k = 3` is `k = −2`, and so on.

## What this rules out, and what it does not

**Ruled out:** any cipher whose letter clock is period 5, advances predictably, and lets
doublets survive at a single clock phase. That is the whole drift-free family, at any
space convention.

**Not ruled out:** the drifting variants — the forward dodge and Michel's negative hold.
Their own fires move the clock away from the position count at about 3.4% per rune, a
full period every 111 to 161 runes of the 12,956, so the phase computed from position is
unrelated to the real one and the test cannot be run. They are untested rather than
supported.

**Not ruled out either:** suppression that does not depend on clock phase at all — a
tuned diagonal, as in `length-clocked-walk.md`. That model predicts no concentration, so
the flat result is consistent with it.

## One robustness note

`separator-loss-is-selective.md` records that roughly 300 word separators may be missing
from the transcription. Word indices would then be wrong, which corrupts the phase for
every `k ≠ 0`. The `k = 0` row does not use word indices at all — the phase is the rune
index — so that row is immune, and it is flat (χ² 3.7). The disproof of the drift-free
family with no space skip therefore stands regardless of separator loss; the `k ≠ 0`
rows depend on the transcription being complete.

## What to do next

1. **A bounded-drift preventer.** The forward and backward drifts are +0.032 and −0.034,
   nearly equal and opposite. A rule that alternates direction strictly — first fire
   forward, second back — keeps total drift bounded by one step and leaves the phase
   readable, which would bring it back inside this test. Nobody has tried it.
2. **The drifting pair stays only testable by fitting**, not by a phase count, which
   leaves the decodability work in `quagmire_dodge_decode.py` as their main handle.

## Scripts

- `experiments/doublet_phase_test.py` — the four variants, their drift, the phase test
  on simulated output and on the LP.

## Related

- `space-eats-clock-steps.md` — where the drift obstacle was identified; this quantifies
  it per variant and finds the two variants it does not apply to.
- `doublet-dodge-walk.md` — the forward-drifting original.
- `quagmire-odometer.md` — the model these preventers sit inside.
- `separator-loss-is-selective.md` — why only the `k = 0` row is transcription-proof.

## Verdict

Michel's negative skip works as a doublet mechanism and lands the rate closer than the
forward version, 0.00588 against the corpus's 0.00628. It is not distinguishable from
the forward dodge by any phase measurement, because both drift.

What the measurement does settle is the drift-free half of the family. If the preventer
leaves the clock alone, every surviving doublet must share a clock phase, and the
corpus's 86 doublets are flat at every space convention with ample power to see
otherwise. That half is out.
