---
type: hypothesis
---
# Hypothesis: The Letter Step g Has Mixed Cycle Lengths

## Claim

The within-word coincidence staircase (d2 < d3 < d4 < d5) is the cycle
census of the letter step: `g` has mixed cycle lengths (3-cycles,
4-cycles, 5-cycles, ...), so the fraction of the alphabet that has
"returned" (g^d fixing it) grows with distance — 3-cycles come back at
d3, 4-cycles at d4, 5-cycles at d5 — producing a rising staircase of
partial echoes structurally. This would answer the question "what
classical construction makes correlation RISE with distance": a
progressive substitution disk whose stepping permutation has mixed
loops. It would also make the partial d5 echo (~70% same-alphabet)
structural: four 5-cycles = 20/29 = 69%.

## Status

**Status**: disproved (the d6 cell — no cycle census can produce a
sub-background rate, and the LP's d6 deficit is exactly that)

## Mechanism

Under a random assignment of letters to cycles, the expected within-word
match rate at distance d is

    r_d = φ_d·K_d + (1 − φ_d)·(1 − K_d)/28

with φ_d = (letters in cycles dividing d)/29 and K_d the plaintext
within-word coincidence at distance d. Each observed rate inverts to a
φ_d; the ladder must be realizable by one integer census, which imposes
hard monotonicity: φ of any multiple ≥ φ of its divisors, and φ_d ≥ 0.

## Evidence for

- The inverted ladder fits the rising side well
  (`experiments/mixed_cycle_g.py`, K_d from register prose cut to the LP
  word-length mix): φ2 = 0.06 ± 0.24, φ3 = 0.14 ± 0.11,
  φ4 = 0.30 ± 0.14, φ5 = 0.59 ± 0.18. Small censuses (e.g. 4+5+5+5+6
  + 4 fixed) fit d2-d5 at chi2 ≈ 0.3 where pure order-5 scores 6.8
  (order-5 predicts a FULL d5 echo, φ5 = 1).
- Simulation of the best census reproduces the partial echo: d5 = 0.0514
  vs LP 0.0492 (pure order-5 simulates 0.0623, the full leak).

## Evidence against

- **The d6 cell kills the whole family.** Observed φ6 = **−0.30 ± 0.15**:
  the LP's d6 rate (0.0245) is BELOW the no-return background. A returned-
  fraction ladder is non-negative and monotone over divisors
  (φ6 ≥ max(φ2, φ3)), so NO census fits — every candidate is pulled +3.5
  to +4.4σ at d6, and the best-census simulation gives d6 = 0.0429 vs LP
  0.0245. A sub-background cell cannot come from letters returning; it
  can only come from a TUNED relation returning — which is precisely the
  order-5 signature (g⁶ = g on all non-fixed letters, inheriting the rare
  doublet diagonal at distance 6). The simulation confirms the
  directionality: untuned order-5 gives d6 = 0.0365 (no deficit), so the
  observed deficit specifically requires order-5 WITH the tuned diagonal.
- d8 leans the same way: 4-cycles would return there (best-census sim
  0.0407) and the LP is low (0.0268, weakly significant on its own).

## The prime-loop subfamily (tested July 2026)

Cicada-flavored variant: all loop lengths prime. Scored over the full
d2-d8 ladder, prime censuses are the BEST of the returned-fraction
family — the winner is **5+5+5+7+7** (chi2 11.4 vs 17-22 for composite
censuses and naive order-5), because heavy 5-loops give the partial echo
(15/29 = 52%) and, uniquely, 7-loops predict the weak d7 elevation
(φ7 obs 0.32 ± 0.29). Two cells still kill it. **d4**: the only prime route to a distance-4
return is 2-loops (2×2) — and because the d2 cell is low-power (plaintext
barely repeats at distance 2, K2 ≈ background), 2-loops big enough to
build the observed shoulder (≈9 letters) would indeed hide at d2. But 2
divides 6 too: that same mass returns at d6 at full strength (φ6 ≈ 0.31
vs the observed −0.30 ± 0.15, a ~4σ collision). The d6 veto catches every
route into it — 2-loops, 3-loops, 6-loops — leaving the 4-loop (returns
at 4 and 8, never 6) as the only shoulder-builder, and 4 is composite.
**d6** itself: a loop census can at best reach background while the LP
dips below it (+2.0σ for the no-short-loop censuses, even crediting the
partial g⁶ = g inheritance on their 5-loop letters, which the naive
scorer omits).

The numerologically perfect member — loops **1+2+3+5+7+11 = 29**, one
fixed rune plus the first five primes, landing exactly on the alphabet
size — fits d3 and d7 almost exactly (pulls −0.0 and −0.2, the 3-loop
and 7-loop doing precisely their jobs) but scores chi2 19.4: its single
5-loop makes the d5 echo four times too weak (φ5 = 0.21 vs 0.59 ± 0.18,
and the echo is the corpus's loudest fact), and its 2- and 3-loops
return at d6 where the corpus dips (+3.4σ). Its order (lcm = 2310)
would also void the DJU-BEI abelianization arithmetic that the order-5
walk satisfies. The corpus wants most of the alphabet on 5-loops and
nothing at all returning at 6.

## The d4/d6 asymmetry (new open tension, surfaced by this analysis)

The inheritance algebra cuts against pure order-5 too: under g⁵ = id,
g⁴ = g⁻¹ and g⁶ = g, and the leading-order diagonal rates are the SAME
sum both ways (Σ q(x)q(g(x))). Pure order-5 therefore predicts
**d4 ≈ d6**. Observed: d4 = 0.0410 (elevated), d6 = 0.0245 (suppressed)
— a ~2.7σ split in opposite directions (φ4 = +0.30, φ6 = −0.30,
mirror-symmetric). Something lifts d4 by about as much as something
suppresses d6, and the walk's algebra moves those cells together. This
sits beside the partial-echo tension (`d5-partial-alphabet-leak.md`) as
the second open internal number of the order-5 formulation.

## The order-20 revival: 4×5 + 2×4 + 1 (live, July 2026)

The naive returned-fraction family is dead, but combining loop returns
WITH tuned-diagonal inheritance revives one specific census: **four
5-loops + two 4-loops + one fixed rune** (20 + 8 + 1 = 29, g of order
20). Naively it is already the best census tested (chi2 10.9): φ4 = 9/29
= 0.310 vs the measured 0.30 (exact) and φ5 = 21/29 = 0.724 vs the
original 72% partial-leak point estimate (exact). The refined ledger
(inherited suppression s fitted on d6, tuning attributed to the 5-loop
diagonal) is stronger still:

- **d5 = 0.0488 predicted vs 0.0492 observed** — the partial echo solved
  with a mechanism: at distance 5 the 4-loop letters experience g⁵ = g,
  the TUNED diagonal, so 20 letters echo while 8 anti-echo and 1 leaks.
  The walk's longest-standing unexplained number closes.
- The d4/d6 asymmetry gets a structural source: 4-loops return at d4
  (never at 6), lifting d4 while the 5-loops' inherited suppression digs
  the d6 dip. (A language-side rescue was tested and failed: annealed
  rare-diagonal g's show NO orientation asymmetry on prose — mirror d4
  0.0297 ± 0.0038 vs same-orientation d6 0.0314 ± 0.0045, both mildly
  below background.)
- Residuals: d2 ✓, d3 +0.9, d5 +0.1, d6 fit, d7 +0.9, d8 −1.6, and
  **d4 still +2.8σ** — the 4-loop leak covers ~40% of the d4 surplus.
  One open cell, down from two open numbers.

Costs and open work: g's order becomes 20 (the DJU-BEI abelianization
and every mod-5 phase argument need redoing mod 20); the ledger is
closed-form arithmetic and needs verification by simulating a genuinely
TUNED order-20 permutation through the full battery; and the d1 doublet
channel must re-derive (the fixed rune leaks plaintext doublets:
(1/29)·K1 ≈ 0.0012 of the 0.0063, the rest from the tuned diagonal —
consistent). This subfamily is LIVE and is the current best candidate
refinement of `length-clocked-walk.md`.

## The exhaustive scan (July 2026)

`experiments/census_scan.py` scores ALL 4,565 partitions of 29 under the
refined model (returns leak K_d; g^±1 cells share one fitted suppression
s; 3,310 pass the fixed-point doublet-leak filter, n_fix ≤ 5). Findings:

- **Consistent fits exist**: the leader (7+5+5+5+4 + 3 fixed) scores
  chi2 = 7.0 on ~6 df, p ≈ 0.32. The within-word profile is fully
  explainable by cycle structure + inheritance.
- **Robust demands shared by every good fit**: three-to-four 5-loops
  (partial echo), exactly one 4-loop-ish part (d4), NOTHING returning at
  2, 3, or 6 (the d6 dip), few fixed points.
- **A 7-loop appears in all top-15** — but only because of the d7 cell,
  which is +0.9σ; discounting it, the leader, the 4×5+2×4+1 census
  (rank 28, chi2 10.3), and 5+5+5+7+7 (rank 35) are statistically
  indistinguishable (Δchi2 ≈ 3 at this model fidelity).
- **The standard five-5-loops + 4-fixed census ranks 266th**
  (chi2 17.0, Δ ≈ 10 vs the mixed family), failing at d5 (full echo,
  +2.3) and d6 (+2.4). Under this model the data prefer a
  partial-echo cycle type — the constraint in `g-from-5x5-grid.md`
  ("five 5-cycles") should be treated as provisional pending the
  simulation test of the mixed family.

## The simulation verdict: 5+5+5+7+7 (July 2026)

`experiments/census_walk_sim.py` runs the promotion test: annealed
tuned-diagonal g (conjugation moves, census-preserving), full walk on
register plaintext in the LP word structure, complete battery. Result —
the live candidate is **three 5-loops + two 7-loops** (all prime, order
35, the UNIQUE partition of 29 into 5s and 7s):

| | d1 | d2 | d3 | d4 | d5 | **d6** | d7 | d8 | d9 | d10 |
|---|---|---|---|---|---|---|---|---|---|---|
| LP | .0063 | .0347 | .0370 | .0410 | .0492 | **.0245** | .0421 | .0268 | .0260 | .0227 |
| 5+5+5+7+7 | .0027 | .0425 | .0360 | .0304 | .0483 | **.0245** | .0494 | .0279 | .0295 | .0379 |
| 4×5+2×4+1f | .0023 | .0442 | .0353 | .0391 | .0466 | .0343 | .0339 | .0465 | .0269 | .0720 |
| 5×5+4f | .0024 | .0399 | .0392 | .0260 | .0602 | .0287 | .0347 | .0380 | .0312 | .0691 |

Why it wins: 6 ≡ 1 (mod 5) and 6 ≡ −1 (mod 7), so at distance 6 EVERY
letter sits on the tuned diagonal — the only census that produces the
full d6 dip (exactly), while its 15 five-loop letters give the partial
d5 echo and its 7-loops explain the d7 elevation and the d8/d9 dips
(g⁸ = g on 7-loops). The 4-loop census dilutes d6 (its 4-loops are
untuned there) and leaks wrongly at d8/d10; the standard census
overshoots d5 (full echo) and underscoops d6 (fixed-point leak).

Remaining residuals and new constraints from the simulation:

- **d4 is still unexplained under every census** (sim 0.0304 vs LP
  0.0410, ~+3σ). It is now THE open cell of the within-word profile.
- **All tuned sims overshoot d2** (+0.005-0.010): annealing the
  g-diagonal through same-class rare bigrams makes the g²-diagonal
  elevated at distance 2 (CVCV rhythm), which LP does not show. The real
  key therefore needs its SQUARE's diagonal near background as well — a
  new key-space filter (and partly an artifact of over-annealing: the
  sims reached 0.0023-0.0026 where LP needs only ~0.005).
- d10 predicts a partial echo return (0.038) vs LP's thin 0.0227 —
  a weak lean against, low power.
- Annealed diagonal floors are 0.0022-0.0026 for every census tested:
  the tuning requirement is achievable regardless of cycle type.
- The seam and d1 rows are not discriminators here (random σ, deliberate
  over-annealing); doubled-rune identities stay uniform in all sims
  (base-scrambling covers the fixed-point leak channel).

If 5+5+5+7+7 holds, `length-clocked-walk.md`'s g has order 35, all
mod-5 phase arguments generalize to mod 35, and the DJU-BEI arithmetic
must be redone in the new abelianization (the σ-even parity condition
survives unchanged: 4946 is even).

## CORRECTION (same day): the crowning was premature

Review of the first pass found two calibration flaws
(`experiments/census_corrected.py`): (1) K_d had been measured on prose
cut into LP word lengths at RANDOM offsets — arbitrary segments whose
statistics approach the unconditional stream coincidence, inflating
K3-K5 by ~10-15%; (2) the diagonals were annealed to their floors
(0.0023) where the LP implies ~0.006, and the d6 dip depth scales with
tuning depth. Redone with real prose words sampled by length and
target-level tuning:

- **The partial-echo evidence largely evaporates**: corrected
  φ5 = 0.85 ± 0.26, consistent with the full echo (−0.6σ). The original
  `d5-partial-alphabet-leak.md` verdict — underpowered, likely
  undecidable — was correct; the first-pass φ5 = 0.59 ± 0.18 was a
  calibration artifact.
- **The census rankings are calibration-fragile**: 5+5+5+7+7 falls to
  rank 14, the standard 5×5+4f census recovers to rank 67, and the gap
  between the mixed family and pure order-5 shrinks to Δchi2 ≈ 3 —
  within the systematic uncertainty of the K reference (register,
  long-word truncation). No census is crowned.
- **At realistic tuning depth NO census reproduces the deep d6 dip**:
  corrected sims give d6 = 0.033-0.040 for every census (including
  5+5+5+7+7) vs LP 0.0245. The "exact d6 match" of the first pass was
  the over-annealing knob. Inheritance at the LP-implied diagonal level
  is ~2σ too shallow; the d6 deficit is either an ADDITIONAL tuning
  constraint on the real g (its d6-form must be suppressed beyond what
  T1-tuning alone delivers — a designed key can do this; a random member
  of the T1 level set does not) or unexplained.
- One positive from the corrected sims: with real-word morphology the
  4×5+2×4+1 census reproduces d4 exactly (0.0417 vs 0.0410) via its
  4-loop leak — but fails d6, d8, and d10.

**Corrected bottom line**: the within-word profile's two calibration-free
anomalies — d4 elevated (+2σ above background) and d6 depressed (−2σ
below background) — are both real and NEITHER is explained by any tested
cycle census at realistic tuning. The cycle-type question is OPEN, with
sharpened constraints: pure return ladders are still dead
(monotonicity), pure order-5 still needs a source for d4, and any mixed
census still needs a source for the d6 depth. Better plaintext
references (the mortlach bigram corpus, solved-page words) are needed
before the φ ladder can decide anything at the ±0.1 level.

## What survives the disproof

- The φ ladder itself is a useful measurement. For order-5, φ5 should be
  1.0 (full echo); the inverted estimate 0.59 ± 0.18 restates the
  partial-echo tension (`d5-partial-alphabet-leak.md`) with slightly
  more power — ~2.3σ from full — subject to the register-calibration
  caveat on K_d (prose proxy, not LP plaintext).
- The d4 shoulder (φ4 = 0.30 ± 0.14 vs order-5's fixed-point prediction
  0.14) is a mild +1.2σ lean, not evidence.
- The conceptual answer stands: the classical construction with
  correlation RISING in distance is mixed-cycle progression; the LP's
  sub-background d6 is the fingerprint distinguishing "more of the
  alphabet returns" (mixed cycles — refuted) from "the same tuned
  relation returns" (order-5 — supported). The d6 deficit is thereby
  promoted from a curiosity to a structural argument FOR g⁵ = id with a
  tuned diagonal.

## Predictions

- (Made and already failed:) d6 and d8 elevated by the returning short
  cycles. Observed: both at or below background.

## Scripts

- `experiments/mixed_cycle_g.py` — the φ-ladder inversion, census search,
  and head-to-head simulation.

## Related

- `length-clocked-walk.md` — the surviving order-5 formulation; the d6
  deficit is now positive structural evidence for it.
- `d5-partial-alphabet-leak.md` — the partial-echo tension the φ ladder
  restates.
- `word-position-pairs.md` — the position-pair battery that measured the
  staircase this hypothesis tried to explain.

## Verdict

Disproved by monotonicity: returned-fraction ladders cannot go below
background, and the LP's d6 does. The staircase's rising side is real
and partially unexplained under pure order-5 (the partial echo remains
the open tension), but its falling side — the d6 deficit — is a
structural signature of an order-5 step with a tuned diagonal, and rules
out mixed cycle types along with every "more of the alphabet returns"
reading.
