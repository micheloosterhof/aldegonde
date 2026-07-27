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

**Status**: disproved for the keyword family (enumeration run, negative
— see "The enumeration, run"), with a register caveat. Not disproved for
freely-designed (non-keyword) mixed alphabets. An earlier "disproved"
verdict rested on a 12-keyword sample and was withdrawn; this one rests
on the full ~3.1×10⁸-key enumeration.

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
but 12,064 candidates is a list small enough to score per candidate —
though the full battery and the 2-rune verifier need a complete key,
so the per-candidate cost is the offset-schedule space, not one run
(see Verdict). This is a genuine enumerable set — the
first in the investigation.

**The space step: zero at the point target, but see the section below.**
Zero keyword alphabets reach 0.0079 exactly, and zero random ones
either (minima 0.0092 and 0.0099). Read as an exclusion this is WRONG —
0.0079 is a 23-event measurement with a 95% CI of [0.0050, 0.0118], and
~130 keyword candidates sit comfortably inside it. The correct reading
of these numbers is that sampled alphabets cluster just above the point
estimate, not that they are excluded.

## The two targets are the SAME rate (July 2026) — and this voids the σ exclusion

The g and σ targets were treated as two distinct numbers, 0.0063 and
0.0079. They are not significantly different:

| | doublets / opportunities | rate | 95% CI |
|---|---|---|---|
| within-word (g) | 63 / 10,028 | 0.0063 | [0.0048, 0.0080] |
| seam (σ) | 23 / 2,927 | 0.0079 | **[0.0050, 0.0118]** |
| difference | | +0.0016 | z = +0.87, **p = 0.38** |
| pooled | 86 / 12,955 | 0.0066 | [0.0053, 0.0082] |

This is the boundary-blindness of the doublet suppression, restated: one
rate, measured twice. And the seam figure rests on **23 events**, so its
interval is wide — which matters, because the σ exclusion above compared
candidates against 0.0079 as though it were exact. It is not, and the
comparison is void:

| threshold | keyword σ candidates at or below |
|---|---|
| 0.0079 (the point target used) | 0 |
| 0.0092 (best candidate found) | 2 |
| 0.0100 | 17 |
| 0.0111 | 130 |
| 0.0118 (upper 95% CI) | 404 |

A σ with diagonal 0.0092 predicts 26.9 seam doublets against 23 observed
(Poisson z = −0.76); at 0.0100, 29.3 predicted (z = −1.16). Both are
entirely consistent with the data. Only past ~0.0118 does the prediction
strain (34.5 expected, z = −1.96).

**So keyword σ is NOT excluded.** Roughly 130 keyword-disk candidates sit
comfortably inside the observed seam behaviour — `monazite`,
`decentralism`, `endocarditis`, `Reubenites` and so on; at the upper 95%
CI the list is 404. Combined with the 12,064 keyword `g` candidates, the
joint space is ~4.8×10⁶ pairs. **The enumerable-key hypothesis is alive on
both halves**, and the "bottleneck is σ" conclusion is withdrawn — it was
an artifact of treating a 23-event measurement as a hard threshold.

## The schedule census (July 2026) — the enumeration is ~10⁸ full keys

`experiments/quagmire_schedule_census.py` counts what actually has to
be enumerated: (alphabet, schedule) pairs, not alphabets. Per alphabet
the five offsets (Σδ ≡ 0 mod 29) give ~29⁴ schedules, but the
within-word doublet band plus one corpus-mandated exclusion prune them
to ~8 on average:

- **The floor-based candidate list was the wrong lens.** Selecting
  alphabets by their cheapest single turn (the 12,064) misses alphabets
  whose five phases *combine* into the band: the phase-decomposed
  criterion passes 341,317 of 787,592, and 97,098 of those have at
  least one admissible schedule.
