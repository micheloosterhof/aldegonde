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

## What survives — corrected by the family-blind sweep

The table above has the same flaw the audit exists to catch: it applies the
control only to cells this repo already treats as findings. A control run on
pre-selected cells cannot say whether those cells are special, and cannot see
a cell nobody looked at. `experiments/negative_control_grid.py` therefore
sweeps the whole grid — within-word d1..d12, plus lag-L match pairs at
separation s for L = 2..15 and s = 1..8, 124 cells — and corrects each family
against the largest |z| the **surrogate** produces over the same family.

| family | cells | real max &#124;z&#124; | surrogate max | p |
|---|---|---|---|---|
| within-word d1..d12 | 12 | **3.47** (d5) | 1.98 ± 0.58 | **0.020** |
| lag-pair grid | 112 | 3.28 (lag5 sep4) | 2.85 ± 0.50 | 0.203 |
| both pooled | 124 | 3.47 | 2.91 ± 0.50 | 0.143 |

- **The d5 echo survives.** It is the largest cell in its own family and clears
  a family-blind correction over all twelve within-word distances at p = 0.020.
  This is the one rune-level finding that holds up to everything asked of it.
- **The lag-5 pairing does not clear a family-blind scan.** Per-cell it reads
  z = +3.20 and +3.28, but that is uncorrected. Asking instead whether any
  *lag* is special — aggregating z² over its eight separations — lag 5 leads
  easily (22.6 against 9.7 for the runner-up, lag 11) yet the surrogate's own
  best lag reaches 17.1 ± 5.0, giving **p = 0.11**. This is consistent with
  the repo's own note that the pairing runs p ≈ 0.01 on the hand-picked {1,4}
  pattern and p ≈ 0.033 family-blind; it is marginal, not established.
  (Aggregating all eight separations is conservative for a structure that
  really sits only at {1,4}, so 0.11 is a floor, not a verdict.)
- **Line-initial bias** (z = +7.43) — but discriminating is not the same as
  cipher structure. `line-initial-bias.md` already attributes this to
  typography, and the solved pages show the same effect.

Pooling all 124 cells is too blunt: the two families ask different questions
and 112 of the cells are lag-pair statistics nobody ever proposed, which
inflates the threshold against a genuine finding.

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

- `experiments/negative_control_battery.py` — the named measurements.
- `experiments/negative_control_grid.py` — the family-blind sweep and the
  per-family scan correction. Run this before writing up any new cell.

## Related

- `seam-channel-clean.md`, `mixed-cycle-progression.md` — corrected by this.
- `within-word-d5-coincidence.md` — confirmed by it.
- `lag5-digraph-structure.md` — its pairing does NOT clear the family-blind
  sweep here; see the caveat above.
- `cross-product-sum-flat.md` — the plain-shuffle artifact that motivated it.

## Verdict

**The d5 echo is the only rune-level finding that survives everything** — a
structureless surrogate and a family-blind correction over all twelve
within-word distances (p = 0.020).

The lag-5 pairing does not clear a family-blind scan (p = 0.11-0.20 depending
on how the family is drawn), the seam diagonal vanishes entirely against a
doublet-preserving null, and the d6 deficit clears only one of two reasonable
nulls. Any new rune-level claim should be run through the grid before it is
written up, and quoted with the family it was drawn from.
