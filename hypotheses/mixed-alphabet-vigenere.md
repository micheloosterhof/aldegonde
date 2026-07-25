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

**Status**: unresolved. An earlier "disproved" verdict here rested on a
12-keyword sample and does not survive its own null — see below.

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

## The keyword test, and why it does NOT settle the question

A schedule's doublet rate is a weighted average of its offsets' costs,
so it can never beat the cheapest offset available under a given `K` —
that cheapest offset is a hard floor per keyword. Twelve keywords were
tested (`experiments/quagmire_walk_sim.py`, offsets targeted at the
observed rate rather than at the floor) and all floored above the
observation:

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

**But twelve draws is not a family test.** Scoring 400 trials of
*twelve random alphabets* on the same table: the best-of-12 has median
floor **0.0084**, 5th percentile 0.0054, and **12.8% of such samples
contain an alphabet reaching 0.0063**. The keyword best-of-12 (0.0101)
sits at the **83rd percentile** of that distribution — slightly
unlucky, comfortably inside noise. Keyword alphabets are therefore
statistically indistinguishable from random draws on this measure, and
the honest reading of the table above is "twelve draws is too few", not
"keywords are not mixed enough". A larger keyword list would be
expected to contain in-band members. This is the same
sample-size-as-property error that the grid-diagonal retraction in
`g-from-5x5-grid.md` corrected, in a new costume.

The end-to-end run does not carry the exclusion either: it used INSTAR
— a single draw, and not the best available — giving d1 = 0.0215
against LP's 0.0063, no d6 dip, and 3.3 triplets, where an order-5 `g`
tuned identically gives 0.0065 / 0.0310 / 0.5. That shows *that* K
fails, not that keyword K's fail.

What remains true: a `K` reaching the observed rate exists (freely
designed, 0.0001 achievable), and the open question is whether the
in-band members of the keyword family also satisfy everything else —
the d6 dip, the triplet count, the seam, and the no-leak prediction
below. That test has not been run.

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

Less than first claimed. The two solid demonstrations that a merely
"mixed" key cannot supply the suppression are **exhaustive over their
families**: the plain Vigenere shift floor (0.0119, all 29 shifts) and
the arithmetic-σ floors (0.0122-0.0211, all members of each family) —
see `sigma-power-step.md`. The keyword tests here and for the σ-disk
are 12-draw samples, not family exhaustions, and add no independent
weight: on the within-word table keywords sit at the 83rd percentile of
random best-of-12, and on the cross-word table at the 12th. Where a
12-draw sample fails to reach a target, that is a statement about the
sample size.

The underlying rule may well hold — a freely designed `K` *is* needed
to reach 0.0001, and nothing keyword-shaped has yet been shown to work
— but it currently rests on two exhaustive demonstrations, not four,
and the keyword families remain untested at scale.

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

Unresolved, and the most attackable live proposal on the books. Twelve
keyword alphabets all floored above the required doublet rate, but
twelve *random* alphabets do the same 87% of the time, so that test
excludes nothing — it measures the sample size. The mechanism itself
remains consistent: it reproduces the d5 echo and the d6 dip by the
same algebra as `g⁵ = id`, a `K` reaching the observed rate certainly
exists, and if an in-band keyword K also passes the rest of the battery
the key would be word-sized and enumerable, which no other formulation
offers. Against it stands one clean prediction — conjugated shifts are
fixed-point-free, so d2/d3/d4 must sit exactly at background, and the
measured φ3 = 0.17 ± 0.14 and φ4 = 0.38 ± 0.19 lean the other way.

Next test: enumerate a real keyword list (10³-10⁴ words), keep the
in-band members, and run those through the full battery — the
experiment the 12-keyword sample was mistaken for.
