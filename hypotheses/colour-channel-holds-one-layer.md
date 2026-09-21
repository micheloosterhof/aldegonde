---
type: observation
---
# Observation: The Colour Channel Holds One Layer, and Five Red Runes Are Not in the Census

## Closing the gap the ink census named

`glyph-inventory-is-complete.md` bins every ink blob by size and finds no missing mark
class — with one stated gap: **a mark drawn in colour rather than ink is invisible to a
threshold on darkness**. `rubrication_census.json` covers part of that, but by asking one
question per page — how many runes are red — which cannot see a third colour.

So bin the colours instead of assuming them. Every rune blob on all 58 pages, summarised
by its mean ink colour in the two channels that separate hues without a colour model:

| R−G | G−B | runes | pages | share |
|---|---|---|---|---|
| 0 | 0 | 12,875 | 57 | **98.35%** |
| 160 | −20 | 174 | 17 | 1.33% |
| 160 | 0 | 21 | 11 | 0.16% |
| 180 | −20 | 19 | 7 | 0.15% |
| 0 | −20 | 1 | 1 | 0.01% |
| −20 | 0 | 1 | 1 | 0.01% |

**Two populations and no third.** Neutral 98.4%, warm 1.6%, cool 0.0% — a single stray
rune. The colour channel holds one annotation layer, the rubrication already catalogued,
and there is no second ink anywhere in the book.

## But the warm population reaches two pages further than the census

| | red runes | pages |
|---|---|---|
| `rubrication_census.json` | 209 | 15 |
| this census | **214** | **17** |

The five extra sit on pages 36, 37 and 38 — one, three and one — and they are not faint:

| | mean RGB |
|---|---|
| the extra runes | (184, 6, 7) |
| a catalogued title rune, page 0 | (180, 4, 5) |

**The same ink.** `rubrication_spans.py` discards "scattered singletons" as "red initials
or bleed", which is the right filter for extracting title *spans* and the wrong
description of what it is discarding: bleed would be desaturated, and these are as
saturated as the titles.

So pages 36–38 carry deliberate red marking that no catalogue records, and pages 36–39 form
a run of four consecutive pages with one to three red runes each.

## What is not established

**Where they are.** Mapping a blob to a rune index needs a reliable alignment, and the
naive one fails here: these pages yield 232–244 rune-sized blobs against 228–240 runes in
the transcription, an excess of three to six. Until that excess is accounted for, any
claim about *which* rune is red is unfounded — and an earlier draft of this file named
them before the counts were checked.

The excess is not the ᚣ artefact from `glyph-inventory-is-complete.md`, which sits at
h 50–62 and is excluded by the 90–140 rune filter.

## Why it might matter

`rubrication-crib-candidates.md` builds cribs from red title spans: contiguous runs
marking enciphered section titles. Isolated red runes are a different object, and if they
mark something — a section opening, an emphasis, a position in the key — they are
plaintext-side information at known page locations. Five of them, on consecutive pages,
are worth locating.

## Status

**Status**: confirmed (census of all 58 page images) that the colour channel holds one
layer and that five red runes on pages 36–38 are absent from the census. Their positions
are **not** established. `experiments/colour_class_inventory.py`, `--singletons`.

## Related

- `glyph-inventory-is-complete.md` — the ink census whose stated gap this closes.
- `rubrication-crib-candidates.md` — the title spans, and the crib programme.
