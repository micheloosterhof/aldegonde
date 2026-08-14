---
type: observation
---
# Observation: Off-Diagonal Bigrams are Uniform

## Feature

The bigram (digraph) distribution has no structure except the suppressed
diagonal. The raw bigram IoC is mildly elevated, but that elevation is entirely
the doublet deficit -- the off-diagonal cells are flat.

## Measurement

`experiments/obs_bigram_ioc.py` (clean corpus, 12,955 bigrams):

| quantity | value |
|----------|-------|
| normalized bigram IoC | 1.0256 (elevated vs 1.0) |
| off-diagonal cells (812) chi-square | 841, 811 df, **p = 0.22** |

## Significance

The +8 sigma raw bigram-IoC elevation vs a plain-uniform null is a TRAP: it is
produced entirely by the missing diagonal (doublet suppression), not by
language. Excluding the 29 diagonal cells, the 812 off-diagonal cells are
uniform (p = 0.22). So the only bigram-level structure in the corpus is the
doublet deficit; there is no digraph-frequency signal of the kind Playfair,
bifid, or language would leave.

**Methodological note**: any null for this corpus MUST include the doublet
rate. A plain-uniform null manufactures fake anomalies here, in isomorphs,
in trigram repeats, and in the seam pair-IoC (`seam-channel-clean.md`) --
the four faces of the "doublet-suppression trap".

## Full battery (July 2026)

`experiments/full_bigram_battery.py` runs the complete matrix analysis
against the library's `doublet_shuffle` null at the observed rate (400
surrogates, real word structure overlaid). Every statistic is flat:

| statistic | observed | null | z |
|---|---|---|---|
| off-diagonal chi2 (812 cells) | 784.5 | 757.6 ± 37.3 | +0.7 |
| max per-cell z | +3.50 | +3.38 ± 0.41 | +0.3 |
| min per-cell z | −2.82 | −2.71 ± 0.24 | −0.5 |
| antisymmetry chi2 (M[a][b] vs M[b][a]) | 426.3 | 380.3 ± 26.6 | +1.7, see note |
| within-word vs cross-word homogeneity | 777.8 | 805.8 ± 36.9 | −0.8 |
| mean successor split nIoC (per predecessor) | 1.026 | 1.023 ± 0.003 | +0.8 |
| mean predecessor split nIoC (per successor) | 1.025 | 1.023 ± 0.003 | +0.7 |
| phase homogeneity (bigrams by within-word position) | 888.4 | 870.8 ± 35.3 | +0.5 |

Notes: the antisymmetry row reads p = 0.23 under the analytic chi-square
(≈406 df, `deep_scan.py`); the +1.7 against surrogates reflects a slight
symmetrizing bias in the `doublet_shuffle` placement algorithm rather than
the data — asserted, not tested; the analytic chi-square is a different
test and does not discriminate the two. The null's own successor-split mean (1.023, not 1.000) is the
doublet artifact baseline — the observed 1.026 depth-1 split sits on it,
confirming the documented reading. The top cell (ᚷᛚ = 30 vs 15.4
expected, z = +3.5) is exactly the extreme 812 cells produce by chance
(null max +3.38 ± 0.41).

Two statements this battery makes for the first time at full power:
**boundary-blindness extends to the whole matrix** — the within-word and
cross-word off-diagonal bigram distributions are statistically identical
(z = −0.8), not just their diagonals — and **the bigram table is
homogeneous across within-word positions** (phase strata z = +0.5), so
no position-dependent digraph structure exists for any phase-keyed
mechanism to leave.

## Consequences

- Excludes Playfair and grid-fractionation (they leave characteristic bigram
  patterns): see `playfair-variant.md`, `bifid-fractionation.md`.
- Confirms there is no pairwise structure beyond lag-1: see
  `pairwise-dependence.md`.

## Scripts

- `experiments/obs_bigram_ioc.py` — raw IoC + off-diagonal uniformity.
- `experiments/full_bigram_battery.py` — the July 2026 full battery
  (matrix, antisymmetry, boundary and phase decompositions, splits).

## Related

- `doublet-suppression.md` — the diagonal deficit that lifts the raw IoC.
- `explicit-doublet-avoidance.md` — the difference-class marginal
  (`experiments/obs_delta_offset_marginal.py`), the class-pooled projection
  of this matrix; flat too, closing spread deterministic repair rules the
  per-cell chi-square is underpowered for.
