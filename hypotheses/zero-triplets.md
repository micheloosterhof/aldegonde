---
type: observation
---
# Observation: Zero Triplets

## Feature

No run of three equal runes (`C[i]=C[i+1]=C[i+2]`) occurs anywhere in the
clean corpus.

## Measurement

`experiments/obs_zero_triplets.py` (clean corpus, 12,956 runes):

| quantity | value |
|----------|-------|
| triplets observed | **0** |
| expected under uniform (1/29^2) | 15.4 |
| expected if doublets were independent at the observed rate | 0.57 |
| Poisson P(0 \| uniform) | 2e-7 |

## Significance

Under uniform randomness ~15 triplets are expected; zero is a 2e-7 event. But
given the doublet suppression, only ~0.6 are expected, so zero is unremarkable
*conditional on* the doublet deficit -- a doubled rune is simply never
immediately re-doubled. The observation is therefore not independent evidence;
it is the run-length shadow of `doublet-suppression.md`.

## Consequences

- Any mechanism reproducing the doublet suppression reproduces this for free.
- A mechanism that suppressed doublets but not triplets (e.g. some
  post-processing filters) is excluded: see `explicit-doublet-avoidance.md`.

## Scripts

- `experiments/obs_zero_triplets.py`

## Related

- `doublet-suppression.md` — the parent anomaly.
