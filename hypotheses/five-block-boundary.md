# Hypothesis: Five-Block Cipher with Edge Effects

## Claim

The cipher processes the text in (possibly phase-drifting) units of five
runes. Within a unit, consecutive outputs are forced distinct; across unit
boundaries there is no constraint. Key material at unit edges (first/last
position) is occasionally reused across consecutive units.

## Status

**Status**: unresolved

## Mechanism

A generator produces key material in rounds of five. Two consequences:

1. **Doublets**: forbidden inside a round (4/5 of adjacencies), natural at
   the 1/29 collision rate across boundaries (1/5 of adjacencies). Predicted
   rate (1/5)(1/29) = 0.690%; observed 0.664% (z = -0.36, parameter-free).
2. **Lag-5 matches**: if edge key values (positions 0 and 4 of a round) are
   occasionally carried over or reused between consecutive rounds, lag-5
   ciphertext matches cluster at unit edges. Match pairs then occur as
   either both edges of one unit — text separation 4 — or the two positions
   flanking a boundary — text separation 1. This reproduces the observed
   selective d=1/d=4 structure (`lag5-digraph-structure.md`) with roughly
   equal counts (observed 29 vs 28), and predicts occasional (1,4)/(4,1)
   gap chains, which are present (3+ observed vs <1 expected).

This is the only mechanism shape found so far that produces all three
appearances of the constant 5 — doublet acceptance 1/5, lag-5 edge
coupling, and the 5-position dead time after doublets — from a single
design element.

## Evidence for

- Parameter-free doublet rate fit: (1/5)(1/29), z = -0.36.
- Kappa at skips 2, 3, 4 is exactly normal (441/439/459 vs 447 expected):
  only ADJACENT positions are constrained. This kills the stronger
  "all five outputs distinct per round" variant (which would suppress
  skip-2..4 coincidences by 60%) but exactly matches consecutive-distinct.
- Lag-5 match-pair structure at separations 1 and 4 only, with ~equal
  excess, matching the two edge-pair geometries.
- Cooldown likelihood fit: doublet gaps prefer "5-position dead time +
  memoryless" over pure memoryless by a likelihood ratio of ~18 (and the
  minimum observed gap is 6).
- Gap-5 deficit: strictly periodic boundaries predict ~3.1 doublet pairs at
  gap exactly 5 (consecutive boundaries both colliding); observed 0
  (p ~= 0.045) — consistent with a boundary interaction (e.g. a round
  refill triggered by an emitted doublet), which is also what the dead-time
  fit suggests.

## Evidence against

- No positional mod-5 lattice anywhere: doublet positions and gaps are flat
  mod 5, and lag-5 events have no phase. Fixed-phase periodic blocks are
  excluded; the units must drift, reset frequently (faster than the ~150
  mean doublet gap), or be stochastic. A stochastic "1-in-5 adjacencies
  unconstrained" variant is observationally identical to memoryless 1/5
  acceptance for doublets, but then the lag-5 edge structure needs the
  block framing anyway — a tension the hypothesis must resolve.
- No track-space structure: the 5 interleaved tracks (i mod 5) are
  individually flat with no autokey signal, and the lag-5 match rate is
  uniform across phases — consistent with drifting units, but offering no
  positive confirmation.
- No algebraic relation found inside the d1/d4 events (anchor values,
  B-A deltas, and middle-position deltas all uniform).

## Predictions

- Doublet gaps of exactly 5 should remain absent as more text is analyzed
  (strict periodic version) or appear at a suppressed rate.
- If unit phase is locally stable over short ranges, nearby lag-5 event
  pairs should show consistent relative phase; measuring phase coherence
  length could localize the reset trigger (word? line? doublet emission?).
- A simulated implementation (5-round keystream, consecutive-distinct
  outputs, edge carryover at a tunable rate, phase reset on some trigger)
  should reproduce doublet rate, dead time, AND the d1/d4 shape
  simultaneously. Building this simulator is the direct next step.

## Scripts

- `experiments/unit5_telex_tests.py` — rate fit, phase frames, cooldown.
- `experiments/lag5_digraph_chase.py` — the d1/d4 structure.
- `experiments/mechanism_fingerprint.py` — harness for the simulator test.

## Related

- `stream-cipher-no-repeat.md` — the memoryless-avoidance reading of the
  same doublet statistics; this hypothesis is its structured competitor.
- `lag5-digraph-structure.md` — the structure this mechanism is built to
  explain.
- `bifid-fractionation.md` — disproved block-of-5 alternative.

## Verdict

Unresolved. Currently the only single-mechanism explanation for all three
independent appearances of the constant 5 in the fingerprint. Needs a
concrete simulator implementation to test whether one parameter setting can
hit the full fingerprint, and a phase-coherence measurement to constrain
the unit reset rule.
