---
type: observation
---
# The Thirteen-Dot Mark Closes a Section; the Four-Dot Mark Avoids One

## The claim

The two dot marks the body uses are different kinds of thing. The 13-dot sits at
structural boundaries; the 4-dot sits away from them, by more than chance.

| | n | median runes to nearest `$` | within 40 runes | random null | P |
|---|---|---|---|---|---|
| **13-dot** | 31 | **9** | **23 / 31** | 313 ± 74 | **0.0000** |
| 4-dot | 141 | 429 | 5 / 141 | 310 ± 33 | 0.999 |
| 3-dot | 6 | 548 | 1 / 6 | 331 ± 152 | 0.907 |
| 10-dot | 4 | 408 | 0 / 4 | 358 ± 189 | 0.658 |

The 4-dot's P of 0.999 is the upper tail: it is **farther** from section breaks than
random scatter, so it avoids them rather than merely ignoring them.

## The adjacency is categorical, not statistical

What immediately follows each mark in the transcription:

    13-dot   '&' 15,  a rune 15,  another 13-dot 1
    4-dot    '&'  0,  a rune 132, a quote mark 5

**Fisher exact P = 2.2 × 10⁻¹³.** Sixteen of the 31 13-dot marks sit at distance zero
from an `&` marker, against 0 of 141 4-dot marks. The run that follows is usually
`& $ %` — marker, section break, page break.

`&` is not a guess: rendering the solved pages with their plaintext spliced into their
own separator layout (`does_the_author_ever_join.py`) shows it standing between blocks of
text, as in `ALL THNGS SHOULD BE ENCRYPTED . <&> CNOW THIS . <&> <$>`.

## What it explains

- **Why pooled `.` statistics are a mixture** — the standing warning in
  `marks-are-not-one-glyph`, now with a mechanism: they average a sentence-level mark
  with a section-level one.
- **Why the 4-dot carries the sentence-final anomaly and the 13-dot does not**
  (`sentences-do-not-end-long.md`, −0.32 ± 0.20 against +0.05 ± 0.39). The 13-dot cell
  was never an underpowered counter-example; it was the wrong population.
- **Why pages 0–14 have none.** They carry 13 `&` and 7 `$` — full section structure —
  and not one 13-dot. The body marks its section closes with a glyph the front matter
  does not use, which is another entry in the list of conventions that change at page 15
  alongside the joining and the interrupter.

## What it does not settle

Fifteen of the 31 are followed by a rune, so the 13-dot is not exclusively terminal.
Whether that is a second function, or the same one at boundaries the transcription does
not record, is not answerable from this corpus.

## A lead that died on the way, recorded so it is not chased again

The body's per-page line measure correlates **−0.74** with the page's 13-dot count, which
looks like a scribal signature and is not. 13-dot pages are section-end pages, which carry
fewer runes (r = −0.56), and a page with fewer runes has shorter lines (r = +0.71, close
to arithmetic). Controlling for runes and lines on the page, the partial correlation is
**+0.087, P = 0.59**.

## How to falsify

- **A 13-dot far from any structural marker in a section it does not close.** Fifteen are
  followed by runes; if those turn out to sit mid-section with no `&` nearby at all, the
  reading needs a second function.
- **The front-matter absence is one sample.** If a 13-dot were found on pages 0–14 the
  convention-change reading weakens; the transcription resolves dot counts there for no
  mark, so this cannot currently be checked either way.

## Status

**Status**: confirmed. `experiments/what_the_thirteen_dot_marks.py`.

## Related

- `sentences-do-not-end-long.md` — where the per-glyph split first showed and was read as
  an underpowered cell.
- `short-units-are-written-joined.md` — the other convention that changes at page 15.

## Confirmed by the ink, independently of the text

`experiments/do_the_marks_bound_the_titles.py`

Everything in this file so far argued from the text. The rubrication supplies an
independent anchor: `rubrication-crib-candidates.md` reads the red runes off the page
scans and records which words each of seventeen titles covers, using only the red rune
count and word lengths — **no mark is used to find a title**, so there is no circularity.

Those seventeen titles are structural boundaries fixed by ink. The thirteen-dot is on
them:

| | observed | rate at an ordinary boundary | P |
|---|---|---|---|
| mid-page titles closed by ⑬ | 6 / 6 | 0.0098 | 9e-13 |
| mid-page titles opened by ⑬ | 5 / 6 | 0.0098 | 5e-10 |
| mid-page titles bounded by any mark, both sides | 6 / 6 | 0.0592 | 4e-08 |
| page-opening titles after a page ending in a mark | 11 / 11 | 13 of 57 pages | 4e-10 |

