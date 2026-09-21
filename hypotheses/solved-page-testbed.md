---
type: observation
---
# Observation: Six Pages of the Transcription Are Literal Plaintext, and the Nine Enciphered ASCII-Convention Pages Resist the Obvious Families

## Feature

The master transcription's fifteen ASCII-convention pages (those writing the clause
delimiter as `.` rather than the 4/10/13-dot glyphs) are **not** the solved section,
which is what the convention was previously taken to mean. Scoring each as runeglish
splits them cleanly:

| | pages | quadgram score per rune |
|---|---|---|
| plaintext in the transcription | 3, 8, 9, 10, 11, 14 | −4.15 to −4.66 |
| still enciphered | 0, 1, 2, 4, 5, 6, 7, 12, 13 | −8.75 to −9.58 |

The six read directly as English — page 8 opens *"THE LOSS OF DIUINITY THE
CIRCUMFERENCE PRACTICES THREE BEHAUIARS WHICH CAUSE THE LOSS OF"*, page 14 *"AN
INSTRUCTIAN CWESTIAN ALL THNGS DISCOUER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH
IMPOSE NOTHNG"*. The gap between the two groups is over 4 nats per rune, so the
classification is not marginal.

**The nine enciphered pages are not cracked by any of:**

- identity, Atbash, all 29 shifts, Atbash composed with a shift in either order
- Vigenère, Beaufort, Atbash-then-Vigenère and Vigenère-then-Atbash, keyed by each of
  120 words from 3301's own vocabulary, each with and without the ᚠ-interrupt
- running keys from the primes (`p` and `p−1` mod 29) and from Euler's totient, in the
  same four families, with and without the interrupt

Best score reached on any of the nine is −6.90, against the −4.2 to −4.7 that the six
plaintext pages establish as what English looks like under this scorer. Nothing is
close.

## Status

**Status**: confirmed (measurement). `experiments/solved_page_testbed.py` classifies
the pages; `experiments/solved_page_keywords.py` runs the key families.

## Why this is worth having

Every positive control in this project is a simulation: prose enciphered with a
planted key, then recovered. That cannot catch a tokenization bug, a register
mismatch, or a scorer blind to real LP text, because the same code manufactured the
ciphertext it is being tested on.

The six plaintext pages are the author's own English, in the author's own runeglish,
with the author's own punctuation — 1,001 runes of it. Anything here that claims to
score LP-like text, or to measure a property of LP plaintext, can now be pointed at
real material instead of a simulation. `marks-are-not-clause-punctuation.md` already
uses them, and its spacing result was withdrawn precisely because the distinction
this file draws had not been made.

## The negative is load-bearing, so the search was controlled first

A key search that finds nothing is only informative if it would have found something.
Planting a key on page 8's real plaintext and running the same search:

| planted | recovered | score |
|---|---|---|
| DIVINITY [vigenère] | DIVINITY [vigenère] | −4.25 |
| CIRCUMFERENCE [beaufort] | CIRCUMFERENCE [beaufort] | −4.25 |
| WISDOM [vigenère then atbash] | WISDOM [vigenère then atbash] | −4.25 |
| DIVINITY [vigenère + ᚠ] | DIVINITY [vigenère + ᚠ] | −7.16 |

Four of four recovered exactly, three of them landing back at the plaintext score.
The search can see a key of the kind it is looking for, on genuine LP material.

## Limits

- **The interrupt family's control is weaker than the rest.** The planted
  interrupt case recovers the right key but scores −7.16 rather than −4.25, because
  the harness enciphers by skipping on a *plaintext* ᚠ while the decryption skips on a
  *ciphertext* ᚠ, which is the documented convention. The round trip is therefore not
  clean and the interrupt rows should be treated as under-tested rather than excluded.
- **"Not cracked" is not "unsolved".** These nine may well be solved in public by
  methods outside the families tried here; nothing in this repository records their
  keys, and this file does not claim they are open problems.
- The classification is of the transcription, not of the book: a page reading as
  plaintext means the transcriber recorded the decryption there, not that the page
  carries no cipher.
- 120 keywords is a small vocabulary and the families are the simplest ones. A wider
  sweep is cheap and has not been run.

## What would change it

Cracking any of the nine would add a genuine (ciphertext, key, plaintext) triple,
which is worth more than the plaintext alone: it would let a key search be validated
end to end on material the project did not manufacture. The cheapest untried
directions are a wider keyword list, keyed alphabets rather than keyed shifts
(Quagmire rather than Vigenère), and fixing the interrupt round trip.

## Scripts

- `experiments/solved_page_testbed.py` — classifies the fifteen pages and runs the
  shift/Atbash family.
- `experiments/solved_page_keywords.py` — the keyword and running-key families, the
  interrupt variants, and the planted-key control.

## Related

- `marks-are-not-clause-punctuation.md` — corrected by this file's classification.
- `no-known-plaintext-foothold.md` — its planted-key controls are the simulations this
  is meant to supplement.
- `running-key-math-sequence.md` — the source of the prime/totient keystreams and the
  ᚠ-interrupt convention.
