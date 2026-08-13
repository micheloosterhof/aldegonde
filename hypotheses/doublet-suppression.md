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
- **The doublet count is a valid constraint on `g`; one pipeline built on it was
  artifactual.** (August 2026, wording corrected — an earlier version of this bullet
  said the count "cannot be used to filter or rank candidate keys", which
  contradicted `key-local-channel-is-empty.md`, where d1 is one of the seven distance
  constraints worth 16.0 bits together.) The within-word rate IS exactly
  `Σ_b P(g(b), b)`, so requiring a candidate to reproduce it is legitimate, and it is
  used as a filter. What failed was a specific pipeline: annealing `g` toward the
  observed count and then scoring survivors by the base_0 quadgram fit produced an
  apparent lift over random keys (+0.031, z = +5.34, `doublet_targeted_search.py`)
  that does not survive scrutiny — the boundary-blindness is the tell, since the
  within-word rate is `g`'s diagonal and the seam rate is σ's on a different table
  (both verified exactly against a planted key, 10028/10028 and 2927/2927), yet the
  two agree, so the annealed statistic tracks something both share rather than `g`.
- Generalising to within-word distance d gives `p_j = g^d(p_k)`. As a RANKING
  signal d=2 and d=3 are useless — they sit on the random-`g` mean to within z = 0.1
  (`skip_repeat_constraints.py`). But as CONSTRAINTS the whole set d1…d7 is used and
  is worth 16.0 bits jointly (`key-local-channel-is-empty.md`); a cell being at the
  random mean still excludes candidates that miss it. d=5 is `g⁰` = identity, i.e.
  the known same-alphabet echo, and cannot be tuned at all.
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
