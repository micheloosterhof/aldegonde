---
type: observation
---
# Observation: The Written Line Is Not a Cipher Unit, and Block-Initial Runes Are Flat

## Two things nobody had tested

`separators-are-the-cipher-unit.md` shows the alphabet phase is anchored to the scribal
separators. The other visible division — the written **line** — had never been tested as
a cipher unit at all, although the body's lines are conspicuously regular: 21.75 runes at
a coefficient of variation of **0.124**, against 19.03 and 0.273 in the front matter, and
76% of them end mid-word against 58.5%. The body is set as continuous justified text.

## The line is not a unit

Pairs in the same line but in **different blocks** must sit at chance under any
block-anchored model:

| lag | hits / pairs | × chance | z |
|---|---|---|---|
| 1 | 22 / 2,722 | 0.234 | −7.55 |
| 2 | 169 / 5,126 | 0.956 | −0.59 |
| 3 | 211 / 6,909 | 0.886 | −1.80 |
| 4 | 266 / 7,904 | 0.976 | −0.40 |
| 5 | 289 / 8,344 | 1.004 | +0.08 |
| 6 | 298 / 8,433 | 1.025 | +0.43 |
| 7 | 293 / 8,277 | 1.027 | +0.46 |
| 8 | 272 / 7,947 | 0.993 | −0.13 |

Lag 1 is the seam doublet suppression, which `separators-are-the-cipher-unit.md` shows is
global rather than boundary-anchored. Everything else is chance, on 5,000 to 8,400 pairs
per lag. **Nothing crosses a block boundary because it shares a line.**

Bucketing by position-in-line reaches at most nIoC 1.0083 against a surrogate's 1.0002 ±
0.0029, where a shared alphabet at this pair type reads 1.79 (`coincidence-reference-is-not-one-number.md`) — a sharing fraction under 1.1%.

## That whole residue is the known layout artifact

| subset | n | nIoC | z |
|---|---|---|---|
| line-initial runes | 594 | **1.0900** | **+6.96** |
| line-initial, **not** block-initial | 388 | 1.0584 | +3.29 |
| block-initial runes | 2,928 | 0.9985 | −0.52 |
| block-initial, not line-initial | 2,722 | 0.9987 | −0.47 |

`line-initial-bias.md` already records line-initial non-uniformity (χ² 81.6, p = 4.8e-7)
and correctly calls it typesetting, confirmed on the solved pages. This localises it: the
effect **survives removing every block-initial rune**, so it belongs to the line, not to
the segmentation. The over-represented glyphs are EA (6.4%), P (5.6%), D (5.4%), IA
(4.9%), OE (4.5%) and NG (4.5%) against 3.4% — a glyph-shaped bias, as a
width-driven break would produce.

## Block-initial runes are the useful negative

Every block-initial rune carries the base with **no letter step applied**, so it is the
cleanest place to look for base reuse without assuming anything about g. If bases
repeated often, these 2,928 runes would coincide above chance.

They read **nIoC 0.9985, z = −0.52**. Taking the surrogate's ±0.0029 as the resolution,
base collisions among blocks are bounded at roughly **1 in 250** — an independent
confirmation of the depth-derived floor in `key-local-channel-is-empty.md` (order(σ) ≥
307), reached by a different statistic that needs no assumption about the letter step or
the clock.

## Status

**Status**: confirmed (measurement), cross-block within-line coincidence at chance for
lags 2–8 on 5,000–8,400 pairs each; block-initial subset flat on 2,928 runes.
`experiments/line_structure.py`.

## Related

- `separators-are-the-cipher-unit.md` — the division that *is* a cipher unit.
- `line-initial-bias.md` — the artifact this localises.
- `key-local-channel-is-empty.md` — the σ order floor this independently supports.
