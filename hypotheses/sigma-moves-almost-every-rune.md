---
type: observation
---
# Observation: σ Moves At Least 24 of the 29 Runes

## The same channel, one level up

`g-has-more-than-one-cycle.md` counts the letter step's fixed points from what they leave
*inside* a block: a rune g fixes enciphers to the same value at every position, so it
floors the within-block coincidence at distances that are not multiples of five.

σ has the same exposure between blocks. If `base_{w+1} = base_w ∘ σ`, then for a plaintext
rune p with `σ(p) = p`, **block w+1 enciphers p exactly as block w does**. So runes at the
same letter phase in *adjacent* blocks coincide above chance in proportion to σ's
fixed-point count, and at chance if σ moves everything.

## Result

The body, coincidence at matching letter phase by block gap:

| gap | phase resets per block | phase continuous |
|---|---|---|
| 1 | **1.0685** | 0.9914 |
| 2 | 1.0256 | 1.0282 |
| 3 | 0.9835 | 0.9968 |
| 5 | 1.0174 | 0.9793 |
| 10 | 0.9989 | 0.9303 |

Adjacent blocks under the reset convention read **1.0685 on 13,001 pairs, z = +1.48** —
not significant on its own. Calibrating against planted walks whose σ fixes exactly f
runes and deranges the rest:

| σ fixed points | median | 10th | 90th | draws below the body |
|---|---|---|---|---|
| 0 | 1.0358 | 0.75 | 1.13 | 62% |
| 2 | 1.0106 | 0.88 | 1.27 | 75% |
| 5 | 1.2633 | 0.82 | 1.40 | 25% |
| **10** | 1.5013 | **1.11** | 1.78 | **0%** |
| **15** | 1.5634 | **1.23** | 2.01 | **0%** |
| **24** | 2.1842 | **1.86** | 2.36 | **0%** |

The medians rise monotonically with the fixed-point count, so the channel is calibrated.
From ten fixed points upward the body sits **below the 10th percentile**, and at 24 it is
nowhere near.

> **σ moves at least 24 of the 29 runes.** Up to about five fixed points is consistent,
> which is what a generic permutation gives.

## What it rules out

Any σ built to touch only part of the alphabet: a step that rotates five runes and leaves
the rest, a disk acting on a sub-alphabet, a keyed swap of a handful of positions. Those
would leave 20 or more runes enciphering identically in consecutive blocks, and the body
shows nothing of the sort.

With `key-local-channel-is-empty.md`'s order(σ) ≥ 307 and
`base-family-is-the-symmetric-group.md`'s classification, the picture on the key side is
consistent and unhelpful in the same direction: **σ is a high-order permutation that moves
almost everything, drawn from a family with no algebraic structure.**

## Scope

- **The two readings do not identify the clock, and an earlier draft of this file said
  they did.** Correction below.
- Assumes `base_{w+1} = base_w ∘ σ`. The other composition order gives the same test with
  σ conjugated, and the same fixed-point count.
- Ten planted draws per cell. The exclusions at f ≥ 10 are p ≤ 0.10 by count, but the
  body sits below every draw and well below the 10th percentile.

## Correction: this channel says nothing about the clock convention

The first version of this file noted that the effect appears under the per-block phase
reset and not under a continuous clock, and called it a mild preference for the reset.
**That was wrong**, and the right test is to plant each clock and read it both ways
against its own shuffled null:

| planted clock | z as reset | z as continuous |
|---|---|---|
| reset | +2.86 | −1.12 |
| **continuous** | **+2.54** | +0.51 |
| **body** | **+1.54** | **−0.33** |

A planted **continuous** clock reads +2.54 under the **reset** reading — almost as high as
a planted reset clock. The reset reading fires whatever the truth, because a σ fixed point
makes `base_{w+1}(x) = base_w(x)` and some share of the pairs line up in phase either way.
So the body's pattern is what *both* clocks produce, and it distinguishes neither.

The clock convention that `key-local-channel-is-empty.md` leaves open — worth a factor of
five on the σ order bound — stays open. What this channel measures is f_σ, and only that.

Incidentally the body's +1.54 sits *below* both plants at f_σ = 5, which is independent
support for the fixed-point bound above.

## Status

**Status**: confirmed (measurement with planted controls at six fixed-point counts) for
the fixed-point bound. The clock-convention remark in the first draft is **retracted**;
planted controls show both clocks produce the body's pattern.
`experiments/sigma_fixed_points.py`.

## Related

- `g-has-more-than-one-cycle.md` — the same channel for the letter step.
- `key-local-channel-is-empty.md` — the order bound this complements.
- `base-family-is-the-symmetric-group.md` — the structural classification it fits.
