---
type: observation
---
# Observation: No Pairwise Dependence Except Lag 1

## Feature

The full 29x29 contingency table of (C[i], C[i+d]) is at chance for every lag
d = 2..100; only d=1 (the doublet diagonal) shows dependence.

## Measurement

`experiments/obs_dependence.py` (clean corpus), chi-square vs independence,
784 df:

| lag | chi2 | z |
|-----|------|---|
| 1 | 1115 | **+7.4** (doublet diagonal) |
| 2 | 778 | -0.1 |
| 3-10 | 750-843 | \|z\| < 1.5 |
| 11-100 | — | worst \|z\| = 2.4 (lag 80), under the 100-lag Bonferroni bar ~3.3 |

## Significance

The ONLY pairwise structure at any distance is the lag-1 doublet diagonal. No
lag carries a hidden bigram dependency, which excludes lagged-feedback ciphers
whose relation would surface as off-diagonal contingency structure. (The lag-5
anomaly is NOT a pairwise-dependence effect -- it is a higher-order pairing of
coincidences, invisible to this test; see `lag5-digraph-structure.md`.)

## Consequences

- Excludes lagged ciphertext autokey at every depth (`ciphertext-autokey.md`).
- Bounds any bounded-context inner layer (`autokey-plus-substitution.md`).

## Scripts

- `experiments/obs_dependence.py`

## Related

- `kappa-spectrum.md`, `bigram-ioc.md`.
