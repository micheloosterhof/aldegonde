---
type: observation
---
# Observation: The Four-Dot Gets No Line Break, and the Thirteen-Dot and Real Punctuation Both Do

## Feature

A mark "sits at a line end" when no rune follows it on its written line. Measured on the
body, with the ordinary word separator on the same pages as the baseline:

| glyph | count | at a line end | rate | z vs the word separator |
|---|---|---|---|---|
| word separator ① | 3,000 | 344 | 0.115 | — |
| **④** | 141 | 15 | **0.106** | **−0.30** |
| **⑬** | 31 | 16 | **0.516** | **+6.98** |
| ③ | 6 | 2 | 0.333 | +1.68 |
| ⑩ | 4 | 3 | 0.750 | +3.99 |
| `&` | 19 | 19 | 1.000 | +12.07 |
| `$` | 11 | 11 | 1.000 | +9.20 |

And on the author's six plaintext pages, where the `.` is genuine clause punctuation:

| glyph | count | at a line end | rate | z |
|---|---|---|---|---|
| word separator | 225 | 37 | 0.164 | — |
| **`.`** | 34 | 16 | **0.471** | **+4.49** |

**The four-dot against the author's own clause punctuation: 0.106 against 0.471,
z = −4.07.**

`experiments/which_mark_is_layout_coupled.py`

## Why this is not the pooled result already on record

`mark_forensics.py` reports the pooled figure — a mark at a line end 17.8% of the time
against 3.7% for the word separator, z = +9.67 — and treats it as layout coupling in
general. Split by glyph, **all of it is ⑬, `&` and `$`, and none of it is ④.**

## The control is internal, which is what makes it strong

⑬ and ④ sit on the same pages, in the same hand, under the same justification. The body's
lines are set as continuous justified text (21.75 runes, cv 0.124, 76% ending mid-word),
so a scribe who never broke a line for the text would show clustering for neither glyph.
He breaks for ⑬ half the time and for ④ never. No reference corpus is involved.

## Reading

When this author ends a clause he tends to end the written line there — 47% on his own
plaintext, and 52% at the ⑬ that `do_the_marks_bound_the_titles.py` confirms from red ink
is a section boundary. **④ shows no such tendency at all.** In layout terms it is
indistinguishable from an ordinary word break.

This is a **second channel, independent of every length statistic**, saying the same thing
as `sentences-do-not-end-long.md`: the four-dot does not behave like a clause terminator.

## Consequence for the two surviving readings

The two readings of the four-dot anomaly are "the words inside a span are transposed" and
"④ is not a sentence mark". Everything built recently —
`the-rearrangement-is-not-a-simple-rule.md`, `can_joining_alone_flatten_the_edge.py` —
rests on the block-length channel, which cannot separate them
(`lengths_cannot_separate_the_readings.py`).

**Layout coupling can, and it favours the second.** A transposition rearranges the words
inside a sentence; it does not move the sentence's end, so a scribe breaking his line at
clause ends would still break at ④. He does not. The simpler reading — ④ marks something
other than a clause end — explains the layout and the lengths at once, and needs no
rearrangement.

That does not retire the transposition reading. It says the evidence for it is confined to
one channel and a rival now has two.

## Falsifiable

- Find a body glyph that is layout-decoupled and still lengthens its preceding block.
- Show the author's plaintext line breaks track something other than clause ends — the
  47% would then not be a punctuation signature.
- Raise ④'s line-end rate above the word separator's on any subset defined without
  reference to lengths.

## A second physical channel agrees: the gap width

`experiments/does_the_scribe_leave_extra_space.py`

The transcription throws away how wide the space at each separator actually is. Measuring
it from the page images — connected components, whitespace defined as the rune-to-rune gap
minus the dot cluster's own width, normalised by each line's median word-break whitespace
so justification cancels:

| dots in the gap | pairs | mean | se | median |
|---|---|---|---|---|
| none (within a word) | 8,758 | 0.407 | 0.002 | 0.417 |
| one (a word break) | 2,392 | 1.007 | 0.005 | 1.000 |
| **four** | 90 | 1.230 | 0.109 | **1.000** |
| thirteen | 7 | 0.839 | 0.054 | 0.857 |

**The mean reads +2.04σ and the median reads nothing.** The four-dot's median whitespace
is exactly a word break's; a few wide gaps carry the mean. The typical four-dot is spaced
like an ordinary separator.

So two independent measurements off the scans agree: the scribe treated the four-dot as a
word break, not a structural pause. The line-end rate said 0.106 against the separator's
0.115; the gap width says 1.000 against 1.000.

The thirteen-dot row is unusable — most thirteen-dots sit at a line end, where there is no
following rune to measure against, leaving seven pairs.

**What is not done:** looking for wide gaps at positions carrying only a one-dot
separator. If the scribe left extra space at unmarked sentence ends, that would locate
boundaries independently of the glyphs, and the within-word / word-break separation
(0.407 against 1.007) shows the measurement is sharp enough to try.
