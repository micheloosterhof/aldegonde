---
type: observation
---
# The Transcription Collapses Four Mark Glyphs into Two Characters

## Status

**Status**: confirmed (characterization) for the inventory. The consequence for
the '.'-mark semantics is measured but underpowered.

## Claim

The transcription records two marks: `-` for a word separator and `.` for a
sentence mark. The page scans carry at least **four distinct dot-cluster
glyphs**, and the transcription maps them onto those two characters — sometimes
inconsistently, sometimes not at all.

Found by manual review of `experiments/boundary_review_sheet.py` (Michel,
August 2026), then measured.

## The inventory

`experiments/dot_cluster_census.py` finds every dot-sized blob in the text
block of all 58 pages and groups them by proximity:

| dots per cluster | clusters | reading |
|---|---|---|
| 1 | 2937 | word separator |
| 3 | 24 | a distinct symbol |
| 4 | 145 | sentence mark |
| 5 | 9 | — |
| 10 | 8 | a distinct symbol |
| 13 | 31 | a distinct symbol |
| 18, 23, 26, 51, 76, 86, 428 | 1 each | marginal artwork |

Per page the transcription's `.` count matches **4-dot + 13-dot**, not the
4-dot count alone (176 against 175 recorded).

`experiments/mark_type_split.py` then aligns each page's glyph sequence to its
transcription line — aligning on mark *positions* rather than types, so the
transcribed type is not assumed — and cross-tabulates 2,131 marks:

| dots on page | as `-` | as `.` |
|---|---|---|
| 1 | 2010 | 0 |
| 3 | **2** | 0 |
| 4 | 0 | 104 |
| 10 | 0 | 3 |
| 13 | 0 | **11** |
| 23 | 0 | 1 |

So `-` is 1-dot **plus** 3-dot, and `.` is 4-dot **plus** everything larger.
Roughly **13% of the recorded `.` marks are not the 4-dot sentence glyph.**

## Where the large glyphs sit

Position of every large symbol the reader locates, relative to its line's first
and last rune:

| dots | line-initial | mid-line | line-final | verdict |
|---|---|---|---|---|
| 10 | 1 | 0 | 3 | mark |
| **13** | **3** | **13** | **16** | mark |
| 14 | 3 | 0 | 0 | **ornament** |
| 15 | 0 | 3 | 0 | **ornament** |
| 23, 26, 51, 76 | 2 | 1 | 1 | artwork |

**The 14- and 15-dot classes are not marks.** Every instance sits on **line 4**
of six consecutive pages, alternating 15-mid / 14-initial across pages 9 to 14.
Punctuation does not land on the same line of six pages in a row; this is a
page ornament the reader still admits, and it should be excluded rather than
encoded. The same goes for the 23/26/51/76-dot singletons, which are marginal
illustration.

**The 13-dot symbol is ordinary punctuation, not a bracket.** It sits mostly at
line ends and mid-line, and only 2 lines out of 43 carrying a large symbol have
one at each end (pages 7 and 15). An earlier draft here called it a structural
delimiter on the strength of exactly those two lines; that was generalising
from the first two examples reviewed, and the census contradicts it. It behaves
like a heavier stop than the 4-dot glyph — and both are recorded as `.`.

**Sharpened (August 2026): it is specifically a SECTION-boundary stop.** Of the 29
thirteen-dot marks, **22 sit within one word of a section marker** (`&`, `$`, `%`)
against 1.8 ± 1.3 expected from random placement — **z = +15.5**. That also disposes
of a clustering effect found and then withdrawn in the same session: the marks appear
to pair up in word index (14 gaps of ≤6 words, against 7.2 ± 2.0 uniform), which
looks bracket-like, but **13 of those 14 pairs straddle a section marker**. A section
ends with one and the next begins with one, so the pairing is section structure, not a
delimiter class. The bracket reading stays retracted, now for a measured reason rather
than a census of two lines.

Manually confirmed cases (Michel, from the review sheet), which is how the
class was found:

| page | line | glyph | position | transcribed as |
|---|---|---|---|---|
| 0 | 0 | 13-dot | mid-line | `.` |
| 3 | 0 | 13-dot | mid-line | `.` |
| 3 | 5 | 13-dot | line end | `.` |
| 3 | 6 | 13-dot | mid-line | `.` |
| 6 | 3 | 13-dot | line end | `.` |
| 7 | 9 | 13-dot | both ends | opening dropped, closing `.` |
| 15 | 0 | 13-dot | both ends | opening dropped, closing `.` |
| 20 | 6 | 3-dot | line start | dropped |
| 38 | 9 | 10-dot | line start | dropped |
| 5 | 4 | 3-dot | line end | recorded as `-` |
| 11 | 10 | 3-dot | line end | recorded as `-` |

Two failure modes, and they are different:

- **Line-END marks are recorded but sometimes mistyped** — a 3-dot glyph comes
  through as an ordinary word separator, a 13-dot as a plain `.`.
