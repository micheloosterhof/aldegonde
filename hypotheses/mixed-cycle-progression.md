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