**Eleven of the body's thirteen page-final marks sit at a title.** A mark at the foot of a
page is usually there because a title starts the next one.

The one exception is the twelve-word span on page 53, opened by a four-dot. The census
records that entry as four adjacent red runs read as a single range, so it is the weakest
of the seventeen.

### What this settles and what it does not

**Settles:** the marks are not placed independently of the text's structure. The reading
"the marks fall in positions unrelated to the syntax" (`marks-are-not-clause-punctuation.md`)
cannot be maintained in that form — the ink says ⑬ marks section edges.

**Does not settle, and this is the important half:** the glyph the titles pin is not the
glyph that carries the sentence-final anomaly. On the final-block gap
(`what_the_marks_are.py`) ⑬ reads +0.05 ± 0.39 and ④ reads −0.32 ± 0.20, and it is ④ that
supplies 136 of the body's blocks-before-a-mark. The rubrication anchors ⑬ and is silent
about ④.

So the anomaly is unchanged and better located: **⑬ is a section mark and behaves like
one; ④ is a mark of some other kind, and whatever it closes, the block before it does not
lengthen.** That is consistent with `marks-are-not-one-glyph.md`, which found the two
glyphs behave oppositely, and it means the two surviving readings should now be restated
about ④ alone.

## A third physical channel: paragraph breaks

`experiments/does_the_body_break_paragraphs.py`

A manuscript set as justified text fills every line except where a unit ends, so a **short
line** marks a paragraph break without reading a rune. The device is real in both sections
— a short line is closed by a mark at ~15× the ordinary rate (author 11/14 against 0.04;
body 9/19 against 0.03, P = 3e-10).

In the body the instances are almost all ⑬:

| glyph | in the body | closing a short line | rate |
|---|---|---|---|
| ⑬ | 28 | 5 | **0.179** |
| ④ | 139 | 3 | **0.022** |

**z = +3.55.** The thirteen-dot takes a paragraph break eight times as often as the
four-dot — a third physical channel separating the two glyphs, after the red ink and the
line-end rate, agreeing with both.

**RETRACTED side observation.** This first read the body's lines as twice as uniform as
the author's (sd 2.3 against 4.7) with paragraph breaks three times rarer (3.5% against
10.6%). That compared against his **plaintext** pages, and
`does_the_body_have_a_different_hand.py` states the confound: enciphered text has no word
shapes to break on, so a scribe fills to a measure.

Against the enciphered front matter — the right control — the body is barely different:

| | lines | sd | short | mid-word |
|---|---|---|---|---|
| front matter, plaintext | 49 | 6.6 | 16.3% | 46.9% |
| front matter, enciphered | 83 | 3.0 | 4.8% | 69.9% |
| the body | 539 | 2.3 | 3.5% | 77.7% |

The residual is small and real: sd 2.32 against 2.97, F = 1.64, p = 0.0007 — a factor of
1.28. The short-line and mid-word rates are within noise, and a short line is mark-closed
at the same rate in both (0.47 against 0.50).

The ⑬-against-④ comparison above is unaffected: it is internal to the body.

## The thirteen-dot has two layout roles, and pooling them describes neither

`experiments/the_thirteen_dot_is_two_marks.py`

Splitting every body ⑬ by its role at a rubricated title, against the body's own one-dot
separator baseline of 0.0401:

| thirteen-dot | n | at a line end | z |
|---|---|---|---|
| **closes a title** | 9 | **0/9 = 0.000** | −0.61 |
| opens a title | 4 | 3/4 = 0.750 | +7.23 |
| **neither** | 13 | **12/13 = 0.923** | +16.19 |
| pooled | 26 | 15/26 = 0.577 | |

A title's **closing** ⑬ is never at a line end — the body text continues on the title's own
line, as a short heading set at the head of a paragraph would. Every other ⑬ ends its line
almost always, which is what opening a new unit looks like.

**Consequence.** `the-four-dot-is-not-layout-coupled.md` uses ⑬'s pooled 0.516 as its
benchmark for a structural mark. That benchmark is wrong in both directions: 0.923 for a
unit-opening mark, 0.000 for a title-closing one. The four-dot's 0.106 sits further below
the first than the pooled comparison suggested. Its own coupling result (+4.02 against the
separator) is unaffected, as is the red-ink finding, which asks which words are red and
has nothing to do with line ends.
