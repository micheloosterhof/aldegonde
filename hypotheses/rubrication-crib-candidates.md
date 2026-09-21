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

**Cross-check, with a numbering caveat that matters.** The page numbers above are
**image** page numbers (`0.jpg` … `57.jpg`). They are *not* the transcription's
`%`-chunk indices: the master transcription holds **72** rune-bearing `%`-chunks against
**58** page images, so a chunk index cannot be assumed equal to a page number, and the
solved/unsolved split established on chunks elsewhere in this directory does not
transfer to these rows by index.

Taking the conventional structure — front matter at the start, the Parable and AN END
at 56–57 — and excluding those, the remainder is 135 runes of rubricated title against
the **128 runes** `crib-budget-for-g.md` costs out. Two independently written pipelines
agreeing to 5% is the check that the census measures the same thing, and it is also the
only evidence here that the exclusion is drawn in roughly the right place. Anyone
needing the split exactly must align images to transcription first, which is not
currently possible — see below.

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

## Reading the titles needs alignment, which blob detection cannot provide

The obvious next step is to read the rubricated titles on solved pages, which would fix
what an LP section heading looks like. That needs each red rune box mapped to its
position in the transcription, and counting blobs does not achieve it. Detected blobs
of rune height disagree with the transcription's rune counts in both directions — image
page 0 gives 261 against 184, page 6 gives 194 against 218, a range of −11% to +42% —
because some runes split into several components and some touching pairs merge. Line
structure does not rescue it either: the counts per line do not line up.

So the titles stay unread until a real OCR pass exists, and this census is a census of
*where* the rubrication is, not of what it says.

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
