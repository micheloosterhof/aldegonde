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

## They are not runes at all: they are extra line-initial marks

The blob excess that blocked the first attempt at locating them turns out to be the
answer. Grouping blobs into lines and comparing line by line:

- every page carries **five header blobs** above the text, in two short rows, which no
  transcription encodes;
- after dropping those, most lines match the transcription exactly;
- **every red mark sits at line index 0**, and on pages 36–38 every line carrying one has
  **exactly one blob more** than the transcription has runes for that line.

| page | line | blobs | transcribed runes | red at index |
|---|---|---|---|---|
| 36 | 5 | 22 | 21 | 0 |
| 37 | 0 | 21 | 20 | 0 |
| 37 | 4 | 23 | 22 | 0 |
| 37 | 9 | 21 | 20 | 0 |
| 38 | 3 | 22 | 21 | 0 |

Remove the red blob and every count matches. At page level the same arithmetic closes:
page 37 has 234 blobs, 3 header, 3 red, and 234 − 3 − 3 = **228 = its transcribed rune
count**; page 38 gives 232 − 3 − 1 = **228**, exactly right.

Page 39 behaves differently and is the control: 243 − 3 = **240 = its rune count** with
its two reds *included*, so those are red-coloured text runes, which is why the census
has it.

> **The five marks on pages 36–38 are not runes. They are rune-sized red glyphs standing
> at the start of a line, outside the transcribed text.**

## The whole book, reconciled: the five are the only red excess

`page_blob_reconciliation.py` runs the same arithmetic on all 58 pages, line by line. It
does **not** balance the book — only 5 pages reconcile exactly — and the reason is
mechanical: runes touch, so blobs merge. **74 lines carry one fewer blob than runes.**

The direction is the finding:

| | lines |
|---|---|
| fewer blobs than runes (merging) | **103** |
| more blobs than runes | **20** |

Of the twenty excess lines, **six carry a red blob**: the five line-initial marks on pages
36–38, plus the rubricated title line on page 53 where two red runes were counted apart.
**Every other excess line is black**, and they cluster on a handful of pages (2, 22, 32,
33, 53) where artwork reaches into the text block.

So across the whole corpus the only red-associated excess blobs are the five already
identified. And because deficits outnumber excesses five to one, the dominant segmentation
error is merging — the transcription is not systematically short of glyphs, which is what
would otherwise explain an excess.

Four pages (15, 49, 51, 56) are excluded: their image row count and transcription line
count disagree by more than three, so the alignment is unreliable and nothing is claimed
about them.

## This qualifies the ink census

`glyph-inventory-is-complete.md` concludes that no mark class is missing from the
transcription. That conclusion was reached by binning **size**, and these marks are
rune-sized — they hid inside the rune class and were counted as runes. Only colour
separates them.

So the honest statement is narrower than the one that file makes: no mark class is missing
*at a size that distinguishes it from a rune*. A class that matches the runes in size and
differs only in colour was invisible to that census, and there is one.

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
