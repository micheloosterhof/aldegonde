---
type: observation
---
# Observation: No Shared Keystream Reset at Page or Section Boundaries

## Feature

Aligning any two pages (or sections) position-by-position and counting
coincidences gives the random rate: no two text units share a positional
keystream that restarts at a boundary.

## Measurement

`experiments/aligned_kappa_nulls.py` (clean corpus):

| alignment | coincidences | expected | z / ratio |
|-----------|--------------|----------|-----------|
| all 1,485 page pairs | 10,751 | 10,729 | z = +0.22 (ratio 1.002) |
| all section pairs | — | — | z = -0.80 (ratio 0.978) |
| top single page pair (28,42) | — | — | +3.9 (order-statistic expected) |

A shared reused keystream would drive the aligned coincidence ratio toward the
plaintext IoC (~1.7), i.e. hundreds of sigma at this sample size.

## Significance

Whatever the cipher is, pages and sections do NOT share a positional keystream
that resets at their boundaries -- the way the solved AN END page restarts its
prime keystream. This is a hard, model-independent fact: the aligned-kappa
cancellation would fire for ANY reused positional keystream regardless of its
content.

## Consequences

- Excludes shared boundary-reset keystreams: see `page-reset-keystream.md`
  (the disproved hypothesis) and `periodic-polyalphabetic.md`.
- Any keystream must differ per page (keyed by page number/content) or be
  feedback-driven (autokey-like), which aligned kappa cannot cancel.

## Scripts

- `experiments/aligned_kappa_nulls.py`

## Related

- `page-reset-keystream.md` — the hypothesis this observation disproves.
- `kappa-spectrum.md`, `no-periodicity.md`.

## The two live signals are also homogeneous across sections (September 2026)

This file establishes no keystream reset at page or section boundaries from kappa. The
same conclusion follows from the corpus's only two departures from randomness, measured
per section:

| section | words | d1 rate | × chance | d5 rate | × chance |
|---|---|---|---|---|---|
| 0 | 160 | 2/569 | 0.10 | 7/134 | 1.51 |
| 2 | 385 | 7/1344 | 0.15 | 18/289 | 1.81 |
| 4 | 440 | 10/1454 | 0.20 | 17/292 | 1.69 |
| 8 | 681 | 14/2327 | 0.17 | 23/469 | 1.42 |
| 9 | 67 | 1/241 | 0.12 | 3/55 | 1.58 |

Pooled: d1 = 0.00629 (0.18×), homogeneity **chi² 4.9 on 8 df, p = 0.77**; d5 = 0.04920
(1.43×), **chi² 4.1 on 8 df, p = 0.85**. Neither the doublet suppression nor the
distance-5 echo varies detectably across the ten sections.

**Power.** The per-section spread looks wide — d5 runs 0.80× to 1.81× — but the counts
are 3 to 23 per section, so that spread is noise. A doubling of the d5 rate in the
largest section alone would contribute chi² ≈ 23 and be seen at p < 0.01, so the test
excludes factor-two variation in the big sections while saying little about subtler
drift.

**Why it matters.** Combined with `solved-page-testbed.md`'s finding that the author's
keystream runs continuously across page boundaries in his own solved pages — page 12's
keystream carries into page 13 at the exactly predicted phase — the natural reading is
one mechanism with one parameter set across all 12,956 runes, not a sequence of
re-keyings. That is also what `flat-ioc.md`'s per-page bound requires: a fresh key per
page would have to be at least 60 runes long.
