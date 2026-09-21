---
type: observation
---
# Observation: A Non-Simulated Testbed — Six Transcription Pages Are Literal Plaintext, Five More Are Monoalphabetic and Now Recovered, Four Remain Polyalphabetic

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

**None of the nine is cracked by any of the keyed-shift families:**

- identity, Atbash, all 29 shifts, Atbash composed with a shift in either order
- Vigenère, Beaufort, Atbash-then-Vigenère and Vigenère-then-Atbash, keyed by each of
  120 words from 3301's own vocabulary, each with and without the ᚠ-interrupt
- running keys from the primes (`p` and `p−1` mod 29) and from Euler's totient, in the
  same four families, with and without the interrupt

Best score reached on any of the nine is −6.90, against the −4.2 to −4.7 that the six
plaintext pages establish as what English looks like under this scorer. Nothing is
close — because five of them are not keyed shifts at all, as the next section shows.

## Five of the nine are monoalphabetic, and are now recovered

The index of coincidence says why the keyword search above was aimed wrongly. IoC is
invariant under any monoalphabetic substitution, and normalised to 29 symbols it
splits the pages into three groups:

| group | pages | normalised IoC |
|---|---|---|
| plaintext in the transcription | 3, 8, 9, 10, 11, 14 | 1.52 – 1.96 |
| **monoalphabetic ciphertext** | 0, 4, 5, 6, 7 | 1.63 – 2.06 |
| polyalphabetic ciphertext | 1, 2, 12, 13 | 1.07 – 1.28 |
| the unsolved corpus, for scale | — | 1.000 |

Five pages sit in the plaintext IoC range, so they are simple substitutions on a
general keyed alphabet — which shifts and Atbash cannot reach, and which is why the
earlier family missed them. Steepest-ascent hill climbing over transpositions,
scored by runeglish quadgrams, recovers all five:

| page | runes | score | plaintext |
|---|---|---|---|
| 0 | 184 | −4.23 | A WARNING BELIEUE NOTHNG FROM THIS BOOC EXCEPT WHAT YOU CNO[W] |
| 4 | 209 | −4.05 | A COAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT |
| 5 | 210 | −4.09 | …AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PRO… |
| 6 | 218 | −4.19 | …O ARE YOU WHO WISHES TO STUDY HERE ASCED THE MASTER AGAI[N] |
| 7 | 141 | −4.20 | BUT HE COULD NOT THINC OF ANYTHNG ELSE TO SAY SO HE TRAILED |

All five land in the −4.05 to −4.23 band that the six plaintext pages establish as
English under this scorer. The solver was controlled first: a random key planted on
page 8's real plaintext is recovered exactly, at −4.25.

The keys and full plaintexts are written to `experiments/solved_page_triples.json`.
**That is the deliverable** — five genuine (ciphertext, key, plaintext) triples in the
author's own hand, against which any scorer or key search here can be validated
without manufacturing its own ciphertext.

What remains enciphered is four pages, 1, 2, 12 and 13, whose IoC of 1.07–1.28 is
below the plaintext range but well above the unsolved corpus's 1.000. That is the
signature of a polyalphabetic cipher with a short period, and it is the obvious next
target: a period estimate on those four is cheap and has not been run.

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

Four pages are still enciphered: 1, 2, 12 and 13. Their IoC of 1.07–1.28 sits below
the plaintext range and well above the unsolved corpus's 1.000, which is the signature
of a polyalphabetic cipher with a short period. The cheapest next steps, in order:

- a period estimate on those four (Friedman, or IoC by decimation), which is minutes
  of work and tells the search what it is aiming at;
- if a period falls out, solve each coset as a monoalphabetic with the climber that
  already works here;
- fixing the ᚠ-interrupt round trip, which is the one family whose control is weak.

Each of the four would add another genuine triple.

## Scripts

- `experiments/solved_page_testbed.py` — classifies the fifteen pages and runs the
  shift/Atbash family.
- `experiments/solved_page_keywords.py` — the keyword and running-key families, the
  interrupt variants, and the planted-key control.
- `experiments/solved_page_masc.py` — the IoC split and the substitution hill climber,
  with its own planted-key control.
- `experiments/solved_page_triples.json` — the five recovered triples.

## Related

- `marks-are-not-clause-punctuation.md` — corrected by this file's classification.
- `no-known-plaintext-foothold.md` — its planted-key controls are the simulations this
  is meant to supplement.
- `running-key-math-sequence.md` — the source of the prime/totient keystreams and the
  ᚠ-interrupt convention.
