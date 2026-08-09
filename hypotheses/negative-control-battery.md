---
type: observation
---
# Negative-Control Battery: Which Measurements Survive a Structureless Corpus

## Status

**Status**: confirmed (characterization) — tooling plus its first pass. Two
standing claims are corrected by it.

## Why

Every statistic here is quoted against some null, and when the null is wrong
the statistic manufactures signal. This project has produced several:

- a plain shuffle made the corpus look underdispersed at z = −5.7
  (`cross-product-sum-flat.md`);
- a naive standard error turned a p = 0.034 section effect into z = +53;
- a linearised model prediction created the d4/d6 "puzzle" and drove a year of
  census work (`d4-d6` correction in `mixed-cycle-progression.md`);
- a seam tap read z = +1.33 until a random control showed that was the noise
  floor (`word-level-autokey.md`).

Four of those five would have been caught by a control. So the fix is
systematic: run the identical pipeline over a corpus known to carry nothing.

## The surrogate

`experiments/negative_control_battery.py` keeps the real text's word
boundaries, sentence marks, line wraps and page breaks **exactly**, and
replaces only the rune values, drawn with `c3301.low_doublet_null()` so the
observed doublet rate is preserved too.

It therefore holds fixed everything the layout and the doublet constraint
supply, and removes everything else. A measurement that separates the real
corpus from this surrogate is seeing something beyond boundaries and doublets;
one that does not, is not.

| measurement | real | surrogate | sd | z |
|---|---|---|---|---|
| unigram IoC ×29 | 0.9999 | 0.9999 | 0.0000 | — |
| doublet rate | 0.0066 | 0.0068 | 0.0007 | −0.29 |
| within-word d1 | 0.0063 | 0.0069 | 0.0008 | −0.72 |
| within-word d4 | 0.0410 | 0.0346 | 0.0029 | +2.18 |
| **within-word d5** | 0.0492 | 0.0348 | 0.0042 | **+3.45** |
| within-word d6 | 0.0245 | 0.0340 | 0.0052 | −1.83 |
| cross-word d5 | 0.0347 | 0.0343 | 0.0016 | +0.24 |
| **lag-5 pairs, separation 1** | 29 | 15.8 | 4.3 | **+3.10** |
| **lag-5 pairs, separation 4** | 28 | 15.1 | 3.9 | **+3.26** |
| seam doublets | 23 | 19.7 | 4.6 | +0.72 |
| line-initial chi2 | 81.4 | 27.8 | 7.2 | +7.43 |
| 3-rune full agreement | 17 | 11.2 | 3.4 | +1.70 |

## What survives

- **The d5 echo** (z = +3.45). Real, and the strongest within-word cell.
- **The lag-5 paired structure** at separations 1 and 4 (z = +3.10, +3.26).
  Both survive.
- **Line-initial bias** (z = +7.43) — but discriminating is not the same as
  cipher structure. `line-initial-bias.md` already attributes this to
  typography, and the solved pages show the same effect.

Rows that cannot discriminate by construction are not failures: the doublet
rate and within-word d1 are matched by the surrogate on purpose, and
cross-word d5 is known to sit at chance.

## What it corrects

**1. The seam carries nothing, not "exactly one structure".**
`seam-channel-clean.md` headlined the 23 cross-word doublets at z = −8.1. That
null permutes word order, which destroys the doublet suppression along with the
seam pairing and sends the expectation to an unsuppressed 100.7. Against a
doublet-preserving surrogate the seam diagonal is **z = +0.72** — nothing. This
also resolves a contradiction: `word-level-autokey.md` already recorded that
the suppression is boundary-blind (within-word 0.0063 vs seam 0.0079, one rate
at z = 0.87) while `seam-channel-clean.md` still treated the diagonal as a
finding. Corrected there.

**2. The d6 deficit is null-dependent.** `mixed-cycle-progression.md` calls
d6 "the solid anomaly" at permutation p = 0.016. That null shuffles word
*lengths* and keeps the runes, asking whether the real boundaries know where
the coincidences are. This surrogate shuffles the *runes* and keeps the
boundaries, and gives **z = −1.83** — under 2 sigma. The two nulls answer
different questions and neither is wrong, but "solid" overstates a cell that
fails to clear one of them. Consistent with `d4_d6_prediction.py`, which showed
the d6 depth is fully reachable by a tuned order-5 g.

**3. Self-check.** The 3-rune full-agreement excess reads +1.70, confirming the
+1.85 reported in `two-rune-depth-no-base-reuse.md` as noise rather than a
lean.

## Limits

- Rune shuffling leaves word lengths untouched, so this cannot test the
  short-word deficit, sentence-final lengths, or anything computed from
  boundaries alone. Those need a length-sequence surrogate — the approach
  `within_word_phase_profile.py` already uses.
- The surrogate destroys *all* rune structure, so it is a strong null. Failing
  to discriminate against it means a measurement's signal is explained by
  boundaries plus the doublet rate — not that the measurement is worthless.
- z here is against the surrogate spread only; it carries no correction for
  the twelve measurements scanned.

## Scripts

- `experiments/negative_control_battery.py`

## Related

- `seam-channel-clean.md`, `mixed-cycle-progression.md` — corrected by this.
- `within-word-d5-coincidence.md`, `lag5-digraph-structure.md` — confirmed by it.
- `cross-product-sum-flat.md` — the plain-shuffle artifact that motivated it.

## Verdict

The d5 echo and the lag-5 pairing are the two rune-level findings that survive
a structureless corpus. The seam diagonal does not, and the d6 deficit clears
only one of two reasonable nulls. Any new rune-level claim should be run
through this before it is written up.
