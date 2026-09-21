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
| 53 | 68 | 51 | 1, 24, 22, 4 |
| 54 | 69 | 8 | 8 |
| 56 | 71 | 4 | 4 |
| 57 | 72 | 6 | 6 |

Span lengths run 1 to 24 runes, median 9.

**The numbering is now resolved, and it changes the count.**
`experiments/page_alignment.py` maps image pages to transcription chunks by matching
word-LENGTH sequences read off the image — runes are blobs 100–125 px tall, separator
dots 6–14, so the word structure is visible without reading a rune — scored by longest
common subsequence to tolerate the blob splits and merges. The mapping is

    chunk = page + 15        for every page, 0 to 57

and it verifies on **53 of 57** checkable pages at LCS ≥ 0.85. Page 57 is the exception,
carrying only 20 detected words; it resolves to chunk 72 by content instead, since that
chunk reads `PARABLE` in clear.

**Corrected 2026-09-22.** This file previously recorded a second regime,
`chunk = page + 14` for pages 51–57, "because page 50 is blank and consumes no chunk".
Page 50 does consume one: master chunk 65 is the base-60 data page, which holds no
runes. The apparent second regime came from `page_alignment.py` indexing a list with
the runeless chunk filtered out, so every chunk after 65 was reported one low, while
`rubricated_titles.json` and `solved_page_triples.json` use the master's own
`%`-positions. Four title entries carried the wrong chunk number as a result; their
extracted text was right, and all 17 now reproduce from their recorded chunk.

That yields a structural fact worth stating on its own: chunks 0–14 are the
ASCII-convention chunks and 15–72 the circled-convention ones, so **the 58 page images
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

- **Page 57 / chunk 72 reads `PARABLE` in clear.** That chunk is stored as plaintext
  (quadgram −4.11, opening *PARABLE LICE THE INSTAR TUNNELNG TO THE SURFACE WE MUST
  SHED OUR OWN CIRCUMFERENCES*), so the extraction produced a real English title
  end-to-end: red detection, page→chunk mapping and word extraction all have to be
  right for that word to appear.
- **Page 56 / chunk 71's title has the shape of `AN END`** — two words of 2 and 3
  runes — and decryption confirms it. That chunk is ciphertext (quadgram −9.13) and
  `running-key-math-sequence.md` records the AN END page as using `K[n] = prime(n) − 1`
  with ᚠ interrupts. Applying it and beam-searching the interrupt positions gives, with
  **one** interrupt at rune 56 and quadgram −4.27:

  > AN END. WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT. [IT] IS THE DUTY
  > OF EUERY PILGRIM TO SEEC OUT THIS PAGE

  The title predicted from red word-shape alone is the title the key produces.

AN END is added to `experiments/solved_page_triples.json` as a tenth triple.

## What the title shapes constrain, and one filter that must not be used

The extracted spans give each title's **word-length shape**, which is key-free. Matching
those against a 327-word vocabulary of 3301's own terms:

| page | shape | combinations | scarcest slot |
|---|---|---|---|
| 54 | (1) | **1** | one 1-rune word exists |
| 33 | (2, 8) | 144 | |
| 0 | (8, 5) | 1,032 | |
| 3 | (2, 11, 3) | 1,656 | 11 runes → 6 words |
| 8 | (4, 8) | 1,920 | |
| 27 | (3, 12, 4) | 11,040 | 12 runes → **3** words |
| 53 | (5,4,4,11,2,3,2,6,5,5,2,2) | 8.6e15 | |

The method identifies both titles that are independently known — (2,3) matches AN END,
(7) matches PARABLE — so it works. None of the fifteen unsolved shapes matches any
common LP title phrase, so those titles are not the obvious ones.

Several are genuinely constrained: page 33's title has 144 candidate phrases and page
27's has a 12-rune slot with only three vocabulary words. What is missing is a way to
*test* a candidate without the key.

**A tempting key-free test exists and it is not safe.** Because g⁵ = id, positions i and
i+5 within a word share an alphabet, so a ciphertext distance-5 coincidence should mean
a plaintext one and vice versa — which would filter candidate words by their own
distance-5 repeat pattern. Applied, it removes 10–15% of candidates and cuts the
11-rune slot to three (ENLIGHTENED, PRESERUATIAN, PRESERVATION).

**Do not use it as a hard filter.** Two reasons:

- It assumes φ5 = 1, and φ5 is measured at 0.64–1.0 and underpowered
  (`d5-partial-alphabet-leak.md`). Under φ5 < 1 a true plaintext repeat can fail to
  appear in the ciphertext, and the filter then rejects the true word.
- Under the preventer reading now favoured by `key-local-channel-is-empty.md`, a clock
  skip between i and i+5 breaks the shared alphabet outright, so the correspondence
  fails in both directions.

**And it cannot be validated on what we have.** The ground truth available — PARABLE,
and the three words of length ≥ 6 in the solved AN END page — has an *empty* distance-5
pattern on both the ciphertext and plaintext side in every case. "The filter agrees with
the truth" is therefore vacuous: it has never been given a case where it could disagree.
It may be used as a soft score; as a hard filter it is the retention failure that
`schedule-band-retention.md` documents, in a new place.

## The titles are enciphered exactly like the body

A natural hope is that section titles, being short and set apart, were enciphered more
simply than the running text — which would make them crackable on their own. They were
not.

Pooling the 16 ciphertext title spans (excluding chunk 72's PARABLE, which is stored as
plaintext) gives **210 runes in 51 words**:

| | title ciphertext | body |
|---|---|---|
| normalised IoC | 0.953 (flat null 0.999 ± 0.036, z = −1.30) | 1.000 |
| within-word doublets | 0/159 | 0.18× chance |

**The IoC is flat**, where a monoalphabetic title cipher would sit near 1.79 and a
five-alphabet Vigenère near 1.16. At 2σ the titles use **at least 11 alphabets**, which
excludes every simple cipher the front matter uses — the front matter's own keys are 8
and 13 runes and would show.

**The doublet suppression is present too**: zero doublets in 159 within-word pairs,
where chance gives 5.5 and the body's own rate gives 1.0. Observing zero is consistent
with the body's rate (P = 0.37) and rules out chance (P = 0.004).

So the titles carry the same cipher as the text around them. Their value remains what
`crib-budget-for-g.md` says it is — verification material, not a way in.
