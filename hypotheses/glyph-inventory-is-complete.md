---
type: observation
---
# Observation: No Mark Class Is Missing, and the Page Map Is Confirmed From the Scans

## The question the tick discovery left behind

`transcription-is-verified` records the lesson sharply: rune *values* are verified ground
truth, but **completeness is a different question**, and in August the scans turned out to
carry a raised tick glyph — four apostrophes and fourteen quotation marks — that no
transcription encoded. `apostrophe_census.py` found it by hunting a specific footprint,
h = 40 and w = 12, once someone suspected it was there.

That is a targeted search. It cannot answer whether anything *else* is missing. This is
the census that would have found the tick without the suspicion: every ink blob inside the
text block of all 58 pages, binned by bounding-box size.

## Result: one unexplained class, and it is not a glyph

| class | blobs | pages |
|---|---|---|
| rune (h ≈ 90–140) | 13,091 | 58 |
| dot (h, w ≈ 6–14) | 3,932 | 58 |
| tick (h 38–42, w 10–13) | 32 | — |
| **unclassified** | 2,407 | — |

Of the unclassified, almost everything is either sub-5px speckle or artwork confined to
one or two pages. **Exactly one cluster recurs at a consistent size across the book**:
h 50–62 by w 4–14, about eight per page on **56 of 58 pages**.

It is not a missing glyph. Correlating its per-page count against every rune's per-page
count in the transcription:

| rune | correlation |
|---|---|
| **Y (ᚣ)** | **+0.999** |
| NG | +0.602 |
| OE | +0.591 |
| W | +0.055 |

The counts match exactly, page after page — 13/13, 10/10, 8/8, 18/18 — while the
rune-class blob count still matches the transcribed rune count. So **ᚣ is drawn with a
detached second stroke** that connected-component labelling splits off as an extra piece.

That also confirms the tick census was uncontaminated: the tick class is h 38–42 and this
one is h 50–62, cleanly apart.

> **No mark class is missing from the transcription at this resolution** — with one
> qualification added the following day, below.

## Qualified: a class that matches the runes in SIZE was invisible here

This census bins by size, so it cannot separate a mark that is rune-sized from a rune.
`colour-channel-holds-one-layer.md` finds exactly that: five rune-sized **red** glyphs on
pages 36–38, standing at the start of a line and absent from the transcription. They were
counted here as runes.

The claim that survives is narrower: no mark class is missing *at a size that
distinguishes it from a rune*.

## The by-product is worth more than the census

One rune is now readable straight off the scans. Using it to check the page-to-chunk map
from the image side, with no text-side alignment involved:

| offset | pages | correlation | exact matches |
|---|---|---|---|
| 12 | 57 | −0.172 | 3/57 |
| 13 | 57 | −0.172 | 7/57 |
| 14 | 57 | +0.041 | 3/57 |
| **15** | 57 | **+0.9994** | **56/57** |
| 16 | 56 | +0.073 | 3/56 |
| 17 | 55 | −0.192 | 7/55 |

**chunk = page + 15 is confirmed independently**, and every competing offset is at noise.
That is the mapping this project corrected in September, when `page_alignment.py` was
found to be indexing a list with the runeless chunk filtered out and reporting a
fictitious second regime of page + 14 for pages 51–57. The fix was made from the text
side; this confirms it from the images.

It also confirms the transcription's ᚣ placements page by page — a small independent
check on transcription accuracy, which had rested entirely on crowdsourcing.

## Scope

- One resolution, one ink threshold, one text-block crop, all inherited from
  `apostrophe_census.py`. A mark drawn in colour rather than ink, or outside x ∈ [500,
  2000], is not covered — `rubrication-crib-candidates.md` handles the colour channel.
- Completeness of *mark classes*, not of individual marks. A single dropped separator
  would not surface here.
- The census counts blobs, so a glyph that always touches its neighbour is invisible.

## Status

**Status**: confirmed (census of 58 page images; 56/57 exact page-level agreement on ᚣ).
`experiments/glyph_class_inventory.py`, `--verify` for the offset check.

## Related

- `transcription-is-verified` (memory) — the completeness lesson this discharges.
- `contraction-cribs.md` — the class that *was* missing, and its census.
- `rubrication-crib-candidates.md` — the page-to-chunk map this confirms.
