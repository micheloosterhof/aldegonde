---
type: observation
---
# Observation: The d5 Deficit and the Doublet Suppression Are Consistent With One Mechanism

## Two anomalies, one arithmetic link

Under a letter step of order 5, positions five apart inside a block share an alphabet
**exactly**, so `c[j] == c[j+5]` should reproduce the plaintext's own d5 coincidence in
full. It does not. The body reads **1.4269 ± 0.1378**, against a plaintext reference near
1.6 — the deficit that `d5-partial-alphabet-leak.md` records as φ5 and leaves undecided.

The deficit has a mechanical reading that nobody has cashed out. If the clock is perturbed
at rate q — a dodge, a preventer, any rule that skips or repeats a step — a d5 pair
survives intact only when no perturbation falls between its members:

    φ5 = (observed d5 excess) / (plaintext d5 excess) = (1 − q)⁵

so the deficit *measures* q. And the doublet suppression measures q independently:
`quagmire-dodge.md` has the dodge failing exactly when the schedule offset is zero, one
time in five, so the emitted doublet rate is a fifth of the would-be rate and the dodge
fires on the other four fifths.

**If one mechanism causes both anomalies, the two q's must agree.**

## The numbers

| source | q |
|---|---|
| the doublet suppression, via the dodge's 1/5 | **0.0251** |
| the d5 deficit, LP plaintext reference | 0.085, interval 0 – 0.283 |
| the d5 deficit, prose reference | 0.064, interval 0.010 – 0.134 |

What each q predicts for the body's d5, against the observed 1.4269 ± 0.1378:

| | vs LP reference | vs prose reference |
|---|---|---|
| **no perturbation** (q = 0) | 1.6667, **z = −1.74** | 1.5950, **z = −1.22** |
| **the dodge's rate** (q = 0.0251) | 1.5870, z = −1.16 | 1.5239, z = −0.70 |
| the d5 point estimate (q = 0.085) | 1.4269, z = 0.00 | 1.3810, z = +0.33 |

**The dodge's rate fits better than no perturbation, and nothing is excluded.** The
deficit leans toward *some* clock perturbation at 1.2 to 1.7 σ, and the rate the doublet
suppression independently implies sits comfortably inside the d5 interval under both
references.

## What this is and is not worth

It is **not** a confirmation. The point estimates differ by a factor of 3.4 (0.085 against
0.0251), and only the wide intervals reconcile them.

It **is** a consistency check that the dodge passes and that it could have failed. Two
anomalies measured on different statistics — a coincidence deficit at distance 5 and a
suppression at distance 1 — imply overlapping perturbation rates. A mechanism that
produced one and not the other would show up here as an incompatibility, and does not.

That modestly raises the prior on the preventer family, which is what the parked
218-core-hour sweep targets. It does not justify starting it.

## Why it cannot be sharpened

φ5 is a ratio of two noisy excesses. The body's d5 rests on 2,073 pairs and the LP
plaintext reference on **261**, giving φ5 a 30–55% relative error — and q = 1 − φ5^(1/5)
amplifies that fivefold. Switching to the prose reference halves the error, at the cost of
the register caveat, and still leaves an interval spanning a factor of thirteen.

Like `clock-convention-is-out-of-reach.md`, the limit is the corpus.

## Status

**Status**: confirmed (measurement and arithmetic) that the two rates are compatible;
**not** a confirmation of either mechanism. `experiments/d5_deficit_as_perturbation.py`.

## Related

- `d5-partial-alphabet-leak.md` — where φ5 is recorded as undecided.
- `quagmire-dodge.md` — the mechanism whose rate this matches.
- `preventer-blinds-absolute-tests.md` — what a perturbation at this rate costs every
  alignment test.
