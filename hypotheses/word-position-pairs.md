---
type: observation
---
# Characterization: Within-Word Position Pairs Carry Distance-Only Structure

## Claim

The full grid of within-word position pairs — first rune vs second, first
vs third, ..., every (j, k) with enough samples — contains no structure
beyond the known DISTANCE profile (d1 suppressed, d2-d4 rising shoulder,
d5 echo, d6 suppressed). Match rates are translation-invariant (the same
at every absolute position for a fixed distance) and there is no
conditional structure (the rune at position k is independent of the
IDENTITY of the rune at position j at every distance, beyond the equality
channel). This is exactly the walk's prediction: c[j] =
base_w(g^(j mod 5)(p[j])) makes every position-pair relation a function
of k − j alone.

## Status

**Status**: confirmed (characterization)

## What was measured

Clean corpus, 2,928 words; null = `aldegonde.stats.nulls.doublet_shuffle`
at the observed rate, 300 surrogates, real word structure overlaid
(`experiments/word_position_pairs.py`).

- **Per-cell grid (36 cells with ≥ 150 samples, positions 1-10)**: max
  |z| = 3.3 at cell (5,9) — a d=4 cell, the strongest of 36 in the known
  shoulder distance; the within-d4 translation-invariance test puts it at
  p = 0.13. Every other cell |z| ≤ 1.9.
- **Pooled per-distance rates** independently reproduce the documented
  profile: d1 z = −0.7 (the suppression, mostly absorbed by the null),
  d2 −0.4, d3 +0.8, d4 +2.1 (shoulder), **d5 +3.6 (echo)**, d6 −1.7
  (the phase-1 suppression), d7 +0.9, d8 −0.6.
- **Translation invariance** (chi2 across absolute position at fixed
  distance): flat at every distance — d1 through d7 all |z| ≤ 1.2,
  p(hi) ≥ 0.13. The echo is the same in positions (1,6), (2,7), (3,8),
  (4,9); no intra-word drift (consistent with
  `within_word_position_decomposition.py`).
- **Conditional splits** (mean nIoC of the rune at k grouped by the rune
  at j): flat at every distance, |z| ≤ 1.5; the d1 value sits on the
  doublet-artifact baseline the null itself shows (1.022 vs 1.023).

## Consequences

- The within-word channel is exhaustively characterized: everything
  reduces to the distance profile, which the walk family reproduces.
  There is no absolute-position keying, no positional alphabet change,
  and no identity coupling between positions — nothing for a
  position-keyed or progressively-keyed-within-word mechanism to have
  left behind.
- Together with `bigram-ioc.md` (full adjacency battery),
  `seam-channel-clean.md` (the boundary channel to depth 6), and
  `pairwise-dependence.md` (global lags 2-100), every first-order
  channel of the corpus is now closed: the corpus's residual information
  lives strictly above pairwise order.

## Scripts

- `experiments/word_position_pairs.py` — reproduces every number above.

## Related

- `within-word-d5-coincidence.md`, `lag5-digraph-structure.md` — the
  distance profile this grid decomposes.
- `position-within-word.md` — the disproved additive positional family;
  this census closes the observational side generally.
- `seam-channel-clean.md`, `bigram-ioc.md` — the companion batteries.

## Verdict

Confirmed characterization. Within words, only distance matters: the
(j, k) grid is translation-invariant, conditionally structureless, and
fully accounted for by the known d1-d6 profile. A clean, full-power
verification of the walk's central structural claim.
