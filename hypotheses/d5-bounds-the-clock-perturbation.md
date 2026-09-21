---
type: observation
---
# The d5 Shortfall Bounds the Clock Perturbation at 9.6%, With an Interval Too Wide to Choose

## Status

**Status**: confirmed as a bound, negative as a discriminator. Recorded mainly so the
channel is not re-opened: it is measured out.

## The idea

`g` has order 5, so within a block two runes five apart are enciphered by the same
alphabet and coincide at the **plaintext** rate. That is what makes d5 the one key-free
window onto the plaintext (`period5-is-confirmed`), and it makes any shortfall a
measurement of something.

A rule that advances the clock an extra step on a would-be repeat breaks the alignment. A
lag-5 pair survives only if no perturbation falls in the five positions between, so

    d5_body = A · d5_plain + (1 − A)/29,    A = (1 − q)^5

with `q` the per-position perturbation rate. Three measured numbers give `q`, with no key
and no model fit.

**The clock-dodge family predicts `q` = the would-be doublet rate = 1/29 = 0.034**, since
that is when it fires. A clean walk predicts `q` = 0.

## The within-word profile, three corpora

Only lag 5 should leak. Chance is 0.0345.

| lag | LP plaintext (2,882 runes) | prose | the body |
|---|---|---|---|
| 1 | 0.0236 ± 0.0033 | 0.0261 ± 0.0003 | **0.0063** ± 0.0008 |
| 2 | 0.0389 ± 0.0051 | 0.0368 ± 0.0004 | 0.0347 ± 0.0022 |
| 3 | 0.0507 ± 0.0071 | 0.0582 ± 0.0006 | 0.0370 ± 0.0027 |
| 4 | 0.0583 ± 0.0096 | 0.0539 ± 0.0007 | 0.0410 ± 0.0035 |
| **5** | **0.0733 ± 0.0133** | **0.0589 ± 0.0008** | **0.0492 ± 0.0048** |
| 6 | 0.0594 ± 0.0160 | 0.0684 ± 0.0011 | 0.0245 ± 0.0043 |
| 7 | 0.0924 ± 0.0266 | 0.0699 ± 0.0015 | 0.0421 ± 0.0075 |

The body sits at chance everywhere except lag 1, which the preventer suppresses, and lag
5, which leaks. That is the walk's signature and it holds across the whole profile.

The two plaintext estimates agree — 0.0733 ± 0.0133 against 0.0589 ± 0.0008, a difference
of +0.0144 ± 0.0134 — so prose is used below for its precision. That agreement is itself
worth having: it is the register check `battery-register-is-unmatched` calls for, passed
at lag 5 specifically.

## The bound

| quantity | value | |
|---|---|---|
| plaintext d5 (prose) | 0.0589 ± 0.0008 | |
| body d5 | 0.0492 ± 0.0048 | 2,073 pairs |
| **shortfall** | **−0.0097 ± 0.0048** | **z = −2.00** |
| fraction still aligned, A | 0.604 ± 0.196 | 95% [0.220, 0.987] |
| **perturbation rate q** | **0.096** | **95% [0.003, 0.262]** |

**The dodge's 0.034 and a clean walk's 0 both sit inside the interval.** The point
estimate is about three times the dodge's rate and the shortfall is two sigma, so the
direction favours a perturbed clock and the precision does not settle it.

## Why the channel is exhausted

- The plaintext side is already at ±0.0008 from prose. Nothing to gain.
- The body side has 2,073 lag-5 pairs, fixed by how many blocks run to six runes or
  more. It cannot be enlarged.
- Lag 10 leaks too, since `g^10` is also the identity, and the ratio of the lag-10 excess
  to the lag-5 excess would measure A directly with no plaintext register at all. Blocks
  of eleven runes or more are 1.5% of the body and supply too few pairs.

So this is the best the d5 channel can do. Anyone returning to it should expect z = −2
and stop.

## What it is worth

- A number for future models: any preventer proposed for the body should be checked
  against **q ∈ [0.003, 0.262]**, which is loose but not vacuous — a rule perturbing the
  clock at 40% of positions is excluded.
- Confirmation that the profile's shape is the walk's: chance at lags 2, 3, 4, 6, 7, a
  leak at 5, suppression at 1.

## Falsification

- If `g` does not have order 5 the whole construction fails; `period5-is-confirmed`
  establishes it independently.
- If the body's plaintext register has a materially different d5 from both prose and the
  front matter, the shortfall moves. The two available estimates agree at z = 1.1.
- A preventer that perturbs the clock by 5 steps rather than 1 would leave A = 1 and is
  untouched. So would one that substitutes without touching the clock — but
  `survivors-use-every-rune.md` closes the single-τ version of that.

## Scripts

- `experiments/d5_attenuation_bound.py`

## Related

- `period5-is-confirmed`, `d5-partial-alphabet-leak.md` — the channel.
- `dodge_d5_attenuation.py` — the earlier treatment, which this supersedes by measuring
  the plaintext side properly.
- `register_is_bigger.py` — why the plaintext d5 estimate moved from 0.0575 to 0.0733.
