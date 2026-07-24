---
type: observation
---
# Observation: Flat Unigram Distribution (IoC = 1/29)

## Feature

All 29 runes occur near-equally often in the clean corpus; the index of
coincidence is indistinguishable from uniform random.

## Measurement

`experiments/obs_flat_ioc.py` (clean corpus, sections 0-9, 12,956 runes):

| quantity | value |
|----------|-------|
| min / max rune count | 399 / 492 |
| chi-square vs uniform (28 df) | 26.4, **p = 0.553** |
| normalized IoC | 0.9999 (random = 1.0000) |

## Significance

Uniformity is not rejected (p = 0.55, well above 0.05). The IoC sits exactly
at the random baseline. Any cipher must flatten English/runeglish letter
frequencies (which are strongly non-uniform, IoC ~1.7-1.8) to this.

## Consequences

- Excludes monoalphabetic substitution and pure transposition (both preserve
  frequencies): see `monoalphabetic-substitution.md`, `transposition.md`.
- A mechanism that visits many alphabets (polyalphabetic, autokey, walk) or a
  stream cipher can produce it.

## Scripts

- `experiments/obs_flat_ioc.py` — chi-square uniformity + IoC.

## Related

- `doublet-suppression.md`, `bigram-ioc.md` — the only departures from flat.
