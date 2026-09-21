---
type: observation
---
# Observation: The Clock Convention Needs Fourteen Times This Corpus

## What hangs on it

`key-local-channel-is-empty.md` derives two σ order bounds from the same depth data:

| letter phase | order(σ) ≥ | fraction of S₂₉ | bits |
|---|---|---|---|
| resets at each block | 1,536 | 0.0041 | 7.9 |
| runs continuously | 307 | 0.115 | 3.1 |

A factor of five on the bound and five bits on the key, turning on a convention nobody has
measured. Two channels have now been tried and priced.

## Channel one fails: the reading fires either way

`sigma-moves-almost-every-rune.md` reads adjacent blocks under both phase conventions. A
planted **continuous** clock scores **+2.54** under the **reset** reading against a planted
reset clock's **+2.86** — the reading fires whatever the truth, because a σ fixed point
makes `base_{w+1}(x) = base_w(x)` and some share of pairs align in phase regardless.

## Channel two discriminates, and is far too small

Under a continuous clock, comparing runes at matching *position* mod 5 in adjacent blocks
is the right comparison **exactly when the first block's length is divisible by 5** — only
then do the two blocks' start phases agree. Under a reset clock it is always right. So the
signal should concentrate in the `len % 5 == 0` class under a continuous clock and be flat
under a reset one.

It does. Planted at σ fixing 5 runes:

| | contrast (len%5=0 class minus the other four) |
|---|---|
| planted **reset** clock | +0.0641 |
| planted **continuous** clock | +0.1314 |
| separation | **0.067** |

And the body's own noise on that statistic, from a shuffled null:

| | |
|---|---|
| body contrast | −0.1360 |
| shuffled null | −0.054 ± **0.125** |
| z | −0.66 |

**separation / noise = 0.54 σ.** Reaching 2 σ needs **14× the corpus — about 177,000
runes**, against the 12,956 that exist.

## Consequence

The clock convention is not open for want of a good idea. The sharpest discriminator the
model admits is about a quarter of the size it would have to be, and the shortfall is in
the corpus, not the method. **The σ order bound must keep both readings — 307 and 1,536 —
rather than choosing one**, and the same goes for anything else that turns on the phase.

This is worth recording as a closure of a different kind: a question marked open invites
repeated attempts, and this one is now priced.

## Scope

- Prices the two channels the model exposes. A channel outside the g/σ frame is not
  covered, though the argument in `sigma-moves-almost-every-rune.md` — that within-block
  statistics cannot see the block's start phase at all, because they depend only on
  relative distance — suggests the exposure is genuinely limited to cross-block pairs.
- Priced at σ fixing 5 runes, the loosest value the fixed-point bound allows. Fewer fixed
  points make both channels weaker still.

## Status

**Status**: confirmed (power calculation with planted controls on both clocks).
`experiments/clock_convention_power.py`.

## Related

- `key-local-channel-is-empty.md` — the two bounds this leaves standing side by side.
- `sigma-moves-almost-every-rune.md` — channel one, and its retraction.

## One piece of evidence does exist, from outside the coincidence channel (September 2026)

Both channels priced above are coincidence statistics, and both are too small. A third
source is not: the DJU-BEI return.

Under a continuous clock a state return requires the phases to agree as well as the bases,
so the RUNE gap must divide by 5; under a reset clock every block starts at phase 0 and
the gap is unconstrained. The rune gap is 6,395 = 5 x 1,279 -- certain under one
hypothesis, one chance in five under the other, a **likelihood ratio of 5 : 1 for the
continuous clock** (`dju-bei-favours-the-continuous-clock.md`).

It is conditional on the return being genuine, and it is tokenization-proof: the rune gap
is invariant at 6,395 under every convention audited, unlike the word gap.

Five to one does not settle a question this file prices at 0.54 sigma, but it is the only
evidence there is, and it points at the CONTINUOUS reading -- which gives the weaker sigma
bound, 307 rather than 1,536. The instruction to quote both stands.