- **Zero offsets are excluded by observation, not choice.** A zero
  offset is an identity letter step: its doublets are plaintext doubles
  concentrated at one phase — a mod-5 comb and a plaintext-double
  position profile, both measured absent (doublet positions uniform
  mod 5; profile flat, `stay-slot-hold.md`). This rejects 2,277,398
  otherwise-in-band schedules, ~74% of the raw band.
- d1 band [0.0049, 0.0080] (Wilson CI of 63/10,028), no zero offset:
  **784,931 (alphabet, schedule) pairs** across 97,098 alphabets.

**The d6 prediction is a free second filter, and the family passes
it.** Under a period-5 schedule the relation at distance 6 collapses to
a single offset (six consecutive offsets sum to the next one over), so
predicted d6 is exactly computable per candidate — as are d4 (the
negated missing offset) and d1, all validated against direct simulation
in the script. Two results: the family spans the observed d6 depth
easily — minimum predicted d6 is **0.0076**, well below the observed
0.0245, so scheduled conjugated shifts CAN produce the d6 dip that no
cycle-type census could (`mixed-cycle-progression.md`) — and requiring
predicted d6 inside the observed CI [0.0173, 0.0345] keeps **562,165
pairs** (72%). d4 is a score, not a filter (its CI includes
background): 27.7% of survivors predict d4 above background, the
direction the corpus leans.

With the σ side at **400 (disk, turn) pairs** in the seam CI (matching
the exhaustion's 404-at-CI count), the joint space is

    562,165 × 400 ≈ 2.2 × 10⁸ full keys

— every key fully specified (K_g, five offsets, K_σ, turn), with base₀
free (`no-known-plaintext-foothold.md`). At a millisecond per key for
the DJU-BEI base-agreement walk and the 2-rune verifier, that is
CPU-days, not CPU-centuries: the first fully concrete, fully costed
enumeration the investigation has had.

Not yet folded in: the d2/d3 predictions (pair/triple offset sums,
generically at background but cheap to verify per candidate), the
positional-profile constraint on the diagonal class, and the
requirement that the same schedule leave the seam channel clean.

### The census in plain terms

For any candidate (alphabet + five turns), three statistics of the
ciphertext it would produce are predictable exactly, with no
simulation: the double-letter rate and the repeat rates at distances 4
and 6. The corpus fixes what those must be, so every key that could
not have produced the corpus's statistics is discarded before any
decryption is attempted. Three prunings do the work: of the ~700,000
turn-combinations per alphabet, only ~8 give the right double-letter
rate; three quarters of those use a null turn (one step leaves the
alphabet in place), which would bunch the doublets at every 5th
position and shape them like natural double letters — fingerprints the
corpus demonstrably lacks; and the distance-6 repeat rate cuts another
quarter, with the bonus that this family is the first mechanism found
that can reach LP's unusually deep distance-6 dip at all. What
survives is ~560,000 letter-wheel keys × 400 space-wheel keys ≈ 220
million complete keys — days of compute to try exhaustively, not
centuries. Caveats: all of this lives inside the keyword assumption
(keywords are not statistically special, merely listable), and the
prediction tables come from a stand-in register (runeglish prose in
the LP length mix).

## Testing a candidate key (the success metric)

Neither quadgram fitness nor IoC is the primary test — quadgrams have
no gradient here (`no-known-plaintext-foothold.md`) and unigram IoC is
blind to the wiring. The validated protocol is layered, cheapest
first:

1. **DJU-BEI agreement, base-free.** Given a full key, every per-word
   base is `base₀ ∘ M_w` with `M_w` a KNOWN permutation product, so the
   state-return condition `base_1477 = base_2926` reduces to
   `M_1477 = M_2926` — checkable with zero unknowns, one 2,928-step
   walk per key. (The unconditional 6-point weakening — enough fixed
   points in `M_1477 ∘ M_2926⁻¹` — passes a wrong key at ~1e-3.)
2. **The 2-rune likelihood, fitting base₀.** For survivors, hill-climb
   `base₀` on the log-likelihood of the 465 decrypted 2-rune words
   against the register function-word distribution
   (`two_rune_gradient.py`, validated on planted keys: exact recovery
   on the first restart, a 4,047-nat gap between true and random —
   there is no wrong-key basin to worry about because `base₀` is the
   only thing being fitted and the rest of the key is frozen).
3. **Full-decryption confirmation.** Only for keys that light up
   step 2: decrypt everything; a correct key must show plaintext-like
   IoC (~1.8, calibrated on the Parable) and readable runeglish under
   quadgram scoring. At this stage both work fine — they fail only as
   search gradients, not as verifiers of a fully-specified decryption.

## Three of the four "cheap filters" are vacuous (July 2026)

Earlier text here and in `length-clocked-walk.md` described the joint
space as ~10⁶ pairs "before the cheap filters (parity, σ ∉ ⟨g⟩, base
count, the DJU-BEI abelianization) are applied", implying the stack would
cut it substantially. Measured, it does not:

