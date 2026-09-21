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

| page (image) | chunk | red runes | span lengths |
|---|---|---|---|
| 0 | 15 | 12 | 12 |
| 3 | 18 | 17 | 15, 2 |
| 6 | 21 | 10 | 10 |
| 7 | 22 | 14 | 13, 1 |
| 8 | 23 | 11 | 11 |
| 15 | 30 | 19 | 9, 10 |
| 23 | 38 | 15 | 15 |
| 27 | 42 | 18 | 18 |
| 33 | 48 | 15 | 9, 6 |
| 39 | 54 | 2 | 2 |
| 40 | 55 | 7 | 7 |
| 53 | 67 | 51 | 1, 24, 22, 4 |
| 54 | 68 | 8 | 8 |
| 56 | 70 | 4 | 4 |
| 57 | 71 | 6 | 6 |

Span lengths run 1 to 24 runes, median 9.

**The numbering is now resolved, and it changes the count.**
`experiments/page_alignment.py` maps image pages to transcription chunks by matching
word-LENGTH sequences read off the image — runes are blobs 100–125 px tall, separator
dots 6–14, so the word structure is visible without reading a rune — scored by longest
common subsequence to tolerate the blob splits and merges. The mapping is

    chunk = page + 15   for pages 0–49
    chunk = page + 14   for pages 51–57      (page 50 is blank and consumes no chunk)

and it verifies on **56 of 57** checkable pages at LCS ≥ 0.85, the exception being page
57 at exactly 0.85 on only 20 detected words.

That yields a structural fact worth stating on its own: chunks 0–14 are the
ASCII-convention chunks and 15–71 the circled-convention ones, so **the 58 page images
are exactly the 57 unsolved chunks plus one blank page. The solved front matter has no
images in this set at all.**

**So every one of the 209 rubricated runes is on unsolved text**, and the earlier
version of this file was wrong to deduct a "front matter" share from it. The title-crib
material is 209 runes in 22 spans — roughly 47 words at the corpus's 4.4 runes per word
— against the **29 words / 128 runes** `crib-budget-for-g.md` costs out. That is a 60%
larger budget than assumed.

It does not change that file's verdict. Pinning `g` by cribs needs on the order of 300
known words; 47 is still short by more than sixfold.

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

## The titles extracted, and the pipeline validated twice (September 2026)

With `page_alignment.py` fixing the image-to-chunk correspondence, the red runes can be
placed in the transcription. Within a page the word-length sequences agree almost
exactly — image page 15 and chunk 30 both hold 37 words with one length differing — so
word-level alignment is direct, and **titles turn out to be whole-word spans**: on the
pages where a title opens the page, every rune of the first few words is red.

That yields **17 contiguous title spans, 217 runes, 52 words**
(`experiments/rubricated_titles.json`).

**Two independent validations, neither of them circular:**

- **Page 57 / chunk 71 reads `PARABLE` in clear.** That chunk is stored as plaintext
  (quadgram −4.11, opening *PARABLE LICE THE INSTAR TUNNELNG TO THE SURFACE WE MUST
  SHED OUR OWN CIRCUMFERENCES*), so the extraction produced a real English title
  end-to-end: red detection, page→chunk mapping and word extraction all have to be
  right for that word to appear.
- **Page 56 / chunk 70's title has the shape of `AN END`** — two words of 2 and 3
  runes — and decryption confirms it. That chunk is ciphertext (quadgram −9.13) and
  `running-key-math-sequence.md` records the AN END page as using `K[n] = prime(n) − 1`
  with ᚠ interrupts. Applying it and beam-searching the interrupt positions gives, with
  **one** interrupt at rune 56 and quadgram −4.27:

  > AN END. WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT. [IT] IS THE DUTY
  > OF EUERY PILGRIM TO SEEC OUT THIS PAGE

  The title predicted from red word-shape alone is the title the key produces.

AN END is added to `experiments/solved_page_triples.json` as a tenth triple.
