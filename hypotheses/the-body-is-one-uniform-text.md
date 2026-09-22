---
type: observation
---
# The Body Is Homogeneous Across Its Sections

## Why it needed testing

Every pooled result in this directory rests on it — 2,896 blocks, 12,956 runes, 86
doublets, all treated as one population. Only two spot checks existed:
`does_g_change_mid_book.py` compares the halves' d-profiles (7:1 for one g) and
`short-units-are-written-joined.md` checks the joining rate over nine sections. Nothing
covered the rest.

The observables must be **key-free** or the audit measures the key instead of the text,
which is how `collision-dispersion-is-key-noise.md` ended. Block lengths and mark rates
never involve the base; a lag-k coincidence cancels it.

## Result

Across the ten sections the `$` markers define:

| observable | χ² | df | P |
|---|---|---|---|
| blocks of length 2 | 3.45 | 8 | 0.903 |
| 4-dot marks per rune | 11.57 | 8 | 0.171 |
| lag-1 doublets | 4.78 | 7 | 0.687 |
| lag-5 coincidences | 4.34 | 7 | 0.740 |
| mean block length | 3.43 | 9 | 0.945 |

Uniform on all five. No trend with section order either (Spearman |r| ≤ 0.37, P ≥ 0.33),
though nine usable sections resolve only a strong one.

## What it could have caught

Heterogeneity planted in section 8, the largest at 669 blocks and 3,008 runes:

| observable | planted | χ² | P |
|---|---|---|---|
| blocks of length 2 | that section at 0.20 | 8.84 | 0.356 |
| blocks of length 2 | **at 0.24, the author's unjoined rate** | **23.32** | **0.003** |
| 4-dot per rune | that section × 1.5 | 22.61 | 0.004 |
| 4-dot per rune | × 2.0 | 45.21 | 0.000 |
| lag-1 doublets | that section at 0.010 | 29.47 | 0.000 |
| lag-1 doublets | at 0.020 | 55.23 | 0.000 |

So the audit excludes **a section behaving like the front matter** — one that does not
join, or carries half again the marks, or suppresses 1.6× more weakly. It does **not**
exclude a section joining at 0.20 against the body's 0.15.

## What this settles and what it does not

**Settles**: pooling the body is sound, and the conventions that change at page 15 —
joining, the interrupter, the 13-dot, the mark rate — change *once*, at that boundary,
not repeatedly through the body. That is what a single different exemplar looks like and
not what a scribe drifting page by page looks like.

**Does not settle** mild drift, nor any change at a boundary the `$` markers do not mark.
A change-point scan would address the second, and would need a surrogate null for the
maximum (`scan-maxima-need-surrogate-nulls`).

## Status

**Status**: confirmed, with measured power. `experiments/is_the_body_homogeneous.py`.

## Related

- `short-units-are-written-joined.md` — the different-exemplar reading this supports.
- `collision-dispersion-is-key-noise.md` — why the observables here are key-free.
- `the-thirteen-dot-closes-a-section.md` — what identifies the section boundaries.
