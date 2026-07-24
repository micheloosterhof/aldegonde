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
