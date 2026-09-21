---
type: disproof
---
# Disproof: The Per-Block Base Is Not an Affine Map

## The family that survived every earlier test

`local-channel-is-exactly-coincidence.md` proves that under a **2-transitive** base family
the only base-invariant statistic of a within-block *pair* is whether the two runes are
equal. `base-family-is-2-transitive.md` confirms the condition by excluding the proper
subgroups of AGL(1,29) — H₂, H₄, H₇ decisively, H₁₄ harmlessly.

Neither touches **AGL(1,29) itself**. It is 2-transitive, so it passes the orbit theorem's
condition and every pair test built on it. And it is by far the most attractive base family
still standing: 812 members against 29! ≈ 8.8 × 10³⁰, with 812 × 5 phases clearing the
≥ 949 alphabets `alphabet_count_bound.py` requires. If the bases were affine, the base key
space would collapse from astronomical to searchable.

## Triples are where it shows

2-transitive does not imply 3-transitive. The symmetric group *is* 3-transitive, so triples
of distinct runes form one orbit and carry nothing. AGL(1,29) is not. For an affine base
`x → m·x + t` and three positions in one block,

    c_b − c_a = m·(u_b − u_a)        c_c − c_a = m·(u_c − u_a)

so

    λ = (c_c − c_a) · (c_b − c_a)⁻¹  mod 29

cancels both m and t. It is base-invariant under affine bases and equals the underlying
ratio, which carries plaintext structure. Under a general base family it is scrambled.

## Result

**Disjoint** consecutive triples only — every triple of positions gives eleven times more
data, but they share runes and the χ² is then invalid, with general-base controls reaching
218 on 28 df from the dependence alone.

| | χ² of λ against uniform |
|---|---|
| planted **affine** bases (12 draws) | 620 – 1,252, median **848** |
| planted **general** bases (12 draws) | 31.5 – 141.2, median **82.2** |
| **body**, 3,357 triples | **89.7** |

The two families do not overlap anywhere. **The body sits at the general-base median.**

## Consequence

The per-block base is not affine. AGL(1,29) is excluded as a base family, and with it the
one remaining route to a base key space small enough to enumerate.

This is strictly stronger than the earlier subgroup work, which could only reach families
that *failed* 2-transitivity. AGL(1,29) passes that test and is excluded here, so the
"base family is 2-transitive" condition is now known to be satisfied by something larger
than the affine group.

## Scope

- Tests the base only. The letter step g is not constrained by this — and cannot be an
  affine map of order 5 anyway, since 5 does not divide 28
  (`compact_state_dichotomy.py`).
- Assumes the base is the same map across a block, which is the shared premise of every
  model here.
- Disjoint triples cost a factor of eleven in sample size. The separation is wide enough
  that it does not matter.

## Status

**Status**: disproved, with planted controls on both sides that do not overlap.
`experiments/affine_triple_invariant.py`, `--control` for the two null distributions.

## Related

- `base-family-is-2-transitive.md` — the subgroup scan this completes from above.
- `local-channel-is-exactly-coincidence.md` — the pair theorem that cannot see this.
- `rotor-machine-compact-state.md` — the compact-state argument, which noted AGL(1,29)
  would reopen if period-5 were retired; this closes it from the base side regardless.
