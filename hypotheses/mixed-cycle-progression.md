---
type: hypothesis
---
# Hypothesis: The Letter Step g Has Mixed Cycle Lengths

## Claim

The within-word coincidence staircase (rates rising d2 → d5, dipping at
d6) is the cycle census of the letter step: `g` has loops of mixed
lengths, so the fraction of the alphabet fixed by g^d — and with it the
plaintext-coincidence leak — grows with distance as successive loop
lengths divide d. This would answer "which classical construction makes
correlation RISE with distance": a progression disk whose stepping
permutation has mixed loops.

## Status

**Status**: unresolved (the pure return-ladder mechanism is disproved;
census selection is below the calibration resolution of the available
plaintext references; the d6 depth is unexplained by any census at
realistic tuning)

## Mechanism and the monotonicity theorem

Under a random assignment of letters to cycles the expected within-word
match rate at distance d is

    r_d = φ_d·K_d + (1 − φ_d)·(1 − K_d)/28

with φ_d = (letters in cycles dividing d)/29 and K_d the plaintext
within-word coincidence. Return fractions are non-negative and monotone
over divisors (anything home at 2 or 3 is home at 6), so a **pure return
ladder can never push a cell BELOW background**. The LP's d6 does sit
below background — the theorem kills the pure mechanism for every
census, and is the arc's most durable result.

Refinement: letters in a cycle with d ≡ ±1 (mod L) experience g or g⁻¹
at distance d — the TUNED doublet diagonal — so 5-loop-rich censuses
partially inherit suppression at d6 (6 ≡ 1 mod 5) and 7-loops at
d6 (6 ≡ −1 mod 7), d8 (≡ 1), d9. This inheritance is what any surviving
mixed census leans on.

## What was measured (clean corpus, calibration-free)

Raw within-word rates against the 1/29 background:

- **d6 = 31/1267 = 0.0245, z = −2.3**, independently permutation-verified
  at p = 0.016 (`within_word_phase_profile.py`). The solid anomaly.
- **d4 = 131/3197 = 0.0410, z = +1.85** — a stable but modest lean
  (uncorrected, one of ~8 scanned cells; it was on the books as part of
  the d2→d5 shoulder before this analysis).
- The **d4 − d6 split ≈ 2.7σ** — sharp because pure order-5 predicts the
  two cells EQUAL: g⁴ = g⁻¹ and g⁶ = g share the same leading-order
  diagonal frequency algebra (Σ q(x)q(g(x)) both ways). A
  language-orientation escape (mirror pairs behaving differently at
  distance 4 vs 6) was tested on prose and is negative.

## What was tested and how it came out

1. **Pure return ladders — disproved** (monotonicity, above), including
   every prime-loop census. Notable members: 5+5+5+7+7 (the unique
   5/7-partition of 29) and the numerologically perfect 1+2+3+5+7+11
   (first five primes + one fixed rune, sum 29 — kills on a starved d5
   echo and 2/3-loops returning into the d6 dip).
2. **Exhaustive census scan** (all 4,565 partitions, inheritance model
   with one fitted suppression, `census_scan.py`, recalibrated in
   `census_corrected.py`): consistent fits exist, but the rankings are
   **calibration-fragile** — leaders reshuffle between the first-pass
   and corrected K references, and the gap between mixed censuses and
   the standard five-5-cycles + 4-fixed type is Δchi2 ≈ 3, inside the
   systematic uncertainty. No census can be selected.
3. **Full-battery walk simulations** (`census_walk_sim.py`, corrected in
   `census_corrected.py`): at the LP-implied tuning depth (~0.006
   diagonal) **no census — mixed or pure — reproduces the d6 depth**
   (all simulate 0.033-0.040 vs 0.0245). A first-pass "exact" d6 match
   by 5+5+5+7+7 was an artifact of annealing the diagonal to its floor
   (0.0023), which exaggerates inheritance; likewise a first-pass claim
   that the echo is partial (φ5 = 0.59 ± 0.18) came from measuring K on
   random stream segments instead of real words — corrected,
   **φ5 = 0.85 ± 0.26**: partial-vs-full echo is undecidable, as
   `d5-partial-alphabet-leak.md` always said. (The printed φ errors are
   LP-binomial only; the K reference carries additional register and
   long-word-truncation systematics — φ6's magnitude is fragile, its
   negative sign is not, since the background is calibration-free.)

## Surviving constraints and open cells

- The d6 deficit requires a tuned relation and is DEEPER than
  adjacent-diagonal tuning delivers at the required rate: either the
  real g's d6-form is separately suppressed (one more designed
  constraint on the key — achievable by selection within the diagonal
  level set, which annealing samples randomly) or d6 is unexplained.
- The d4 lean and the d4−d6 split have no mechanism in any tested
  census; a 4-loop leak with real-word morphology can reproduce d4
  (corrected sim: 0.0417 vs 0.0410) but then fails d6, d8, and d10.
- New key-space filter from the simulations: tuned g's generically
  elevate the g²-diagonal at d2 through consonant/vowel class structure;
  the LP shows no such elevation, so the real g's SQUARE must also have
  a near-background diagonal.
- Annealed diagonal floors are 0.0022-0.0026 for every census tested:
  the doublet tuning is achievable regardless of cycle type.
- Deciding the census question needs better plaintext references than
  runeglish-encoded Gutenberg prose: the mortlach bigram corpus and the
  solved-page words, with errors that include the K systematics.

## Scripts

- `experiments/mixed_cycle_g.py` — φ-ladder inversion, first census
  search, head-to-head simulation (first-pass K, superseded where the
  corrected run differs).
- `experiments/census_scan.py` — exhaustive partition scan.
- `experiments/census_walk_sim.py` — full-battery tuned-walk simulation
  (floor-annealed; superseded on d6 depth).
- `experiments/census_corrected.py` — real-word K, target-level tuning;
  the authoritative numbers where passes disagree.

## Related

- `length-clocked-walk.md` — the architecture this constrains; its d6
  bullet records the same open cells.
- `d5-partial-alphabet-leak.md` — the partial-echo question this arc
  briefly sharpened and then correctly returned to undecidable.
- `word-position-pairs.md` — the position-pair battery that measured the
  staircase.

## Verdict

The mixed-cycle idea produced one theorem, two sharpened anomalies, and
no answer. Established: return ladders cannot produce the d6 dip
(disproving the naive family outright), the d6 suppression is real and
permutation-verified, the d4−d6 split contradicts the pure order-5
symmetry, and the doublet tuning is achievable under any census. Not
established: any particular census — the selection signal is below the
calibration floor of the plaintext references, and the d6 depth exceeds
what tuned-diagonal inheritance explains at realistic tuning. The
within-word profile keeps two open cells (d4 up, d6 down), now with a
much shorter list of surviving explanations: a multi-diagonal-tuned g,
or something outside the cycle-structure family altogether.
