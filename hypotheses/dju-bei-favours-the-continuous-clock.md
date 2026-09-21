---
type: observation
---
# Observation: The Return's Rune Gap Divides by Five, Which Only One Clock Requires

## A question priced as unreachable, with evidence sitting in plain view

`clock-convention-is-out-of-reach.md` prices both channels that bear on whether the letter
phase resets at each block or runs continuously. The sharper is **0.54 σ** and would need
**14× the corpus** to settle. The question is worth a factor of five on the σ order bound
(1,536 against 307), so it is not a detail.

The DJU-BEI return speaks to it, and nobody had read it that way.

## The argument

Under a **continuous** clock the alphabet at a block start is `base_w ∘ g^(A_w mod 5)`,
where A_w is the cumulative rune count. Two occurrences give identical ciphertext only if
the bases agree **and the phases agree**, so the rune gap must be divisible by 5.

Under a **reset** clock every block starts at phase 0, so only the bases need agree and the
gap is unconstrained.

The rune gap is **6,395 = 5 × 1,279**.

| | P(gap divisible by 5) |
|---|---|
| continuous clock, genuine return | **1** |
| reset clock, genuine return | 1/5 |

> **Likelihood ratio 5 : 1 in favour of the continuous clock.**

## Why this is worth more than its size

Five to one is not decisive. But it is the *only* evidence on this question that exists,
against a coincidence channel measured at 0.54 σ, and it is free — the observation has
been in the files since the repeat was found, under the heading of period divisibility
rather than clock convention.

It is also **tokenization-proof**. The word gap varies from 1,378 to 1,711 across the six
audited conventions, which is why `sigma-is-even.md` has to check parity under each. The
**rune gap is invariant at 6,395 under all of them**, because apostrophes, quotes and
digits are not runes. So this reading depends on nothing that is in dispute.

## Consequence, if taken

Under the continuous clock, `key-local-channel-is-empty.md`'s depth argument gives
**order(σ) ≥ 307**, not 1,536 — the weaker of the two bounds. So this evidence, such as it
is, points at the *less* constraining reading of σ. That is worth stating plainly: it is
not a convenient result, and the instruction in that file to quote both bounds stands.

## Scope

- **Conditional on the return being genuine**, as everything downstream of this repeat is.
  At 1 in 2,700 (`dju-bei-is-more-surprising-than-recorded.md`) that is likely, not
  established.
- Assumes the phase advances one step per rune, which is the shared premise of every model
  here.
- 5 : 1 is a likelihood ratio, not a posterior. Anyone holding a strong prior for the
  reset convention should still hold it afterwards, just less strongly.

## Status

**Status**: confirmed (arithmetic on an invariant gap), conditional on the return.
`experiments/dju_bei_clock_evidence.py`.

## Related

- `clock-convention-is-out-of-reach.md` — the channels this bypasses.
- `key-local-channel-is-empty.md` — the two σ bounds at stake.
- `sigma-is-even.md`, `dju-bei-needs-a-product-step.md` — the other deductions from this
  repeat.
