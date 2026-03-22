# Hypothesis: Explicit Doublet Avoidance (Post-Processing)

## Claim

The cipher produces doublets at a normal rate, but a post-processing step
replaces or shifts doublets to suppress them.

## Status

**Status**: disproved

## Mechanism

After encryption, any adjacent repeated rune pair (doublet) is detected and
"fixed" by incrementing the second rune, swapping it, or applying some other
local transformation. This would reduce the doublet rate without changing the
underlying cipher.

## Evidence for

- Would be a simple way to achieve doublet suppression on top of any cipher
- The zero-triplet observation is consistent (post-processing would catch them)

## Evidence against

- **Geometric doublet spacing**: The spacings between doublets follow a
  geometric distribution, which is the signature of independent random events
  with probability p ~= 0.0068. A post-processing rule that "fixes" doublets
  would produce a different spacing distribution: the minimum spacing would be
  anomalous (no closely-spaced doublets), and the distribution would deviate
  from geometric.
- **Doublets are natural**: The 89 observed doublets behave as if they arise
  naturally from the cipher mechanism, not as residual errors that slipped
  through a filter.

## Scripts

- `experiments/lp_deep_analysis.py` — Analyzes doublet spacing distributions.

## Verdict

Disproved. The geometric spacing distribution of doublets indicates they are
natural products of the cipher mechanism, not artifacts of post-processing.
