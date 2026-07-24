---
type: observation
---
# Observation: Kappa Anomalous Only at Skip 1

## Feature

The coincidence rate (kappa) at skip d is at the random baseline for every
d from 2 to 60, with two exceptions: skip 1 (the doublet deficit, strongly
below) and skip 5 (mildly above -- the lag-5 structure).

## Measurement

`experiments/obs_kappa_spectrum.py` (clean corpus):

| skip | coincidences | z |
|------|--------------|---|
| 1 | 86 | **-17.4** |
| 2 | 441 | -0.32 |
| 3 | 439 | -0.41 |
| 4 | 459 | +0.55 |
| 5 | 479 | +1.52 (lag-5) |
| 6 | 455 | +0.36 |
| 11 | 386 | -2.95 |
| others (to 60) | ~447 | \|z\| < 2 |

Only skip 1 has |z| > 3.

## Significance

The corpus has essentially no periodic or lagged coincidence structure. Skip 1
is the doublet deficit (17 sigma). Skip 5 (+1.5 sigma monographically) is the
foot of the lag-5 paired-match structure, which is significant only in its
PAIRING, not its raw kappa (see `lag5-digraph-structure.md`). Skip 11 (-2.9)
does not survive multiple-testing correction (`lag11-cross-word-deficit.md`).

## Consequences

- Excludes fixed-period polyalphabetic ciphers (a period-L key spikes kappa at
  multiples of L): see `periodic-polyalphabetic.md`.
- Excludes shared/reset keystreams (no kappa at page or section alignment):
  see `page-reset-keystream.md`.
- Localizes ALL adjacency structure to skip 1 plus the weak skip-5 pairing.

## Scripts

- `experiments/obs_kappa_spectrum.py`

## Related

- `doublet-suppression.md` (skip 1), `lag5-digraph-structure.md` (skip 5),
  `lag11-cross-word-deficit.md` (skip 11, not a finding).
