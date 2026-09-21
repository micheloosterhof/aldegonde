---
type: observation
---
# Observation: If the DJU-BEI Return Is Genuine, σ Is Even and the Base Family Is A₂₉

## One bit, and it is the bit that names the group

`dju-bei-needs-a-product-step.md` shows no bare σ can produce the return: the base step
must be a product `g^a ∘ σ` whose exponents depend on the block lengths between the two
occurrences. That looks like it makes the return depend on 1,449 unknowns.

It does not, because **parity is a homomorphism and the exponents drop out**:

    sign(g^a ∘ σ) = sign(g)^a · sign(σ) = sign(σ)

since g has order 5, so every one of its cycles is a 5-cycle — an even permutation — and
sign(g) = +1 whatever its cycle count. Over the gap,

    sign(product) = sign(σ)^gap

and a state return needs the product to be the identity, whose sign is +1. **With an odd
gap that forces sign(σ) = +1.**

The repo-default word gap is **1,449**, which is odd.

> **σ is even. g is even. The group they generate lies in A₂₉.**

## It settles a question left open

`base-family-is-the-symmetric-group.md` composes three measurements with the
classification of 2-transitive groups of prime degree and concludes the base family is
**A₂₉ or S₂₉**, adding: *"A₂₉ against S₂₉ is not decided here and probably cannot be from
statistics."*

It is decided here, and not from statistics — from the return plus a parity argument. The
base family is **A₂₉**.

## Robustness to the tokenization

The word gap depends on which marks advance the clock, and
`rotor-machine-compact-state.md` audits six conventions:

| word gap | parity | forces |
|---|---|---|
| 1,378 | even | nothing |
| 1,448 | even | nothing |
| **1,449** (repo default, and the convention ruling) | odd | **σ even** |
| 1,451 | odd | σ even |
| 1,709 | odd | σ even |
| 1,711 | odd | σ even |

Four of six force it; the other two leave parity free. So the conclusion holds under the
ruling and under most alternatives, and is **vacuous rather than contradicted** under the
rest. No convention gives the opposite answer.

## Scope — three conditions, all named

1. **The repeat is a state return**, not the 1-in-2,700 coincidence
   (`dju-bei-is-more-surprising-than-recorded.md`). This is the load-bearing assumption.
2. **The step has the form `g^a ∘ σ`** with g of order 5 — the walk's own form. A step
   containing an odd factor other than σ would change the arithmetic.
3. **The gap is odd** under the operative tokenization, which it is.

## Status

**Status**: confirmed (exact parity argument, verified numerically) *conditional on* the
return being genuine. `experiments/dju_bei_parity.py`.

## Related

- `dju-bei-needs-a-product-step.md` — the product form this exploits.
- `base-family-is-the-symmetric-group.md` — the question this closes.
- `dju-bei-is-more-surprising-than-recorded.md` — the condition it rests on.
