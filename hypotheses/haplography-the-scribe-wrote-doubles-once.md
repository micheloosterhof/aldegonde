---
type: hypothesis
---
# Hypothesis: The Cipher Has No Repeat Rule; the Scribe Wrote Doubled Runes Once

## Claim

The body's doublet suppression is not part of the encryption algorithm. It is **runic
orthography**: in runic writing a doubled rune is written once, and the convention
applies across word boundaries as well as inside words. Applied to the ciphertext by
whoever prepared the exemplar, with about 80% consistency, it produces a suppression that
is boundary-blind, rune-blind, strictly adjacent and memoryless, and it lands the
within-word and seam rates together with **one** parameter. The cipher underneath needs no
dodge, no zero offset and no tuned diagonal.

## Status

**Status**: unresolved. Proposed 2026-10-25 in answer to the design objection that a
preventer "that only acts four times in five" is not something an author writes. One
recorded fact stands against it (below); one recorded file leaves room for it.

## Mechanism

Encipher with any carrier that changes alphabet every letter and has a period-5 letter
clock (a walk with an untuned g, or a Quagmire with a 5-rune keyword and two dials).
Then write the stream out, and whenever a rune would repeat the one just written, write
it once. The merge happens at a rate near 0.8; the 86 doublets of the body are the
places where it did not.

The reader who knows the key sees a stream with about 360 runes missing at unknown
places. Where a rune is missing, the decryption of the rest of the word is out of step by
one; a decryption must therefore allow an insertion at any position, which is a
beam-search cost comparable to the dodge's lookahead, not worse.

## Evidence for

`experiments/cipher_zoo_fingerprint.py`, six key draws, body in the first row:

| | d1w | seam | d4 | d5 | d6 |
|---|---|---|---|---|---|
| **body** | **0.0063** | **0.0079** | 1.19 | 1.43 | 0.71 |
| walk, untuned g, no rule | 0.0284 | 0.0351 | 0.93 | 2.12 | 1.27 |
| same, scribe writes doubles once at 0.8 | 0.0042–0.0071 | 0.0054–0.0072 | 1.23 | 2.04 | 0.91 |
| Quagmire, distinct-letter keyword, no rule | 0.0259 | 0.0370 | 0.80 | 2.12 | 1.07 |
| same, scribe at 0.8 | 0.0049–0.0058 | 0.0070–0.0074 | 0.86 | 2.05 | 1.17 |

- **One parameter lands both cells.** The within-word and the seam rate fall together
  because the convention does not know about separators. This is the fact D14 of
  `what-any-solution-must-satisfy.md` credits to a cipher-level preventer; a copyist's
  habit gives it with no cipher-level rule at all.
- **It is the only reading in which the 1/5 is nobody's design.** Under the dodge the
  surviving doublets are the failing phase of a schedule; here they are the copyist's
  lapses, and 80% consistency is an ordinary human rate.
- **The deletion leaves a trace at lag 4, and the body has it.** A dropped rune moves
  pairs that were five apart to four apart, so the lag-5 echo leaks into d4. The walk
  with the scribe reads d4 1.23 against 0.93 without; the body reads 1.19 against 1.01
  and 1.07 at lags 2 and 3. An inserted null would leak the other way, into d6, where
  the body reads a deficit (0.71). `null-rune-preventer.md` is the weaker reading for
  that reason.
- `the-preventer-is-in-the-stream.md` shows the suppression crosses written line breaks,
  and says in its own words that this excludes a rule applied by eye at write time but
  "not scribal at all": a convention applied to the exemplar before the page layout
  existed shows exactly that pattern.
- Zero triplets, the flat position profile of the survivors and their Poisson spacing
  (`doublet-spacing-poisson.md`) are what random lapses give.

## Evidence against

- **D8 is the obstacle.** `nothing-else-in-the-book-suppresses-repeats.md`: the
  author's own interrupted Vigenère pages carry doublets at chance (0.0300 on 834
  runes) and his monoalphabetic pages inherit the plaintext's doubles (0.0198). Whoever
  wrote those pages wrote doubled runes. The hypothesis then needs the body's exemplar
  to have been prepared differently from the solved pages'. `the-scribe-ignored-the-blocks.md`
  records that the body was laid out differently (lines broken mid-word 76% of the
  time, against word-boundary breaks on the readable pages), which is a different
  production mode but not proof of a different convention.
