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
- **The difference-class marginal is flat, closing SPREAD repair rules**
  (`experiments/obs_delta_offset_marginal.py`): a partial rule parking the
  ~361 displaced events on a set S of offsets loads the classes
  (c_j - c_{j-1}) mod 29 = s in S. Observed max per-class |z| is 2.64,
  family-blind p = 0.20 under three nulls (global shuffle, within-section
  shuffle, doublet-preserving); planted rules at the matched 0.66% doublet
  rate read max |z| 17.2 / 8.7 / 5.5 / 4.3 for |S| = 1 / 2 / 4 / 8. So any
  shared-offset rule up to |S| ~ 8 is excluded. A prev-DEPENDENT rule
  s(prev) instead loads 29 scattered cells at per-cell z ~ +3.2, which
  would lift the battery's off-diagonal chi2 by ~+8 sigma (observed +0.7,
  `bigram-ioc.md`) — also excluded. Watch-item, not signal: the 28-class
  chi2 is mildly overdispersed (41.4 on 27 df, p ~ 0.035 uncorrected,
  identical under all three nulls, no responsible class). This is the same
  number `per-word-related-alphabets.md` already carries as its "d1-delta
  residual" soft observable; what this experiment adds is the per-class
  bands and the planted power curve, not the residual itself.
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
- `experiments/obs_delta_offset_marginal.py` — difference-class marginal with
  planted-rule power curve; closes partial deterministic rules spread over
  up to ~8 offsets, and prev-dependent rules via the bigram battery.

## Verdict

Disproved for deterministic repair rules, full or partial: a full rule
predicts a ~0% doublet rate, and a partial rule must park the displaced
mass either in shared offset classes (flat marginal, planted power to
|S| ~ 8) or in prev-dependent cells (flat battery chi2). Neither is
observed. What survives is redistribution indistinguishable from uniform —
a stochastic re-draw or a key-state-driven replacement, observationally
equivalent to emission-time avoidance and tracked as
`stream-cipher-no-repeat.md`, not disproved by this file.
