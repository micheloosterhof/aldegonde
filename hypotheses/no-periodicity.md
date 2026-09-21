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
kappa spectrum (`kappa-spectrum.md`, skips 2-60) up to 60 — and, via the
lag-1..11,956 scan in `cryptodiagnostics-page0-58.md`, to the corpus length. The key, if any, is
aperiodic.

## Consequences

- Excludes `periodic-polyalphabetic.md`.
- Consistent with aperiodic word-length clocking (`length-clocked-walk.md`) or
  a non-repeating stream (`stream-cipher-no-repeat.md`).

## Scripts

- `experiments/obs_periodicity.py`

## Related

- `kappa-spectrum.md` (no lagged coincidence), `no-running-key-depth.md`.

## Interrupts blind this test, demonstrated on the author's own ciphertext (September 2026)

The flat Friedman scan is read here as excluding a periodic key. The solved front matter
shows that a preventer defeats the scan outright, so the reading needs qualifying.

Chunks 1, 2 and 12 are keyed Vigenère with **known** periods 8, 8 and 13 and known
interrupt positions (`solved-page-testbed.md`). Running the project's own
`friedman_test` on them:

| chunk | runes | interrupts | true period | avgioc as transcribed | phase restored | background |
|---|---|---|---|---|---|---|
| 1 | 251 | 6 | 8 | 0.0420 | **0.0640** | 0.0448 |
| 2 | 264 | 3 | 8 | 0.0440 | **0.0600** | 0.0392 |
| 12 | 226 | 2 | 13 | 0.0490 | **0.0630** | 0.0356 |

Plaintext-level IoC is ~0.062, which a clean Vigenère coset should reach. **Once the
interrupt runes are dropped and the key phase is restored, all three do.** As
transcribed, chunks 1 and 2 sit *at or below* their own background: a period-8 Vigenère
with 6 interrupts in 251 runes — an interrupt rate of 2.4% — is completely invisible to
this test.

**So a flat Friedman scan cannot exclude a periodic key that is interrupted.** The body
would have to be quieter than that to be excluded, and the preventer reading favoured by
`key-local-channel-is-empty.md` puts its perturbation rate near 3.4%, higher than the
2.4% that already blinds the scan here.

**What still excludes short keys is the index of coincidence, not this scan.** A phase
perturbation moves *which* alphabet is used at a position; it does not change *how many*
alphabets exist, and the IoC bound in `flat-ioc.md` counts alphabets. That bound —
≥949 under one key, ≥60 runes per key even with a free rekey every page — is
phase-independent and survives any interrupt rate.

Net: this file's conclusion stands, but its force comes from the IoC bound rather than
from the period scan, and the period scan should not be cited on its own against an
interrupted cipher.