| filter | effect on the Quagmire candidate space |
|---|---|
| joint doublet count | **vacuous** — 4,825,600 of 4,825,600 pairs pass |
| parity (σ even) | **vacuous** — 0 of 56,000 conjugated shifts rejected |
| DJU-BEI abelianization | **vacuous** — no content beyond parity |
| σ ∉ ⟨g⟩, base count ≥ ~600 | unmeasured here; on this space they exclude only same-disk pairs (two conjugated shifts generate the same cyclic group only when the disks agree, and a distinct rotating disk already yields full base diversity), so likely near-vacuous too |

- **Joint doublet count.** `r_g` is an alphabet's *floor* — the cheapest
  non-identity turn — and a real schedule picks five offsets summing to
  0 (mod 29), so it can only cost MORE. The constraint is therefore
  one-sided: reject only when the cheapest possible joint total already
  overshoots. The largest floor total in the candidate set is ~98,
  against a ceiling of 105, so nothing is excluded. An earlier two-sided
  window reported a 96% pass rate; that test was mis-shaped and was
  discarding the *best* candidates (`impletive`, floor 0.0010, gives a
  floor total near 39 and was being rejected for being too low).
- **Parity.** Every non-identity conjugated shift on 29 points is a
  single 29-cycle, i.e. 28 transpositions, i.e. even. The parity
  condition is automatically satisfied by every Quagmire σ and can never
  reject one. It retains force only for a general (non-Quagmire) σ.
- **DJU-BEI abelianization.** See below.

## The abelianization relation is not an independent constraint

`[g] = −1449·[σ]` is a relation in the abelianization of the *free* group
on two generators. It constrains the concrete permutations only if
⟨g, σ⟩ actually has a matching abelian quotient. Computing |G/G′|
directly for order-5 `g` (k = 1…5 five-cycles) against both a random σ
and a 29-cycle disk σ:

| σ type | |G/G′| observed |
|---|---|
| random permutation | 1, 1, 1, 2, 2 |
| 29-cycle disk (Quagmire) | 1, 1, 1, 1, 1 |

Never larger than Z₂. These groups are A₂₉/S₂₉ or their point
stabilizers — g's fixed points give σ a good chance of sharing one — and
all have abelianization at most Z₂. So the relation collapses to the
parity condition, which for a Quagmire σ is itself vacuous. It is not a
fourth filter alongside parity; where it is not parity, it is nothing.

Scope: ten sampled (g, σ) draws, not a proof. A specially-constructed
pair generating a small solvable group could have a larger abelian
quotient — but such a pair is already excluded by the base-count
requirement, which demands a large orbit of distinct bases.

**The one place the relation IS valid** is `sigma-power-step.md`, where
it is applied under the assumption σ = g^k. That makes the group ⟨g⟩ ≅
Z₅, genuinely abelian, so the mod-5 arithmetic giving k = 1 is sound.
That use stands; the general-filter uses do not.

