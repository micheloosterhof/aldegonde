---
type: hypothesis
---
# Hypothesis: The Period-5 Step is a Mixed-Alphabet (Quagmire) Vigenere

## Claim

The letter step is not a general mixed permutation `g` but a **shift in a
mixed alphabet**: each step is `K ∘ (add δ) ∘ K⁻¹` for one mixed alphabet
`K` and a per-phase offset `δ`, with the five offsets summing to
0 (mod 29) so the alphabet returns after five letters. The per-word base
step `σ` is unchanged. The key would be **(K, δ₁…δ₅, base₀, σ)**, with
`K` keyword-derived — the classic Quagmire key, and small enough to
enumerate.

## Status

**Status**: disproved as proposed — a keyword-derived `K` floors at
0.0101-0.0197 on the doublet rate against the observed 0.0063. A freely
designed `K` clears the rate but is a full 29-permutation, forfeiting
the small enumerable key that was the point.

## Mechanism

Write `u = K⁻¹(p)`. Then `c[j] = K(u[j] + s_j)` under the word base,
where `s_j` is the running sum of offsets, periodic mod 5:

- **d5 echo**: `s_{j+5} = s_j`, so positions five apart share an
  alphabet — a full echo, as for `g⁵ = id`.
- **Doublets**: `c[i] = c[i-1]` iff `u[i] − u[i-1] = −δ`, i.e. a doublet
  needs a specific delta in the *transformed* plaintext. This is the
  degree of freedom the plain Vigenere lacks (which floors at 0.0119 on
  English's own deltas, `length-clocked-walk.md`).
- **d6**: five steps plus one, so its relation equals the d1 relation —
  the suppression is inherited and the dip follows, as under `g⁶ = g`.
- The achievable step relations are exactly the single **29-cycles**
  (conjugates of a nonzero shift), which are fixed-point-free — the
  source of this model's one distinguishing prediction, below.

## Why it fails

A schedule's doublet rate is a weighted average of its offsets' costs,
so it can never beat the cheapest offset available under a given `K`.
That cheapest offset is therefore a hard floor per keyword, and every
keyword tested floors above the observation
(`experiments/quagmire_walk_sim.py`, offsets targeted at the observed
rate rather than at the floor):

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
| **freely designed K (not a keyword)** | **0.00010** | 0.02x |

End to end the best case (INSTAR) simulates d1 = 0.0215 against LP's
0.0063, with d6 = 0.0395 (no dip) and 3.3 triplets (LP has 0); an
order-5 `g` tuned identically on the same harness gives d1 = 0.0065,
d6 = 0.0310, 0.5 triplets — so the failure is the model's, not the
simulation's.

The escape — designing `K` freely against the bigram table — does reach
0.0001, but such a `K` is an arbitrary 29-permutation: no keyword, no
small key, and no enumeration advantage over the general mixed `g` it
was meant to replace. Nothing then distinguishes it favourably, and it
still carries the unfavourable prediction below.

## The distinguishing prediction (unfavourable)

Conjugated shifts with δ ≠ 0 are single 29-cycles and so have **no fixed
points**: every relation at a distance not divisible by 5 is
fixed-point-free, forcing d2, d3 and d4 to sit exactly at background.
The order-5 `g` model predicts the opposite — `g^d` retains `g`'s fixed
runes, leaking `f/29 ≈ 0.14` there (`g-from-5x5-grid.md`). Measured
returned fractions: φ2 uninformative, **φ3 = 0.17 ± 0.14**,
**φ4 = 0.38 ± 0.19**. Both lean toward a leak, i.e. against this model,
though φ4 is the corpus's standing anomalous cell
(`mixed-cycle-progression.md`) and cannot arbitrate on its own.

## What this establishes

The negative result generalises, and is the durable part. Together with
the plain Vigenere floor (0.0119) and the arithmetic-σ floors
(0.0122-0.0211, `sigma-power-step.md`), this is the third independent
demonstration that **no key that is merely "mixed" can produce the
observed doublet suppression**. Keywords, shifts, affine maps and
keyword-conjugated shifts all leave the relation near the language's own
bigram statistics. Reaching 0.0063 requires a permutation deliberately
routed against the digraph table, rune by rune — which says something
about the author: whoever built this had runeglish digraph frequencies
in front of them, and it explains why no small, human-memorable key has
ever fit.

## Scripts

- `experiments/quagmire_walk_sim.py` — keyword-K floors and the
  full-battery run.
- `experiments/sigma_algebraic_floor.py` — the plain-Vigenere and
  arithmetic-family floors this was meant to escape.

## Related

- `length-clocked-walk.md` — the parent model, whose general mixed `g`
  this proposed to replace.
- `g-from-5x5-grid.md` — the rival construction; the d2/d3/d4 leak is
  what separates them.
- `periodic-polyalphabetic.md` — plain periodic Vigenere, disproved
  separately; this is not that, since the per-word `σ` destroys the
  period.
- `sigma-power-step.md` — the same floor method applied to `σ`.

## Verdict

Disproved in the form that mattered. The appeal was a keyword-sized,
enumerable key; keyword alphabets are not mixed enough to suppress
doublets, failing by 1.6x-3.1x across every keyword tried including
Cicada's own vocabulary. The version that clears the rate needs a
designed 29-permutation and so inherits every difficulty of the model it
was meant to simplify, while additionally forbidding the d2/d3/d4 leak
that the data weakly favour.
