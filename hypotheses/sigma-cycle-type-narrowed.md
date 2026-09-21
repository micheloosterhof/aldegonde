---
type: observation
---
# Observation: Parity and Order Together Leave One Cycle Type for σ, Under One Clock Reading

## Two results compose

`sigma-is-even.md` derives **sign(σ) = +1** from the DJU-BEI return. `key-local-channel-is-empty.md`
bounds **ord(σ)** from the depth data at **307** under a continuous letter clock or
**1,536** under a per-block reset. Intersecting them is a finite computation over the
4,565 partitions of 29, weighted by conjugacy-class size so the answer is in permutations
rather than cycle types.

| | cycle types | of which even | fraction of S₂₉ | bits |
|---|---|---|---|---|
| ord ≥ 307, any parity | 329 | — | 0.1157 | 3.1 |
| **ord ≥ 307, even** | — | **151** | **0.0523** | **4.3** |
| ord ≥ 1,536, any parity | 9 | — | 0.00415 | 7.9 |
| **ord ≥ 1,536, even** | — | **1** | **0.00032** | **11.6** |

**Under the per-block reset the intersection is a single cycle type: (11, 7, 5, 4, 2),
order 1,540.** σ's cycle structure would be completely determined — 11.6 bits, from two
measurements neither of which touches σ directly.

The reason is clean: of the nine cycle types with order ≥ 1,536, eight contain an
even-length cycle (8, 6, 4 or 2) an odd number of times and are therefore odd
permutations. Only (11, 7, 5, 4, 2), with its 4 and its 2, has two even-length cycles and
comes out even.

## The evidence points at the weaker branch

`dju-bei-favours-the-continuous-clock.md` gives **5 : 1 for the continuous clock**, and
that is the branch where 151 types survive rather than one — 4.3 bits rather than 11.6.

So the spectacular version of this result sits on the reading the evidence disfavours.
Both are quoted here and neither is chosen; `clock-convention-is-out-of-reach.md` shows
the corpus cannot settle it, and a result that depends on which way it falls should say so
rather than take the flattering branch.

## Scope

- Inherits everything `sigma-is-even.md` conditions on: the DJU-BEI repeat being a genuine
  state return, the step having the walk's `g^a ∘ σ` form, and an odd word gap.
- The order bounds inherit the depth calibration in `key-local-channel-is-empty.md`.
- Weighting by class size is what makes the bits meaningful — 151 of 4,565 cycle types
  would suggest 4.9 bits, but the surviving classes are large and the honest figure is 4.3.

## Status

**Status**: confirmed (finite computation) given its inputs.
`experiments/sigma_cycle_types.py`.

## Related

- `sigma-is-even.md` — the parity.
- `key-local-channel-is-empty.md` — the two order bounds.
- `dju-bei-favours-the-continuous-clock.md` — why the weaker branch is the likelier one.
