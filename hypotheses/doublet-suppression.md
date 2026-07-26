---
type: observation
---
# Observation: Doublet Suppression (5.2x, boundary-blind)

## Feature

Adjacent equal runes (doublets, `C[i]=C[i+1]`) occur ~5x less often than
random, and the suppression is the same within words and across word
boundaries. This is the corpus's defining anomaly.

## Measurement

`experiments/obs_doublet_suppression.py` (clean corpus, 12,955 adjacent pairs):

| quantity | value |
|----------|-------|
| doublets observed | **86** |
| expected at 1/29 | 446.7 |
| suppression factor | **5.19x** (rate 0.0066) |
| z vs binomial | **-17.4** |
| within-word rate | 63 / 10,028 = 0.0063 |
| cross-word rate | 23 / 2,927 = 0.0079 |
| within vs cross | z = -0.92 (boundary-blind) |

## Significance

17 sigma below random -- not a fluctuation. The within-vs-cross z of -0.92
(|z| < 2) shows the suppression ignores word boundaries: it is a property of
adjacent runes regardless of whether a space intervenes. Zero triplets
(`zero-triplets.md`) accompany it.

## Consequences

- Additive/keystream ciphers whose key is fixed before emission cannot produce
  this (rate stays ~3.45%); requires output feedback OR a bigram-tuned mixed
  alphabet. See the structural constraint in `README.md` and
  `stream-cipher-no-repeat.md`, `length-clocked-walk.md`.
- Boundary-blindness rules out per-word-reset mechanisms as the *source* of the
  suppression: see `word-boundary-reset-autokey.md`.
- Placement is Poisson/content-driven, not positional: see
  `doublet-spacing-poisson.md`.

## Scripts

- `experiments/obs_doublet_suppression.py` — count, z, within/cross split.

## Related

- `doublet-spacing-poisson.md` — the spacing of the 86 doublets.
- `zero-triplets.md` — no run of three.
- `doublet-marker-rune-ea.md` — what the doublets might mark (the
  single-fixed-rune marker class is disproved; a key event survives).