- The blocks get shorter by about 360 runes, while the body's blocks are already longer
  than the author's words (4.43 against 3.99). The joining of `short-units-are-written-joined.md`
  has to carry that too; its fit must be rerun with the deletion in front.
- The lag-5 echo stays at 2.0 in the simulation against the body's 1.43, as it does for
  every carrier in the zoo; the scribe neither helps nor hurts there.

## Predictions

1. **The d4 excess is the leak.** Under deletion the pairs now four apart that were five
   apart carry the echo, and their share is the deletion rate times five, about 14%. The
   body's d4 excess (1.19 against about 1.04 at lags 2–3) should be reproduced by a
   rule-free carrier plus the scribe at the rate that gives 86 survivors, and not by any
   insertion reading.
2. **Any key search may drop the dodge.** Decrypt with the plain carrier and a beam that
   allows one inserted rune per word at the positions where the decryption breaks. If a
   key is found, the inserted runes are the merged doubles, and each one should be a
   repeat of its left neighbour in the cipher's output.
3. **The exemplar, if it is ever found, has 447 doublets and the page has 86.**

## Consequences, 2026-10-25

**Not triplets.** Chance triplets in a flat stream of the body's length are about 16; under a
pair rule (XX → X, so XXX → XX) applied always they would be the only visible doublets, five
times too few. Under the stricter "never twice in a row" nothing survives. The 86 are the
copyist's lapses, with at most about nine former triplets under the pair rule; a lapse and a
former triplet are indistinguishable on the page.

**Decryption works the way the interrupter did.** On the solved Vigenère pages the reader
cannot tell an enciphered F from a passed-through F; the convention is resolved by reading
the plaintext. A dropped doubled rune is the same kind of convention with the same cost: a
word with a missing rune decrypts wrongly from that point, and the reader re-inserts the
rune where the sense breaks. Michel's point: 3301 has done exactly this before.

**It revives the simplest carrier.** `pure-quagmire-word-restart.md` disproved a 5-rune
keyword restarting at every word because a dodge at a fixed restart fails at every seam or
at none. With no dodge that argument has nothing to act on. Scored in the zoo
(`cipher_zoo_fingerprint.py`, six keys):

| Quagmire, keyword restarts per word, two dials with carry | d1w | seam | d2 d3 d4 | d5 | d5x |
|---|---|---|---|---|---|
| no rule, no copyist | 0.0342 | 0.0395 | 0.93 1.01 1.00 | 2.12 | 1.00 |
| no rule, copyist at 0.8 | **0.0079** | **0.0076** | 0.91 1.07 1.01 | 2.11 | 0.96 |
| body | 0.0063 | 0.0079 | 1.01 1.07 1.19 | 1.43 | 0.95 |

The restart anchors the echo to the separators (D1, D2) by construction, the two dials
supply 841 × 5 alphabets (A1), and the copyist supplies both doublet cells. The key is a
mixed alphabet, a 5-rune keyword and two dial starts, all enumerable, and the carrier
decrypts word by word, so a missing rune damages one word only. Length-clocked carriers
(the walk's chain depends on L_w) are the fragile ones under deletion: a dropped rune
changes the length the chain is clocked by.

What this carrier still misses, like every other: d5 at 2.1 against 1.43, and the DJU-BEI
return, which a word-count odometer does not produce at words 1477 and 2926.

## Scripts

- `experiments/cipher_zoo_fingerprint.py` — the scribe rows (`scribe(words, rate, rng)`).
- To write: the joining fit with deletion in front; a leak test on d4 by word length.

## Related

- `doublet-suppression-requires-design.md` — the theorem this escapes, since writing a
  rune once is not a bijection at that position.
- `explicit-doublet-avoidance.md` — tested increment and swap repairs, which inflate
  specific bigrams; deletion inflates none, which is why those tests do not reach it.
- `null-rune-preventer.md` — the insertion twin; the lag-4 / lag-6 asymmetry separates
  them.
- `the-body-is-machine-made.md` — a program that collapses repeated symbols is one
  line; it would run at 1.0, not 0.8, unless the 86 were reinstated.

## Verdict

Open, and the most economical account of the suppression in the directory: no rule in
the cipher, one human parameter, both rates, the lag-4 leak. D8 is what it has to
answer.
