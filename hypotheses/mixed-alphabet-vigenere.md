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

**Status**: disproved as proposed (a KEYWORD-derived `K` cannot reach
the doublet rate — floors at 0.0101-0.0197 against the observed 0.0063).
A freely-designed `K` clears the rate but forfeits the small,
enumerable key that was the hypothesis's entire advantage, and is
disfavoured by the d4 leak.

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

## The kill: keyword alphabets are not mixed enough (July 2026)

Full-battery simulation (`experiments/quagmire_walk_sim.py`) with `K`
keyword-derived, offsets chosen to land on the observed rate rather than
at the floor:

| keyword | cheapest offset cost | vs observed 0.0063 |
|---|---|---|
| INSTAR | 0.0101 | 1.6x |
| PARABLE | 0.0102 | 1.6x |
| LIBERPRIMUS | 0.0110 | 1.8x |
| CIRCUMFERENCE | 0.0123 | 1.9x |
| MOBIUS, AETHEREAL, PRIMES, TOTIENT | 0.0123-0.0127 | 2.0x |
| DIUINITY | 0.0148 | 2.4x |
| WISDOM | 0.0164 | 2.6x |
| CICADA, SHADOW | 0.0194-0.0197 | 3.1x |
| **freely annealed K (not a keyword)** | **0.00010** | 0.02x |

A schedule's doublet rate is a weighted average of its offsets' costs,
so it can never beat the cheapest offset — the column above is a hard
floor per keyword. Every keyword tested floors 1.6x-3.1x above the
observation. The end-to-end run confirms it: the best case (INSTAR)
simulates d1 = 0.0215 against LP's 0.0063, with d6 = 0.0395 (no dip)
and 3.3 triplets (LP has 0), while an order-5 `g` tuned the same way
sits at d1 = 0.0065, d6 = 0.0310, 0.5 triplets.

This is the same failure as the plain Vigenere (`length-clocked-walk.md`,
floor 0.0119) and for the same reason: a keyword permutation is not
*designed against the bigram table*, so its conjugated shifts land near
the language's own delta statistics. The earlier 0.0017 figure came from
annealing `K` freely over all 29! alphabets — that `K` is not a keyword,
carries a full permutation's worth of key, and therefore gives no
enumeration advantage over a general mixed `g`, which was the whole
point of the hypothesis.

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

Disproved in the form that made it attractive. The appeal was a
keyword-sized, enumerable key: `K` from a word, five offsets, done. But
a keyword-derived `K` floors at 0.0101-0.0197 on the doublet rate
against the observed 0.0063 — 1.6x to 3.1x too high across every
keyword tried, including Cicada's own vocabulary — and the end-to-end
simulation confirms the failure (d1 = 0.0215, no d6 dip, triplets
present). The escape is a freely-designed `K`, which does clear the rate
(0.0001 achievable) but is a full 29-permutation: no keyword, no small
key, no enumeration advantage over the general mixed `g` it was meant to
replace, and it still carries the unfavourable no-leak prediction at
d2/d3/d4.

The general lesson is the durable part, and it now has three
independent confirmations (plain Vigenere, arithmetic σ, keyword
Quagmire): **the LP's doublet suppression cannot be produced by any key
that is merely "mixed"** — a keyword, a shift, an affine map, or a
keyword-conjugated shift all sit near the language's own bigram
statistics. The suppression requires a permutation deliberately routed
against the bigram table. Whatever the cipher is, its designer had the
digraph frequencies in front of them.
