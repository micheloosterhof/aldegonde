---
type: observation
---
# Observation: The Base Family Is A₂₉ or S₂₉ — the Classification Is Now Complete

## What three measurements now compose into

Degree 29 is prime, and that makes the possibilities finite and nameable. Three separate
measurements in this directory now close every branch.

**Step 1 — the family is transitive.** It has to be: the ciphertext unigrams are flat
(`flat-ioc.md`, χ² 26.4 on 28 df) while the plaintext's are not (χ² 1,574), and an
intransitive family cannot move mass between its blocks. `no-block-partition.md` confirms
it from the data, excluding every partition into three or more blocks at 100% planted
detection and every small two-block split by exhaustive enumeration.

**Step 2 — Burnside narrows it to a list.** A transitive permutation group of prime
degree p is either 2-transitive or Frobenius (contained in AGL(1,p) with the multiplier in
a proper subgroup of F_p*). The 2-transitive groups of degree 29 are, by the
classification:

| candidate | applies at degree 29? |
|---|---|
| A₂₉, S₂₉ | yes |
| AGL(1,29) | yes, order 812 |
| PSL/PGL(d,q) on projective points, 29 = (qᵈ−1)/(q−1) | **no** — checked exhaustively for prime powers q ≤ 400, d ≤ 8 |
| Mathieu groups | **no** — degrees 11, 12, 22, 23, 24 |
| AΓL(1,29) | same as AGL(1,29), since ΓL = GL for prime degree |

So the whole space is: **the Frobenius subgroups, AGL(1,29), A₂₉, S₂₉.**

**Step 3 — the measurements eliminate the first two.**

| branch | excluded by | how |
|---|---|---|
| Frobenius subgroups H₂, H₄, H₇ | `base-family-is-2-transitive.md` | the coset invariant H·(b−a), planted detection 1–2 orders of magnitude above the body |
| AGL(1,29) | `base-is-not-affine.md` | the triple invariant λ = (c_c−c_a)/(c_b−c_a); planted affine 620–1,252 against planted general 31.5–141.2, body 89.7 |

Nothing else is left.

> **The per-block base family is A₂₉ or S₂₉.**

## Why it matters

This is the strongest possible negative on the base side, and it is now measured rather
than assumed. **There is no algebraic structure in the base family to exploit.** The bases
are arbitrary permutations of 29 runes, so:

- no base key space small enough to enumerate — 812 was the last candidate, and it is gone;
- the orbit theorem's 2-transitivity condition holds *a fortiori*, so the local channel's
  13-bit ceiling (`why-the-body-resists.md`) stands on a classification rather than on a
  test that could have missed something;
- any model proposing a structured base family — a disk, a keyword alphabet, a rotor
  wiring drawn from a small set — is proposing something already excluded.

`compact_state_dichotomy.py` reached A₂₉/S₂₉ from the other direction, by measuring
|⟨g, σ⟩| for random order-5 g against random σ. That argument is conditional on the walk
being the right frame. This one is not: it reads the group off the ciphertext.

## Scope

- **The base is assumed constant within a block.** That is the shared premise of every
  model here, and `separators-are-the-cipher-unit.md` supports it by anchoring the phase
  to the separators.
- H₁₄ remains formally untested, but `base-family-is-2-transitive.md` shows its extra
  invariant is the quadratic-residue class of g^j(p_j) − g^i(p_i), which a non-affine g
  scrambles — so it carries nothing even if present.
- A₂₉ against S₂₉ is not decided here and probably cannot be from statistics —
  **but it is decided elsewhere, and not statistically.** `sigma-is-even.md` derives
  sign(σ) = +1 from the DJU-BEI return: the base step is a product `g^a ∘ σ`, g is even
  because its cycles are all 5-cycles, so the product's sign is sign(σ)^gap, and an
  identity return with an odd gap forces σ even. The repo-default gap 1,449 is odd. So
  the base family is **A₂₉**, conditional on the return being genuine.

## Status

**Status**: confirmed (composition of three measurements plus the classification of
2-transitive groups). The arithmetic is checked in
`experiments/affine_triple_invariant.py` and `experiments/compact_state_dichotomy.py`.

## Related

- `base-is-not-affine.md` — the step that removes AGL(1,29).
- `base-family-is-2-transitive.md` — the step that removes the Frobenius subgroups.
- `no-block-partition.md` — the step that establishes transitivity.
- `rotor-machine-compact-state.md` — the same conclusion under the walk's own premises.
