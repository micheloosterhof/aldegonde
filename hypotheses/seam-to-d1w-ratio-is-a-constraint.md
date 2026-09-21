---
type: observation
---
# Observation: The Seam-to-Within-Word Doublet Ratio Is a Constraint the Whole Dodge Family Fails

## The repair that works, and the one that does not

`models-on-the-informative-cells.md` scores the deterministic dodge at 2 of the 5
discriminating cells and shows *how* it fails: d1w at 0.0040 against the corpus's 0.0063,
the seam at 0.0001 against 0.0079. **Over-suppressed, not under** — the rule fires too
reliably. The obvious repair is to let it fire with probability φ.

That helps. At φ ≈ 0.8 the model reaches **3 of 5**, the best score in this directory:

| φ | d1w | seam | seam/d1w | gap_min | d6w | lands |
|---|---|---|---|---|---|---|
| **corpus** | **0.0063** | **0.0079** | **1.25 ± 0.30** | **6.0** | **0.0245** | |
| 0.00 | 0.0165 | 0.0315 | 1.91 | 1.00 | 0.0234 | 1/5 |
| 0.60 | 0.0066 | 0.0146 | 2.21 | 1.72 | 0.0238 | 3/5 |
| 0.80 | 0.0033 | 0.0089 | 2.68 | 4.82 | 0.0236 | **3/5** |
| 0.90 | 0.0017 | 0.0057 | 3.37 | 12.15 | 0.0239 | 3/5 |
| 1.00 | 0.0001 | 0.0031 | 48.34 | — | 0.0239 | 2/5 |

**But d1w and the seam cannot land together.** Fitting d1w at φ ≈ 0.6 overshoots the seam
by a factor of two; fitting the seam at φ ≈ 0.8 undershoots d1w by the same. The ratio
never falls below **1.91**, against the corpus's **1.25 ± 0.30**.

## Why, and why it is not a tuning problem

The two contexts are not alike from the mechanism's point of view.

- **Inside a word** the base is constant, so a would-be repeat needs `g(p_j) = p_{j−1}`.
  It is *schedule-determined*, and the rule's failures are structured.
- **Across a seam** the base has just changed, so a would-be repeat is a chance event at
  roughly 1/29, and the rule's failures are unstructured.

A rule that perturbs the schedule therefore cannot equalise the two rates, whatever φ is.
The corpus does equalise them.

This is the same conclusion `separators-are-the-cipher-unit.md` reaches from the other
direction: sliding every block boundary by a fixed number of runes leaves the doublet rate
unchanged (0.193 against 0.182) while destroying the d5 echo — so **the suppression
belongs to the emitted stream, not to the block schedule**. Two independent measurements,
one conclusion: whatever suppresses repeats does not know where the blocks are.

## Strength

About **two sigma**, and it should be quoted that way. The corpus's ratio rests on 63
within-word doublets and 23 at the seam, giving 1.25 ± 0.30; the family's floor of 1.91 is
2.2 standard errors above it. That is a constraint worth designing against, not a
disproof.

## What it asks of a mechanism

A rule producing the corpus's near-equal rates must inspect **the emitted stream alone**
and act the same way at a seam as inside a word — which the dodge's *trigger* does and its
*failure mode* does not. The direction to look is a rule whose failures are also
context-free: re-emission from a fresh alphabet, a fixed substitution applied on collision,
anything whose residual collision probability is 1/29 in both contexts.

## Status

**Status**: confirmed (measurement, 60 prose corpora per φ). The exclusion is ~2σ and the
structural argument is exact. `experiments/probabilistic_preventer.py`.

## Related

- `models-on-the-informative-cells.md` — the five cells and the scores.
- `separators-are-the-cipher-unit.md` — the boundary-shift result this agrees with.
- `doublet-dodge-walk.md`, `quagmire-dodge.md` — the family constrained.
