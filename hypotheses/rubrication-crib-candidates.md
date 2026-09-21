---
type: observation
---
# Observation: The Rubricated Title Slots — 22 Spans, 209 Runes, and 24 Pages Where They Cannot Be Seen

## Feature

This file is cited by `crib-budget-for-g.md` (twice) and `repeated-phrase-dju-bei.md`
but had never been written; the census below supplies what those references assume.

The Liber Primus writes section titles in red. Detecting rubricated runes directly from
the page images — a rune is an ink blob 100–125 px tall inside the text block, and its
mean redness `R − (G+B)/2` is bimodal, with most runes at 0 and rubricated ones near
178 — gives:

| | |
|---|---|
| pages | 58 |
| pages whose scan carries colour | **34** |
| pages stored as greyscale (rubrication unrecoverable) | **24** |
| pages with rubrication, among the colour ones | 15 |
| rubricated spans | 22 |
| rubricated runes | 209 |

| page | red runes | span lengths |
|---|---|---|
| 0 | 12 | 12 |
| 3 | 17 | 15, 2 |
| 6 | 10 | 10 |
| 7 | 14 | 13, 1 |
| 8 | 11 | 11 |
| 15 | 19 | 9, 10 |
| 23 | 15 | 15 |
| 27 | 18 | 18 |
| 33 | 15 | 9, 6 |
| 39 | 2 | 2 |
| 40 | 7 | 7 |
| 53 | 51 | 1, 24, 22, 4 |
| 54 | 8 | 8 |
| 56 | 4 | 4 |
| 57 | 6 | 6 |

Span lengths run 1 to 24 runes, median 9.

**Cross-check.** Excluding the front matter (pages 0–14) and the solved Parable and AN
END pages (56, 57) leaves 135 runes of rubricated title on unsolved pages, against the
**128 runes** `crib-budget-for-g.md` costs out. Two independently written pipelines
agreeing to 5% is the check that this census is measuring the same thing.

## Status

**Status**: confirmed (measurement) from the page images at
`~/src/cicada-2014/stage11/…onion/`. `experiments/rubrication_census.json` holds the
per-page result.

## The limitation that matters: 24 pages cannot be checked at all

**Nearly half the book's scans are greyscale** — pages 1, 16–21, 24–25, 28–31, 41–48,
50–52 have R = G = B exactly, so any rubrication on them is simply absent from the data
rather than absent from the book. Among the 34 colour pages, 15 carry rubrication (44%),
so the greyscale pages plausibly hide another ten or so titled sections and roughly 90
further rubricated runes.

**That would not change the crib verdict.** `crib-budget-for-g.md` measures that pinning
`g` by cribs needs on the order of 300 known words where the titles supply 29. Doubling
the title material to ~58 words still falls short by a factor of five. Better scans
would improve the verification material, not open the crib route.

## What the spans are for

`mark-glyph-inventory.md` establishes the section structure as **[rubricated
title][13-dot mark][body]**, which the 13-dot findings in
`marks-are-not-clause-punctuation.md` corroborate independently: the 13-dot glyph is
paragraph-associated, sitting immediately beside the transcription's own `&` in 45% of
cases against ~1% expected. So a rubricated span is a section heading and the 13-dot
mark closes it.

That makes each span a *phrase-shaped* crib rather than a word-shaped one, which is why
`crib-budget-for-g.md` treats them as verification material: 22 spans of median 9 runes
can confirm a candidate key quickly but cannot generate one.

## Related

- `crib-budget-for-g.md` — the budget these slots are costed against.
- `mark-glyph-inventory.md` — the [title][13-dot][body] structure.
- `marks-are-not-clause-punctuation.md` — the independent evidence that 13-dot is
  structural markup.
