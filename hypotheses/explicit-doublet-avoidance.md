---
type: hypothesis
---
# Hypothesis: Explicit Doublet Avoidance (Post-Processing)

## Claim

The cipher produces doublets at a normal rate, but a post-processing step
replaces or shifts doublets to suppress them.

## Status

**Status**: disproved (deterministic local fixes; a stochastic partial
re-draw is observationally equivalent to emission-time avoidance, tracked
in `stream-cipher-no-repeat.md`)

## Mechanism

After encryption, any adjacent repeated rune pair (doublet) is detected and
"fixed" by incrementing the second rune, swapping it, or applying some other
local transformation. This would reduce the doublet rate without changing the
underlying cipher.

## Evidence for

- Would be a simple way to achieve doublet suppression on top of any cipher
- The zero-triplet observation is consistent (post-processing would catch them)

## Evidence against

- **Deterministic fixes leave fingerprints that are absent**: an
  increment/swap rule applied to every doublet would drive the rate to ~0
  (observed 0.66%) and inflate specific repair bigrams such as (c, c+1) —
  but the off-diagonal bigram matrix is uniform (`bigram-ioc.md`, chi-sq
  p=0.23) and the doublet spacing stays geometric.
- **A stochastic partial fix is not excluded — it is a reformulation**: a
  post-processor that re-draws ~80% of doublets is a memoryless thinning of
  doublet events, observationally near-identical to avoiding them at
  emission time. The spacing and bigram statistics cannot distinguish the
  two. That mechanism is not disproved here; it is the open
  `stream-cipher-no-repeat.md`.
- **Doublets are natural**: The observed doublets (86 in the clean corpus)
  behave as if they arise
  naturally from the cipher mechanism, not as residual errors that slipped
  through a filter.

## Scripts

- `experiments/lp_deep_analysis.py` — Analyzes doublet spacing distributions.

## Verdict

Disproved for deterministic repair rules (increment/swap/local transform):
they predict either a ~0% doublet rate or repair-bigram structure, and
neither is observed. The stochastic partial-re-draw variant is
observationally equivalent to emission-time doublet avoidance and is
tracked as `stream-cipher-no-repeat.md`, not disproved by this file.
