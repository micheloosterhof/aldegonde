---
type: observation
---
# Observation: The Four-Dot Does Get Line Breaks — Weakly, and Far Less Than Real Punctuation

## RETRACTED AND REPLACED (September 2026)

**This file first claimed the four-dot gets no line break at all, at z = −0.30 against the
word separator. That was a contaminated baseline and the sign reverses.**

The baseline pooled `①` with ASCII `-`. In the body `-` is not a word separator: it is the
delimiter inside the **number-grid lines** on chunks 30 and 64, whose rows read
`3258-3222-3152-3038`. Those lines carry no runes, so nothing can follow a hyphen on them
and **every one of the 236 counted as line-final, at rate 1.000**. That inflated the body's
separator baseline from 0.039 to 0.115 and buried a real effect.

Excluding rune-free lines and using `①` alone:

| section | glyph | count | at a line end | rate | z vs that section's separator |
|---|---|---|---|---|---|
| the body | separator ① | 2,764 | 108 | 0.039 | — |
| the body | **④** | 141 | 15 | **0.106** | **+4.02** |
| the body | ⑬ | 31 | 16 | 0.516 | +13.63 |
| the body | ③ | 6 | 2 | 0.333 | +3.72 |
| the author's plaintext | separator ① | 205 | 17 | 0.083 | — |
| the author's plaintext | **`.`** | 34 | 16 | **0.471** | **+7.59** |
| the enciphered ASCII pages | `.` | 53 | 8 | 0.151 | +2.97 |

**The four-dot is layout-coupled.** It takes a line break 2.7 times as often as a word
separator does. What survives from the original reading is the comparison with real
punctuation: the author's own clause mark runs at 5.7 times its separator baseline, and
against it the four-dot is still low — 0.106 against 0.471, **z = −4.07**.

So the corrected statement is an intermediate one. The scribe breaks his line at a
four-dot more often than at a word break and much less often than at a clause end, with
the thirteen-dot (13.2× its baseline) behaving like a section boundary as the ink
independently says.

## What this costs elsewhere

The layout channel no longer supports "the four-dot is unrelated to the syntax". It was
reported as a second independent channel agreeing with the length evidence; it is not. The
length evidence (no sentence-final lengthening, −3.35σ) is untouched, and the
`does_the_scribe_leave_extra_space.py` gap-width result is untouched because it reads the
page images rather than the transcription — but those two now **disagree**, and that
tension is recorded at the end of this file rather than resolved.

## The original measurement, left for the record

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

**Both physical channels agree once the gap width is read correctly.** The median said
nothing because the effect is a minority one; the tail says otherwise. Share of gaps above
each percentile of the one-dot distribution:

| cutoff | one-dot | four-dot | ratio | z |
|---|---|---|---|---|
| p75 | 0.278 | 0.433 | 1.56 | +3.22 |
| p95 | 0.051 | 0.144 | 2.81 | **+3.92** |

So the four-dot gets extra space in roughly one occurrence in six, and a line break in
about one in ten (0.106 against a separator's 0.039). **The scribe gave it special
physical treatment in 10–20% of cases and ordinary word-break treatment otherwise** — two
measurements off the page images, agreeing.

The thirteen-dot row is unusable — most thirteen-dots sit at a line end, where there is no
following rune to measure against, leaving seven pairs.

**What is not done:** looking for wide gaps at positions carrying only a one-dot
separator. If the scribe left extra space at unmarked sentence ends, that would locate
boundaries independently of the glyphs, and the within-word / word-break separation
(0.407 against 1.007) shows the measurement is sharp enough to try.

### The gap-width channel is confounded by justification

`experiments/align_the_marks_to_the_image.py`

The mixture test's weak arm was the image reader's word lengths. That is fixable: take the
gap width from the image and the **length from the transcription**, matching them on pages
where the two four-dot counts agree exactly. This gives 52 marks with exact lengths,
against the line-end split's 14.

**RETRACTED.** This first reported a one-dot control at r = +0.397 on 93 marks and
concluded the channel was confounded outright. The transcription parser behind it reset
its rune counter at each line start (`body_parse.py`), and since pages were selected by
*exact count agreement* between image and transcription, the pages kept were those where
that parser's errors cancelled the image reader's. Selection by mutual error is not a
sample; corrected, the control collapses to 17 marks.

Measured on all 1,395 one-dot gaps with no count-agreement filter, the confound is real
and small: **r = +0.054 ± 0.027**, wide-minus-narrow +0.05 ± 0.12 — and the reader's
missed-rune artifact biases that negative, so it is a lower bound.

| mark | marks | wide-gap subset | narrow | difference | r |
|---|---|---|---|---|---|
| four-dot, aligned | 41 | 4.19 | 3.80 | +0.39 ± 0.63 | −0.128 |

**The channel is underpowered, not confounded** — the same verdict the line-end split
reached, for the same reason.

The alignment technique is worth keeping for any statistic not confounded this way. The
line-end flag is one — `are_some_four_dots_real.py` shows its control is clean — and it
lacks only marks.

Caveat: pages qualify only when image and transcription counts agree exactly, which is
easy for a few four-dots and hard for forty one-dots, so the four-dot row draws on 23
pages and the control on 3.

## A bound on the mixture: at most a sixth

`experiments/the_rank_of_the_last_block.py`

Every earlier test of the mixture used a **mean**, which is the wrong instrument: if one
span in five ends on a genuinely heavy word and the rest end anywhere, the mean moves by a
fifth of the effect. The **rank of a span's last block among its own blocks** is
reference-free — the span's multiset is its own control — and sensitive to a minority.

| corpus | spans | mean rank of the last block | a random block of the same spans | z |
|---|---|---|---|---|
| **the author** | 68 | **0.647** | 0.500 ± 0.030 | **+4.97** |
| **the body** | 129 | **0.481** | 0.500 ± 0.023 | **−0.86** |

Taking the author's lift as one genuine sentence end's contribution, the body's lift over
his is the fraction of four-dots that could be real:

**f = −0.135 ± 0.153 — so f < 0.17 at two sigma, f < 0.32 at three.**

**A large mixture is dead.** More than a sixth of four-dots being genuine sentence ends is
excluded.

**A small one is not, and the physical evidence points at that size.** The four-dot takes
a line break 10.6% of the time against a separator's 3.9%, and gets extra space in about
one occurrence in six. A mixture of one in ten would produce that coupling and sit inside
the bound. The two lines are consistent rather than in tension: a minority of four-dots may
be real sentence ends, small enough that no length statistic here can confirm it.

**A note on the cell that failed.** The natural statistic — the share of spans whose last
block is in the top tenth of its span's ranks — does not work, and the control says so: the
author reads only 0.044 there despite a +1.17 rune lift, because block lengths tie
constantly and a midrank rarely reaches 0.9. His mass sits at the 0.8 decile (0.31). A cell
the positive control cannot fill is not a test.