Net: the only surviving cheap filters are σ ∉ ⟨g⟩ and the base count.
Everything else in the stack was doing no work, and the real gate is the
expensive 1,449-step state return.

**Why the two nonetheless behave differently under sampling.** Both steps
need the same kind of low diagonal, and it is worth resisting the story
that σ is a different sort of object:

| | within-word (g) | cross-word (σ) |
|---|---|---|
| observed target | 0.0063 | 0.0079 |
| assignment floor | ~0.0000 | 0.0048 |
| target as % of the floor→random span | 18.2% | 10.3% |
| target, sd below the random mean | 2.3 | 3.6 |

σ's constraint is tighter by less than a factor of two in headroom —
enough to turn 1.5% of sampled alphabets into 0%, because that is a
Gaussian tail, but not a difference in kind. The cause is *not* that the
cross-word table is more concentrated overall (it is less: cell
concentration 5.620 vs 7.695). It is that the word-FINAL marginal is
concentrated (IoC 2.675, against 1.763 for initials and 1.770 for
within-word rows): the common finals E/S/T/D/N must each be paired with
something, so the assignment cannot route everything into near-empty
cells and the floor lifts from ~0 to 0.0048.

**Register caveat, and it bites here harder than anywhere else.**
Within-word bigrams are mostly morphology and travel between registers;
word-final and word-initial distributions are driven by function words
and sentence shape, and the LP's register is aphoristic and liturgical,
unlike the prose the table is built from. The σ exclusion therefore
rests on the more register-sensitive of the two tables. A register whose
finals are less concentrated would lower the floor and could put 0.0079
back inside reach of sampled alphabets.

Net: with the target's uncertainty respected, the enumerable-key
hypothesis survives on BOTH halves — ~12,064 `g` candidates and ~130 σ
candidates — and the σ half is additionally contingent on the cross-word
table being register-representative.

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
see `sigma-power-step.md`. The superseded 12-keyword samples here and
for the σ-disk were 12-draw samples, not family exhaustions, and added
no independent weight: on the within-word table keywords sit at the
83rd percentile of random best-of-12, and on the cross-word table at
the 12th. Where a 12-draw sample fails to reach a target, that is a
statement about the sample size.

The underlying rule therefore survives only in a narrower form: the
two exhaustive demonstrations establish that the relation cannot be
ARITHMETIC. The keyword families, tested at scale by the
full-dictionary exhaustion above, are not excluded — they contain
in-band members at the same rate random alphabets do (~1.5%), so
keyword structure supplies no advantage but no exclusion either.
Whether any keyword-shaped key passes the full battery is exactly what
the enumeration is for.

## Scripts

- `experiments/quagmire_walk_sim.py` — keyword-K floors and the
  full-battery run.
- `experiments/sigma_algebraic_floor.py` — the plain-Vigenere and
  arithmetic-family floors this was meant to escape.
- `experiments/keyword_exhaustion.py` — the full-dictionary family test
  producing the 12,064 `g` and 404 σ candidates.
- `experiments/joint_keyword_search.py` — the joint space and the
  one-sided doublet filter.
- `experiments/quagmire_runner.py` — the full enumeration: DJU-BEI
  6-point return filter + 2-rune base₀ fit, with a manufactured-key
  self-test; the negative result above.
- `experiments/abelianization_check.py` — |G/G′| and the parity check
  behind the vacuity table (needs `sympy`).

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

Unresolved and live on both halves. The full-dictionary exhaustion gives
**12,064 keyword `g` candidates** clearing the within-word diagonal and
**~130 keyword σ candidates** consistent with the 23 observed seam
doublets (404 at the upper 95% CI) — a joint space of ~4.8×10⁶ pairs.
That is enumerable, and it is the only formulation of the walk for which
that is true.

