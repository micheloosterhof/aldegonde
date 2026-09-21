---
type: observation
---
# Observation: No Bare-σ Step Can Produce the DJU-BEI Return

## Two measurements, one deduction

`dju-bei-is-more-surprising-than-recorded.md` puts the chance of the DJU-BEI repeat at
**1 in 2,700** under the framing a state return predicts — surprising enough to be worth
asking what a genuine return would require of the key.

A state return needs the base to come back: `base_{w+1449} = base_w`. If the step between
blocks were a bare permutation σ, that means σ¹⁴⁴⁹ = id, so

> **ord(σ) divides 1,449 = 3² · 7 · 23**

leaving twelve candidates: 1, 3, 7, 9, 21, 23, 63, 69, 161, 207, 483, 1449.

A bare-σ step visits exactly ord(σ) distinct bases. `base_pool_floor.py` measures how
small a pool the corpus allows: a pool of N predicts **10,853/N** excess joint-agreement
pairs among two-rune blocks, against an observed 95% upper bound of **+4.0**. So any pool
below about **2,713** is excluded.

| ord(σ) | predicted excess | |
|---|---|---|
| 161 | 67.4 | excluded |
| 207 | 52.4 | excluded |
| 483 | 22.5 | excluded |
| **1,449** | **7.5** | **excluded** |

**Every divisor is excluded**, the largest by a factor of nearly two.

## What follows

**No bare-σ step produces the return.** If the repeat is genuine, the base step must be a
product that returns to the identity without any single factor having small order — the
walk's own `g^a ∘ σ`, whose exponents depend on the **block lengths** between the two
occurrences.

That is worth stating plainly because it ties the return to *visible data*. Under a bare
σ the return is a property of the key alone; under a product step it is a joint property
of the key and the 1,449 block lengths that separate the two occurrences, which anyone can
read off the page.

**The argument needs no σ order floor.** `key-local-channel-is-empty.md` bounds ord(σ) at
307 or 1,536 depending on a clock convention that `clock-convention-is-out-of-reach.md`
shows cannot be settled here. None of that is used: the largest divisor of 1,449 is itself
well below the base-reuse ceiling.

## Scope

- Assumes the repeat *is* a state return. At 1 in 2,700 that is likely but not
  established, and the alternative — coincidence — leaves nothing to explain.
- Assumes the return is a base return. A cipher whose state includes more than the base
  could return in that larger state without the base recurring, though every candidate
  here has the base as its whole state.
- The 1,449 figure is the repo-default tokenization. `rotor-machine-compact-state.md`
  audits the alternatives; the rune gap 6,395 is invariant under all of them, and the word
  gap varies from 1,378 to 1,711. Every one of those is below 2,713, so the conclusion
  survives the convention question.

## Status

**Status**: confirmed (deduction from two measurements).
`experiments/dju_bei_step_form.py`.

## Related

- `dju-bei-is-more-surprising-than-recorded.md` — why the return is worth taking seriously.
- `two-rune-depth-no-base-reuse.md` — the base-pool floor this uses.
- `repeated-phrase-dju-bei.md`, `rotor-machine-compact-state.md` — the repeat and the
  tokenization audit.
