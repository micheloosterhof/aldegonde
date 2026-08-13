---
type: observation
---
# Observation: Sub-Chance Doublets Force a Tuned Permutation Relation

## Feature

Michel asked for a mechanism explaining the low doublet rate (within AND across
words) and the d5 echo, **without** g/σ permutations. This note records why that
combination is not available: for any cipher that is invertible position by
position, a sub-chance doublet rate is *equivalent* to a rare-diagonal permutation
relation. The primitives can be rings, grids, arithmetic or keywords; the constraint
is the same.

## The argument

Let the cipher be invertible at each position, `c_j = f_j(p_j)` with each `f_j` a
bijection on the 29 runes. Define `R_j = f_j⁻¹ f_{j+1}`. Then

```
c_j = c_{j+1}   ⟺   f_j(p_j) = f_{j+1}(p_{j+1})   ⟺   p_j = R_j(p_{j+1})
```

so the doublet rate is the average over positions of `Σ_b P(R_j(b), b)` — the
**diagonal of a permutation** on the plaintext bigram table. Chance is 1/29 = 3.45%;
the corpus shows 0.63% within words and 0.79% across. Reaching that requires the
`R_j` to be rare-diagonal, i.e. designed against the digraph table.

`R_j` is a permutation by construction. So "no permutations" and "sub-chance
doublets" are incompatible **within this class**, whatever the mechanism looks like
from outside. Only the diagonals matter, and a device that produces them is
producing a tuned permutation whether or not it is described as one.

Note this also explains the boundary-blindness cheaply: the argument never mentions
word boundaries, so it applies identically at a seam with `R = σ`.

## What a genuinely new mechanism would have to break

Per-position bijectivity. The known ways, and their status:

| class | how it escapes | status |
|---|---|---|
| **Fractionation** (bifid etc.) | `c_j` mixes coordinates from several `p` | **excluded structurally** — an output doublet needs both coordinates to collide, and balanced marginals floor the product near 1/(rows×cols) ≈ chance. Annealed 5×6 grids reach 0.0237–0.0246 against 0.0063 (`bifid-fractionation.md`) |
| **Ciphertext feedback** (`f_{j+1}` depends on `c_j` alone) | adjacent positions coupled by construction | **excluded empirically** — each group sharing a previous rune would be enciphered by one fixed map, so grouped IoC must read ~1.78; measured within words 1.0227 / 0.9979 / 1.0060 at lags 1/2/5 |
| **Mixed feedback** (ciphertext *and* plaintext taps) | a plaintext tap convolves the grouped distribution flat again | **not excluded by the grouped-IoC test** (`dual-autokey-lag1-lag5.md` reaches 1.046 where the pure form gives 1.756) — but it does NOT escape this note: its doublet suppression requires a tuned labelling, which is a permutation, and over random labellings it sits at chance |
| **Homophonic** (one plaintext letter, several runes) | the encoder simply declines to repeat, so suppression is free | **excluded by alphabet size** — 29 runes in, 29 out leaves no spare symbols (`homophonic-substitution.md`) |
| **Digraphic** (unit is a rune pair) | doublets constrained inside a pair | **disfavoured** — flat parity at periods 2–6 |

## The one structural gap

**Homophonic remains the only class** where the suppression would cost nothing rather
than being designed, and it fails only on alphabet size.

A mixed-feedback candidate (`dual-autokey-lag1-lag5.md`) appeared to escape this
conclusion and does not. Its apparent structural suppression — 2.28% against a 3.45%
chance — was one labelling's fluctuation: over 200 random labellings the mechanism
gives 3.41% ± 0.76, i.e. chance. Its suppression comes from tuning the labelling, and
a labelling is a 29-permutation. The conclusion of this note is unaffected. It would revive if the ciphertext
alphabet were larger than the plaintext alphabet — which is what
`thirty-symbol-disk.md` (unresolved) posits, treating the `.` mark as a 30th symbol.

The obvious version of that is already refuted. If a mark were inserted to break a
would-be doublet, the runes flanking a mark would be EQUAL by construction, so the
across-mark rate would be near 1. Measured: **0.786%**, i.e. suppressed like
everything else. Any surviving variant must therefore break doublets without leaving
equal runes on either side of the inserted symbol.

## What is NOT claimed

That no new mechanism exists. The argument is exact only for per-position-bijective
ciphers; outside that class it is a table of four known escapes with their statuses,
not a proof of exhaustiveness. A fifth escape not listed here would not contradict
anything measured.

Nor does any of this address the **d5 echo**, which is a separate requirement: the
transformation at positions `j` and `j+5` must coincide, so something must have
period 5 regardless of how the doublet question resolves.

## Scripts

- `experiments/sigma_local_budget.py` — the seam relations, including the across-mark
  rate quoted above.
- `experiments/information_budget.py` — the grouped-IoC and delta-stream measurements
  that exclude feedback.

## Related

- `bifid-fractionation.md`, `homophonic-substitution.md`, `thirty-symbol-disk.md`,
  `stream-cipher-no-repeat.md` — the four escape classes.
- `doublet-suppression.md` — the measurement being explained.
- `length-clocked-walk.md` — the model that pays the design cost this note describes.
