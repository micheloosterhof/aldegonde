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
- **The doublet count cannot be used to filter or rank candidate keys** (August
  2026). Under the walk the within-word rate is `g`'s diagonal and the seam rate
  is σ's, on different plaintext tables — both verified exactly against a
  planted key (10028/10028 and 2927/2927). Annealing `g` toward the observed
  count and scoring survivors by the base_0 quadgram fit produced a real-looking
  lift over random keys (+0.031, z = +5.34, `doublet_targeted_search.py`), but
  it is an artifact: the statistic being fitted is a property of the whole
  stream, shared by g and σ alike, so the filter selects for the suppression
  rather than for the key. Boundary-blindness is the tell — a genuine constraint
  on `g` would not apply equally where `g` is absent from the algebra.
- Generalising to within-word distance d gives `p_j = g^d(p_k)`, but only d=1
  departs from chance: d=2 and d=3 sit on the random-g mean to within z = 0.1
  (`skip_repeat_constraints.py`), so they cannot rank candidates either. d=5 is
  `g⁰` = identity, i.e. the known same-alphabet echo.
- Placement is Poisson/content-driven, not positional: see
  `doublet-spacing-poisson.md`.

## Scripts

- `experiments/obs_doublet_suppression.py` — count, z, within/cross split.
- `experiments/sigma_algebraic_floor.py` — the two diagonals and the floor each
  arithmetic family can reach (σ floor 0.0048, `g` floor 0.0000).
- `experiments/skip_repeat_constraints.py` — the same constraint at d = 1, 2, 3.
- `experiments/doublet_targeted_search.py` — the retracted filter; kept as the
  worked negative, see Consequences.

## Related

- `doublet-spacing-poisson.md` — the spacing of the 86 doublets.
- `zero-triplets.md` — no run of three.
- `doublet-marker-rune-ea.md` — what the doublets might mark (the
  single-fixed-rune marker class is disproved; a key event survives).
