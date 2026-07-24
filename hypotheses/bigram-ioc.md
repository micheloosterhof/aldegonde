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
rate. A plain-uniform null manufactures fake anomalies here, in isomorphs, and
in trigram repeats -- the three faces of the "doublet-suppression trap".

## Consequences

- Excludes Playfair and grid-fractionation (they leave characteristic bigram
  patterns): see `playfair-variant.md`, `bifid-fractionation.md`.
- Confirms there is no pairwise structure beyond lag-1: see
  `pairwise-dependence.md`.

## Scripts

- `experiments/obs_bigram_ioc.py` — raw IoC + off-diagonal uniformity.

## Related

- `doublet-suppression.md` — the diagonal deficit that lifts the raw IoC.
