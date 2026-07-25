---
type: hypothesis
---
# Hypothesis: The Period-5 Step is a Mixed-Alphabet (Quagmire) Vigenere

## Claim

The letter step is not a general mixed permutation `g` but a **shift in a
mixed alphabet**: each step is `K ∘ (add δ) ∘ K⁻¹` for one mixed alphabet
`K` and a per-phase offset `δ`, with the five offsets summing to
0 (mod 29) so the alphabet returns after five letters. The per-word base
step `σ` is unchanged. The key becomes **(K, δ₁…δ₅, base₀, σ)** — and
`K` can be keyword-derived, which makes it the first formulation of the
walk with a plausibly *enumerable* key.

## Status

**Status**: unresolved (not excluded — reaches the doublet rate, the d5
echo and the d6 dip; the discriminating prediction is zero coincidence
leak at d2/d3/d4, where the data are currently ambiguous)

## Mechanism

Write `u = K⁻¹(p)`. Then `c[j] = K(u[j] + s_j)` under the word base,
where `s_j` is the running sum of offsets, periodic mod 5. Consequences:

- **d5 echo**: `s_{j+5} = s_j`, so positions five apart share an
  alphabet — a full echo, exactly as for `g⁵ = id`.
- **Doublets**: `c[i] = c[i-1]` iff `u[i] − u[i-1] = −δ` — a doublet
  needs a specific delta in the *transformed* plaintext. Because `K` is
  free, that distribution can be reshaped; this is what separates the
  mixed case from the plain one (`length-clocked-walk.md`: an unmixed
  5-letter Vigenere floors at 0.0119, 1.9x too high).
- **d6**: spans five steps plus one, so the relation equals the d1
  relation — the suppression is inherited and the d6 dip follows, same
  as under `g⁶ = g`.

## Evidence for

- **The doublet rate is reachable** (`experiments/sigma_algebraic_floor.py`
  for the plain case; the mixed case computed alongside it). The
  achievable relations are exactly the single 29-cycles, and the
  bigram table is sparse (344 of 841 cells never occur), so a
  minimum-diagonal 29-cycle reaches **0.00007**. Optimising `K` and the
  five offsets jointly against the real phase weights
  (0.086/0.340/0.270/0.182/0.122) gives a doublet rate of **0.0017**,
  comfortably below the observed 0.0063 — so unlike the plain Vigenere
  this family is *not* excluded, and the observed rate sits above its
  floor exactly as it does for the mixed-permutation model.
- **The optimum has a suggestive shape**: the cheapest schedules use one
  offset for four phases and a second offset once, placed on the
  lightest-weighted phase (e.g. δ=18 four times, δ=15 once, summing to
  0 mod 29). That is "one step repeated, one step different" — the same
  4+1 shape the stay-slot idea proposed, arrived at independently.
- **The key could be small and human-usable.** `K` is a keyword-mixed
  alphabet — the classic Quagmire key — and the offsets are five
  numbers. This is the first walk formulation whose key a pencil-and-
  paper designer would plausibly write down, and the first that could be
  ENUMERATED: keywords x offset schedules filtered to the right doublet
  rate is a ~10⁶-scale search, against ~10⁹-10¹⁰ for grid-built `g`
  (`g-from-5x5-grid.md`). Given the (g, σ) landscape has no gradient
  (`no-known-plaintext-foothold.md`), enumerability is the property that
  matters most.

## Evidence against / the discriminator

- **It predicts NO coincidence leak at d2, d3, d4.** A conjugated shift
  `K ∘ (add δ) ∘ K⁻¹` with δ ≠ 0 is a single 29-cycle and therefore has
  **no fixed points**, so the relation at every distance not divisible
  by 5 is fixed-point-free and those cells must sit exactly at
  background. The order-5 `g` model predicts the opposite: `g^d` retains
  `g`'s fixed runes, giving a leak of `f/29 ≈ 0.14` at those distances
  (`g-from-5x5-grid.md`). Measured returned fractions: φ2 uninformative,
  **φ3 = 0.17 ± 0.14** (1.2σ from zero), **φ4 = 0.38 ± 0.19** (2σ from
  zero). Both lean toward a leak, i.e. toward fixed points and against
  this hypothesis — but neither is decisive, and φ4 is the corpus's
  standing anomalous cell (`mixed-cycle-progression.md`), so it cannot
  currently arbitrate.
- Not yet simulated through the full battery. Everything above is
  achievability arithmetic plus the shared structure of the walk; the
  model must still reproduce flat unigrams, zero triplets, the seam
  behaviour and the d1-d10 profile end to end.

## Predictions

- d2, d3 and d4 sit at background exactly (no fixed-point leak); a
  sharper plaintext reference would decide this against the order-5
  model.
- The offsets are recoverable independently of `K`: under a correct `K`,
  the doublet positions concentrate on one plaintext delta per phase.
- Enumerable attack: for each candidate keyword-derived `K`, compute the
  29 offset costs, keep only offset schedules summing to 0 (mod 29) that
  land the doublet rate in 0.004-0.009, then verify with the 2-rune word
  objective (`no-known-plaintext-foothold.md`).

## Scripts

- `experiments/sigma_algebraic_floor.py` — the plain-Vigenere exclusion
  and the arithmetic-family floors this hypothesis escapes.

## Related

- `length-clocked-walk.md` — the parent model; this replaces its general
  mixed `g` with a conjugated shift, keeping everything else.
- `g-from-5x5-grid.md` — the rival construction for `g`, which is not
  enumerable; the fixed-point leak is what separates them.
- `periodic-polyalphabetic.md` — plain periodic Vigenere, disproved; this
  is not that, because the per-word base `σ` destroys the period.
- `mixed-cycle-progression.md` — the d2/d3/d4 measurements that would
  arbitrate.

## Verdict

Unresolved and worth pursuing. A mixed-alphabet Vigenere step clears the
doublet floor that kills the plain one (0.0017 achievable against 0.0063
observed), reproduces the d5 echo and the d6 dip by the same algebra as
`g⁵ = id`, and — decisively for the attack — has a key a designer would
actually use and a searcher could actually enumerate. It differs from
the order-5 `g` model in one measurable place: it forbids the
fixed-point leak at d2/d3/d4 that the `g` model requires. The data lean
weakly the other way (φ4 = 2σ from zero), which is the same unresolved
cell that troubles every model, so the question is open.
