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

## The remaining four: few alphabets, but not cycled

Pages 1, 2, 12 and 13 are the only material in the book at an intermediate index of
coincidence — above the unsolved corpus's 1.000, below the 1.52-2.06 of plaintext and
monoalphabetic ciphertext. That makes them the closest thing to a bridge between the
solved front matter and the unsolved body, so what kind of cipher they carry is worth
more than four pages of plaintext would be.

**The elevation is real.** Against a simulated flat null at each page's own length:

| page | runes | IoC | z vs flat | p | k (Friedman) |
|---|---|---|---|---|---|
| 1 | 251 | 1.227 | +7.72 | 0.0002 | 3.2 |
| 2 | 264 | 1.117 | +4.13 | 0.0012 | 6.2 |
| 12 | 226 | 1.071 | +2.18 | 0.028 | 10.3 |
| 13 | 93 | 1.281 | +3.45 | 0.0045 | 2.6 |

The alphabet count `k` uses the LP's **own** plaintext pages to fix the plaintext
level at 1.729, rather than importing a figure from English prose. So the elevation
implies only a handful of alphabets — roughly 3, 6, 10 and 3.

**But they are not cycled.** Nothing finds a period:

- Coset IoC at every period from 1 to 12 stays in 0.94-1.49 on all four pages. A real
  period-`k` cipher would put its cosets at the plaintext level of 1.73; none comes
  near. Period 8 looked briefly promising on pages 1 and 12 from autocorrelation, and
  its cosets sit at 1.22 and 1.12 — so it is not a period.
- Kappa autocorrelation to shift 25 gives a best of z = +3.1 to +3.7 per page. Across
  four pages and 25 shifts that is 100 tests, where the largest of 100 draws sits near
  +2.6 by chance, so nothing here survives its own multiple testing.

**And the elevation is not a plaintext region.** Windowed IoC (window 60, step 20)
stays in 0.90-1.44 across all four pages, never touching the 1.5-2.0 that a plaintext
or monoalphabetic window shows on pages 8 and 0. There is no readable patch raising a
flat average.

So these four pages use few alphabets, applied **aperiodically** — which is the shape
of the unsolved corpus's own family, only weaker. That is what makes them worth
attacking: the unsolved body is at IoC 1.000 and gives a search nothing to climb,
while these four leak 2 to 8 sigma of the same structure and are 93-264 runes long
instead of 12,956.

## Pages 1 and 2 are solved: DIVINITY, with an interrupted keystream

Plain Vigenere with the key DIVINITY decrypts page 1's first 49 runes exactly —
*WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END* — and then loses sync.
That is an interrupted keystream, so rather than guess what triggers the interrupt,
`experiments/interrupt_beam.py` searches the skip positions directly: at each rune the
keystream either advances or holds, and a beam scored by runeglish trigrams picks the
path. The answer can then be read off instead of assumed.

**Page 1, six interrupts, quadgram −4.40** (plaintext pages run −4.15 to −4.66):

> WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THNGS IT IS NOT
> AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE
> WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUF[F]ERING YOUR INNOCENCE YOUR
> ILLUSIANS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOUER AN END TO
> SEL[F]

Every one of the six skips falls on a ciphertext **ᚠ**, and the letters that go
missing if the skip is treated as a deletion are exactly the plaintext F's — *END
[OF] ALL*, *BUT [F]OR THOSE WHO [F]IND*. So the documented rule is confirmed from the
data: a ciphertext ᚠ can be a literal plaintext F that consumes no key.

**The detail that matters is that only SOME of them are.** Page 1 carries 14
ciphertext ᚠ and only 6 are interrupters. That is why `solved_page_keywords.py`, which
treated every ᚠ as an interrupt, scored DIVINITY below a meaningless key and reported
the whole family as a miss. The interrupt is a mark the scribe placed, not a property
of the rune, and no rule stated over the alphabet alone can recover it.

**Page 2, same key, quadgram −4.48:**

> …THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELUES AND OUR REALITI… JOURNEY DEEP
> WITHIN AND YOU WILL ARRIUE OUTSIDE LICE THE INSTAR… EACH INTELLIGENCE IS HOLY FOR
> ALL THAT LIUES IS HOLY AN INSTRUCTIAN COMMAND YOUR OWN SEL[F]

## What the beam can and cannot be trusted for

Skip count is the guard against the beam manufacturing English. Six binary choices
over 251 runes is negligible freedom and the output is clean, so page 1 is a solve.
Page 2's 24 skips over 264 runes is more latitude, and it is accepted on external
grounds — *EACH INTELLIGENCE IS HOLY*, *AN INSTRUCTIAN COMMAND YOUR OWN SELF* is LP
content, not an artifact a trigram beam would invent.

Pages 12 and 13 are **not** solved. Under DIVINITY the beam reaches only −5.86 and
−5.70 and needs 115 and 42 skips respectively — on 226 and 93 runes, that is nearly
one decision per two runes, which is enough freedom to fit noise. Their keys are
different and remain unknown.

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

- ~~a period estimate on those four~~ **done, and negative**: few alphabets (k ≈ 3-10)
  but no period, so a coset attack has nothing to split on;
- an aperiodic few-alphabet attack, which is the same problem the unsolved corpus
  poses but at 1/50th the length and with 2-8 sigma of leak instead of none;
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
- `experiments/poly_page_profile.py` — the elevation, diversity, period and locality
  tests on the four remaining pages.
- `experiments/interrupt_cipher.py` — the interrupter family with an exact round trip
  and a 6/6 planted-key control.
- `experiments/interrupt_beam.py` — the beam over skip positions that solves pages 1
  and 2 and reports which rune sits at each interrupt.

## Related

- `marks-are-not-clause-punctuation.md` — corrected by this file's classification.
- `no-known-plaintext-foothold.md` — its planted-key controls are the simulations this
  is meant to supplement.
- `running-key-math-sequence.md` — the source of the prime/totient keystreams and the
  ᚠ-interrupt convention.