The cheap pair-level filters do not reduce the space — the joint
doublet count, parity and the DJU-BEI abelianization are all vacuous on
it (see above) — but the schedule census does: the ~29⁴ offset
schedules per alphabet collapse to ~8 under the doublet band and the
no-zero-offset exclusion, and the exactly-computable d6 prediction
keeps 72% of those. The full joint space is **~2.2 × 10⁸ complete
keys** (562,165 g alphabet-schedules × 400 σ disk-turns), each directly
verifiable with base₀ free.

An earlier verdict here called σ the bottleneck. That rested on
comparing candidates against 0.0079 as an exact threshold when it is a
23-event measurement with a 95% CI of [0.0050, 0.0118]; it is
withdrawn. The two doublet rates (within-word 0.0063, seam 0.0079) are
not significantly different at all — z = 0.87, p = 0.38 — and are best
read as one rate, 0.0066, measured on two tables.

Standing against the hypothesis: it forbids the d2/d3/d4 fixed-point
leak that φ3 = 0.17 ± 0.14 and φ4 = 0.38 ± 0.19 weakly favour; viable
keywords must disrupt the canonical order substantially, so they are
long and specific rather than memorable; and the σ half rests on the
register-sensitive cross-word table.

## The enumeration, run (July 2026) — negative for the keyword family

`experiments/quagmire_runner.py` streamed the full candidate space —
**313,972,400 complete keys** (keyword `g` alphabet-schedules × keyword
σ disk-turns, within the register-derived diagonal/seam/d6 bands) — and
tested each against two necessary conditions of the true key:

1. **DJU-BEI partial return.** The observed ciphertext repeat forces
   base₁₄₇₇ and base₂₉₂₆ to agree on the 6 plaintext image points, i.e.
   ≥6 fixed points of the interval step-product (base₀-independent).
   **Not** full base equality: that would require a 1,449-step product
   of non-commuting permutations to be the identity (~1/29!), reachable
   only by the degenerate σ∈⟨g⟩ class, so a full-equality filter can
   never pass a genuine key (an early run made exactly this error and
   found only 69 degenerate `bases=29` returns).
2. **The 2-rune function-word likelihood.** Each of the 186,465 keys
   passing the ≥6 filter (the chance rate, 5.9×10⁻⁴) was scored by
   fitting base₀ to the 465 real LP 2-rune words. A wrong key floors at
   the random level (~−4950, verified); a genuine key scores ~−1300 (a
   planted key the pipeline recovers exactly, `manufactured_test`).

**Result: zero keys scored above −4000.** Every one of the 313.97M
floored at random. No keyword-derived Quagmire key decrypts the corpus.

**Scope of the exclusion.** It covers keyword-derived alphabets
(196,898 dictionary words × 4 construction rules, both wheels) whose
diagonals fall inside the observed bands. It does **not** exclude:
freely-designed (non-keyword) mixed permutations — the general
length-clocked walk, never enumerable; a true key whose diagonals fall
**outside** the bands because the candidate bands were computed against
a stand-in prose register (Pride & Prejudice runeglish), not the LP's
own aphoristic register — the standing register caveat, and the biggest
remaining uncertainty; and the edge case where the 6 DJU-BEI agreements
are not distinct (the filter used ≥6; an ≥5 fallback is untested).

## Verdict (updated)

The keyword-Quagmire formulation — the investigation's only enumerable
key — has been enumerated in full and is **negative**: none of the
~3.1×10⁸ keyword keys within the register-derived bands decrypts the
corpus. The result is a genuine test, not the vacuous full-return filter
of the first attempt: the pipeline provably recovers a planted key, and
the 2-rune discriminator separates real (~−1300) from wrong (~−4950) on
real LP data. What survives is not keyword-shaped: either a freely
designed mixed alphabet (no enumeration advantage over the general
walk), or a keyword key whose diagonals sit outside the bands under the
LP's true register. The next reducible question is therefore the
register — whether the candidate bands, computed on prose, are
representative — not another pass over the same keyword family.
