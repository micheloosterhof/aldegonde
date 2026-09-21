---
type: observation
---
# The Coincidence Profile Filters a Pool of g and Cannot Confirm a Single One

## Status

**Status**: confirmed negative, with a planted control that works and a body run that
does not. It stops an attack rather than opening one.

## The attack that suggests itself

`d-profile-pins-g-to-five-cycles.md` scores candidate `g` by how well its predicted lag-k
coincidences match the body's, using the identity `c_i = c_(i+k)` iff
`p_i = g^(k mod 5)(p_(i+k))` in which the base cancels. It ranks the true `g` in the top
0.1% of a random pool. The obvious next step is to stop sampling and search: conjugating
by a transposition preserves cycle type, giving a 406-move neighbourhood over the
conjugacy class.

## It overfits, and the control shows exactly how

`experiments/g_cannot_be_annealed.py`, planted `g`, prose enciphered through the walk,
17 usable cells split 8 for fitting and 9 for holding out.

| | fit χ²/cell | **held-out χ²/cell** |
|---|---|---|
| random g (400 draws) | 50.84 ± 35.28 | 53.21 ± 49.64 |
| best of those 400 | 6.75 | 6.21 |
| **the true g** | **1.35** | **3.11** |
| 12 hill-climb winners | **0.15 ± 0.09** | **28.06 ± 19.51** |
| best held-out of those | 0.11 | 8.14 |

**The winners beat the truth in sample by nine times and lose out of sample by nine
times**, while sharing **0 to 3 of its 29 points**. Seventeen numbers cannot pin a
permutation drawn from a class of about 10²⁵.

But cross-validation catches it perfectly: the true `g` scores 3.11 per held-out cell
against 53.21 for a random one — a factor of seventeen — and every hill-climb winner is
worse than the truth out of sample. **In the control, held-out score is a working
verifier.**

## On the body it is not a verifier at all

The same procedure, 12 cells split 8 and 4.

| | fit χ²/cell | held-out χ²/cell |
|---|---|---|
| random g (400 draws) | 7.84 ± 6.49 | **3.92 ± 2.73** |
| best of those 400 | 0.54 | **0.18** |
| 12 hill-climb winners | 0.09 ± 0.12 | **4.19 ± 3.23** |
| best held-out of those | 0.02 | **0.53** |

**Fitted candidates do slightly worse out of sample than random ones** — 4.19 against
3.92 — and the best fitted candidate's 0.53 is beaten by a random draw's 0.18. Fitting
buys nothing at all.

The reason is arithmetic. The body's measurement errors are about five times the
control's, because the control encipherment is clean prose measured at ±0.0008 while the
body's cells carry ±0.004 to ±0.007. Only four cells survive the split. There is not
enough information to both fit `g` and check it.

## What this settles

- **The profile filters a pool and cannot confirm a candidate.** The 100× reduction in
  `d-profile-pins-g-to-five-cycles.md` is real and is the most the channel gives. A
  single proposed `g` cannot be validated against it on the body.
- **Any candidate `g` must come from somewhere else** — a crib, a structural argument, a
  key search that decrypts — and the profile can only say whether it is in the plausible
  100th.
- **Hill-climbing against these numbers is wasted effort**, and this is the measurement
  that says so rather than an intuition.

It also localises where the earlier filter's power lives: in the *aggregate* over a pool,
not in any individual score. That is consistent with the binned filter being a better
ranker and a worse reader (`d-profile-pins-g-to-five-cycles.md`, last section).

## Falsification

- If the held-out cell count can be raised — a different split, more lags, a longer
  corpus — the body's verifier might start working. With five lags and four position bins
  there are at most 20 cells and 12 have the pairs; no split gives the control's nine
  held-out cells at the control's precision.
- If the body's plaintext register were known exactly rather than through prose, the
  model error would fall and every cell would sharpen. That is the one route that would
  change this verdict, and it needs solved body pages.
- The control uses two enciphered prose corpora. Shrinking it until its errors match the
  body's should reproduce the body's failure, which is the direct check that error size
  and not something else is the cause.

## Scripts

- `experiments/g_cannot_be_annealed.py`

## Related

- `d-profile-pins-g-to-five-cycles.md` — the filter, and what it can still do.
- `cross-validate-a-search-winner` — the rule this applies, here with the unusual outcome
  that cross-validation itself has too little data to run.
