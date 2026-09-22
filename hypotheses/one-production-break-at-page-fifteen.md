---
type: observation
---
# Three Conventions Change at One Page, and One of Them Belongs to the Scribe

## The claim

The joining rate, the mark rate and the line measure all switch at page 14–15, each at
P < 0.0001 against a surrogate null for the scan maximum. Two of those describe the text
being copied; the third describes the person ruling the page. They change together.

Three observables, not four: the 13-dot is a further difference at this boundary but
cannot be scanned, since it does not occur before page 15 at all, and the interrupter
turns out not to be a phase convention (below).

| observable | kind | max | null | P | best split |
|---|---|---|---|---|---|
| blocks of length 2 | exemplar | 24.9 | 4.1 ± 2.4 | 0.0000 | p14: 0.243 → 0.159 |
| dot marks per rune | exemplar | 35.0 | 4.2 ± 2.4 | 0.0000 | p15: 0.0311 → 0.0139 |
| runes per line | **scribe** | 884.5 | 115.9 ± 74.1 | 0.0000 | p15: 19.03 → 21.77 |

## Why the line measure is the one that matters

`short-units-are-written-joined.md` already records an 8% line-measure difference and
treats it as weak support for a different hand, because of a confound: enciphered text has
no word shapes to break on, so a scribe fills to a measure where plaintext breaks at
sentence ends. That inflates any front-against-body comparison.

Measured directly, with paragraph-final lines dropped:

| step | change | z |
|---|---|---|
| **the confound**: plaintext → enciphered front matter | +1.14 ± 1.00 | **+1.14** |
| **the test**: enciphered front matter → the body | +2.07 ± 0.37 | **+5.57** |

The confound is not significant and the enciphered-against-enciphered change is, at
+9.7%. So the ruling changes at page 15 and the cipher is not what changes it.

## What it supports

A **single production break** at page 14–15 covering the exemplar and the ruling
together. That is reading 1 of `short-units-are-written-joined.md`, which survived by
elimination for a long time and is now carried by three measurements that change at one
place rather than one measurement compared across an assumed partition.

It fits the two neighbouring results: `where_the_joining_starts.py` finds no second
change point after page 14 (P = 0.77), and `the-body-is-one-uniform-text.md` finds the
body homogeneous across its ten sections. Pages 57–72 read 22.05 runes per line, still in
the body's regime.

## What it does not identify

Which of a different hand, a different pen, a different page format or simply a
different sitting produced the change. All four give this signature and the transcription
cannot separate them. Nor does it say anything about *why* the cipher also changes there.

## How to falsify

- **A fourth convention changing elsewhere.** ~~The interrupter is the obvious
  candidate~~ — **checked and withdrawn, September 2026.** Both halves of that were
  wrong. The key-free proxy exists and `interrupter_rule.py` already uses it: the rule is
  that every interrupt is a plaintext F passed through *literally*, so it shows as rune F
  and the rune-F rate measures it. And the convention does not belong to a phase at all —
  it appears on every polyalphabetic page the author solved, **including page 71, which
  is after the break**, and cannot appear on the monoalphabetic pages because they have no
  keystream to interrupt. It tracks the cipher, not the scribe, so there is no change
  point to find. See `the_interrupter_tracks_the_cipher.py`.
- **Page format.** If the physical page dimensions were known, a format change would
  explain the line measure without any change of hand, and the two exemplar observables
  would have to carry the break alone.

## Status

**Status**: confirmed. `experiments/three_conventions_one_boundary.py`.

## Related

- `short-units-are-written-joined.md` — reading 1, and the confound this clears.
- `the-body-is-one-uniform-text.md` — no further change after the break.
- `the-thirteen-dot-closes-a-section.md` — a fourth difference at the same boundary,
  not scanned because the 13-dot simply does not occur before page 15.
