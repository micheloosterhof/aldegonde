---
type: observation
---
# Observation: No Periodic Key (Friedman flat at every period)

## Feature

There is no fixed-period polyalphabetic structure: the periodic index of
coincidence is at the random baseline for every period 2..40.

## Measurement

`experiments/obs_periodicity.py` (clean corpus): mean column nIoC when the
stream is split into p interleaved columns.

| period p | mean column nIoC |
|----------|------------------|
| 2..12 | 1.00-1.01 |
| max over 2..40 | 1.0094 |

A period-p key would spike the p-column nIoC toward the plaintext value
(~1.7 normalized). None does.

## Significance

Rules out every fixed-period polyalphabetic cipher (Vigenere/Beaufort with a
repeating key) regardless of key length up to 40, and combined with the flat
kappa spectrum (`kappa-spectrum.md`), up to thousands. The key, if any, is
aperiodic.

## Consequences

- Excludes `periodic-polyalphabetic.md`.
- Consistent with aperiodic word-length clocking (`length-clocked-walk.md`) or
  a non-repeating stream (`stream-cipher-no-repeat.md`).

## Scripts

- `experiments/obs_periodicity.py`

## Related

- `kappa-spectrum.md` (no lagged coincidence), `no-running-key-depth.md`.
