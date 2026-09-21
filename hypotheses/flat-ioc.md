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
- **Bounds a pass-through interrupter, including 3301's own** (September 2026).
  `solved-page-testbed.md` establishes the device from the author's solved pages: a
  ciphertext ᚠ can be a literal plaintext F consuming no key, at 1.75% of runes on
  pages 1 and 2. Such an interrupter EMITS the rune, so a fraction `q` of them puts
  `rate(x) = q + (1-q)/29` and the flat table inverts to an upper bound with no key,
  model or search:

  | rune | count | rate | q (95% upper) | runes |
  |---|---|---|---|---|
  | ᚠ (the author's own) | 458 | 3.535% | 0.0037 | 47 |
  | ᛟ (loosest of all 29) | 492 | 3.797% | 0.0065 | 84 |

  So the body admits a pass-through interrupter on **at most 0.65% of runes even at
  its most favourable rune**, against 1.75% in the author's own usage — excluded by a
  factor of 2.7. The literal form of the device does not extend from the front matter
  to the body.

  **Scope.** This bounds only interrupters that emit the rune. A clock perturbation
  that skips a key step while still enciphering the rune — the `quagmire-dodge.md`
  and `interrupted-walk.md` families — leaves no unigram trace and is untouched.

## Scripts

- `experiments/obs_flat_ioc.py` — chi-square uniformity + IoC.
- `experiments/passthrough_interrupter_bound.py` — the interrupter bound above.

## Related

- `doublet-suppression.md`, `bigram-ioc.md` — the only departures from flat.
