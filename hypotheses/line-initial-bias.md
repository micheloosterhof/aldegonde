---
type: observation
---
# Observation: Line-Initial Rune Bias (layout artifact)

## Feature

The first rune of each written line is strongly non-uniform, while the last
rune is uniform. This is a typesetting artifact, not cipher structure.

## Measurement

`experiments/obs_line_initial.py` (clean corpus, 604 lines):

| position | chi2 (28 df) | p |
|----------|--------------|---|
| line-initial | 81.6 | **4.8e-7** (non-uniform) |
| line-final | 25.7 | 0.59 (uniform) |

## Significance

Lines are filled with as many runes as fit and break words arbitrarily, so the
first glyph of a line is biased by glyph width and layout. The solved pages show
the same line-initial bias (p=0.009), confirming it is a property of the
typesetting, not the cipher. Line-final runes are uniform, as expected for a
break driven by running out of horizontal space.

## Significance caveat

This observation is a WARNING, not a lead: any acrostic or line-anchored
analysis must treat line-initial non-uniformity as a null artifact.

## Scripts

- `experiments/obs_line_initial.py`

## Related

- `word-length-keystream-and-boundaries.md` — the line-wrap convention that
  produces this.