- **Line-START marks were dropped entirely, and are now RECOVERED (August
  2026).** Every confirmed line-initial glyph, at three different sizes, was
  absent. This also explained the "leading separator" cases in
  `boundary_verification.py`: 19 of 21 clean disagreements had the image carrying
  a mark the transcription lacked, all at line edges — not reader noise after
  all. The re-transcription has since restored them: `page0-56.txt` now has **38
  lines beginning with a mark** (44 in the master, 0 lines end with one, the
  convention placing a line-spanning boundary at the start of the following
  line). The `boundary_verification.py` leading-separator disagreements are
  therefore resolved rather than open.

The dropped line-initial marks are the same failure mode as the apostrophes and
quotation marks (`contraction-cribs.md`): the glyph inventory was assumed rather
than measured.

## Consequence for the '.'-mark semantics: measured, not resolved

`word-length-keystream-and-boundaries.md` records the corpus's one unexplained
observation — the `.` marks carry no English sentence-final signature (solved
pages z = +7.06, unsolved z = -1.21) — and proposes the marks may be a
**mixture**. It looked for that mixture by line position. The scans say there
is a mixture by glyph, which is a better candidate.

Splitting the aligned `.` marks by glyph and measuring the word before each:

| glyph | n | mean length before | 1-2 runes |
|---|---|---|---|
| small (< 8 dots) | 101 | 4.16 | 21.8% |
| large (>= 8 dots) | 15 | 4.60 | 13.3% |
| pooled | 116 | 4.22 | 20.7% |

The large glyphs do lean the English way — longer words before them, fewer
short ones — but **t = -0.77, p = 0.45**. This does not resolve the puzzle. The
4-dot marks alone still sit at 4.16 against a 4.42 corpus baseline, i.e. still
no signature.

**It is also underpowered by construction**: n = 15 in the large class, and 173
lines were skipped because the connected-component reader merges touching runes,
so only about two thirds of the marks aligned. A better reader would roughly
double the sample. The negative should be read as "not shown", not "shown
absent".

## Proposed encoding

One character per glyph, so the classes stop collapsing. Unicode has exact
names for the small counts; the large ones have no standard mark, so circled
numerals carry the count plainly (Michel's suggestion):

| dots | character | codepoint | name |
|---|---|---|---|
| 1 | `-` | — | word separator, unchanged |
| 3 | `⁖` | U+2056 | THREE DOT PUNCTUATION |
| 4 | `⁘` | U+2058 | FOUR DOT PUNCTUATION |
| 5 | `⁙` | U+2059 | FIVE DOT PUNCTUATION |
| 10 | `⑩` | U+2469 | CIRCLED DIGIT TEN |
| 13 | `⑬` | U+246C | CIRCLED NUMBER THIRTEEN |

This is deliberately not applied yet. The transcription is shared data and the
reader still has gaps (below); the encoding should follow adjudication, not
precede it.

## Reader accuracy

Correcting the marks needs a reader whose disagreements are the
transcription's fault rather than its own. `experiments/page_reader.py`
replaces the first one, fixing both known faults:

- **Artwork** — glyphs were selected by y-band and a global x window, so a
  marginal illustration at a line's height was read as a dot. Each line is now
  bounded by its own leftmost and rightmost rune plus a margin.
- **Merged runes** — connected components join touching runes into one blob.
  Splitting on width alone made this *worse* (alignment fell to 22%), because
  runes differ genuinely in width and glyphs like D and X were cut in half. A
  cut is now made only where the column ink profile actually collapses, which
  is what a thin join between two runes leaves and a single wide rune does not.

| reader | lines aligned exactly |
|---|---|
| first | 429 / 604 = 71.0% |
| current | 447 / 498 = **89.8%** |

Remaining gap: 12 pages are skipped entirely because the band count does not
match the transcription's line count, which is why the denominator falls from
604 to 498. Those pages need per-page attention before the inventory is
complete.

## What needs correcting downstream

Any statistic that counts `.` marks is measured on the wrong inventory:
sentence lengths, mark density, the 168-mark count, the sentence-final tests,
and the quoted-span alignment in `quote-span-boundaries.md` (which found span
edges landing on `.` marks at p = 1.5e-7 — worth re-running split by glyph,
since a structural bracket is exactly the kind of thing quoted speech might
align to).

## Scripts

- `experiments/dot_cluster_census.py` — the glyph inventory by dot count.
- `experiments/mark_type_split.py` — page glyph against transcribed character,
  and the sentence-final split.
- `experiments/boundary_review_sheet.py` — the review sheet that surfaced it.

## Related

- `word-length-keystream-and-boundaries.md` — the mark-semantics puzzle.
- `quote-span-boundaries.md` — quoted spans align to `.` marks; needs re-running
  by glyph.
- `contraction-cribs.md` — the previous incomplete-inventory finding.

## Verdict

The transcription's mark alphabet is smaller than the book's. There are at
least four dot glyphs and two characters, the 13-dot symbol looks structural
and is sometimes dropped entirely, and 3-dot symbols are recorded as ordinary
word separators. Splitting the `.` marks by glyph does not rescue the
sentence-final signature at current coverage, but the test is weak and the
inventory correction stands on its own.
