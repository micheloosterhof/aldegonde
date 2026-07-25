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

## Superseded: the 12-keyword sample

An earlier pass tested twelve keywords, found all floored above the
target, and recorded the hypothesis as disproved. That was a statement
about the sample: twelve RANDOM alphabets floor the same way (the
keyword best-of-12 sat at the 83rd percentile of the random best-of-12
distribution, which reaches the target 12.8% of the time). The
end-to-end simulation likewise used INSTAR — one draw, not the best
available. Both are superseded by the family test below.

## The family test (July 2026) — the bottleneck is σ, not g

`experiments/keyword_exhaustion.py` runs the exhaustion the 12-keyword
sample was mistaken for: the full `/usr/share/dict/web2` (196,898 words
of length 4-12) under FOUR keyword→alphabet rules — remainder in
gematria order, remainder reversed, remainder continuing cyclically
after the last keyword rune, and keyword into a 5×6 grid read by
columns — giving 787,592 candidate alphabets, with a matched random
null at the same sample size.

| step | target | keyword candidates reaching it | random, same count |
|---|---|---|---|
| `g` (within-word) | 0.0063 | **12,064 of 787,592 (1.53%)** | 1.31% |
| `σ` (cross-word) | 0.0079 | **0 of 787,592** | 0.000% |

**The letter step is enumerable.** 12,064 keyword alphabets clear the
diagonal — best `impletive` at 0.0010, `irritability` 0.0011,
`Gilbertese` 0.0012. Keywords are not special (44th percentile of
random; the family works because it is large, exactly as for the grids),
but 12,064 candidates is a list one can push through the full battery
and the 2-rune verifier in hours. This is a genuine enumerable set — the
first in the investigation.

**The space step is not.** Zero keyword alphabets reach 0.0079, and zero
random ones either: the minimum over all 787,592 keyword candidates is
0.0092 and over 40,000 random draws 0.0099, both above the target. So
this is not a fact about keywords — **no sampled alphabet, of any
origin, supplies σ as a rotating disk**. A designed permutation does
(the assignment floor is 0.0048, and TSP-annealed 29-cycles reach far
below), but sampling never finds it. The cross-word table is simply more
concentrated than the within-word one — English word-final letters pile
on E/S/T/D/N and initials on T/A/S/W/H — so its diagonals resist being
pushed low.

Net: the enumerable-key hypothesis fails on **σ**, not on `g`, which is a
far sharper localisation than "no small key exists".

## Keyword clumping is a real structural filter

A keyword alphabet leaves the unused runes in canonical order after the
keyword, so it carries long ascending runs — and on those runs the
conjugated shift acts like a plain shift, which floors at 0.0119 and
cannot suppress doublets. The data show exactly that pressure:

| longest ascending run | candidates | hit rate |
|---|---|---|
| ≥ 10 | 128,745 | 1.66% |
| ≥ 15 | 16,930 | 1.05% |
| ≥ 20 | 2,208 | 0.27% |
| ≥ 24 | 314 | **0.00%** |

and the hit rate rises monotonically with how much of the alphabet the
keyword disturbs — 0.68% for keywords contributing 3 distinct runes,
1.53% at 7, 2.46% at 11. A viable keyword must break up the canonical
order substantially; heavily clumped alphabets are excluded outright.
This both narrows the candidate list and blunts the hypothesis's appeal,
since the surviving keywords are long and specific rather than short and
memorable.

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

Unresolved, and now precisely localised. The full-dictionary exhaustion
settles the two halves differently: **`g` can be keyword-derived** —
12,064 alphabets clear its diagonal, an enumerable candidate list and
the first the investigation has produced — while **`σ` cannot**, with
zero of 787,592 keyword alphabets and zero of 40,000 random ones
reaching the cross-word target. Since no sampled alphabet supplies σ as
a rotating disk, a Quagmire-shaped cipher would still need a designed
permutation for its space step, and the enumerable-key appeal collapses
there rather than at the letter step.

Two further constraints on any surviving keyword: it must disrupt the
canonical alphabet order substantially (heavily clumped alphabets score
zero hits), and the model still forbids the d2/d3/d4 fixed-point leak
that φ3 and φ4 weakly favour.

Next test, if pursued: run the 12,064 in-band `g` candidates through the
full battery, which would confirm or kill the letter-step half on its
own. The σ half needs a different idea entirely.
