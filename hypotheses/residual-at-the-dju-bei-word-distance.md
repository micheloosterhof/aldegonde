---
type: observation
---
# Observation: A Residual at the DJU-BEI Word Distance, +2.73σ With the Phrase Removed

## Feature

Compare word w with word w + 1,449, rune by rune from the start of each. 1,449 is the
word distance between the two occurrences of the repeated pair of blocks. With the
phrase's own two words dropped, the runes still agree more often than chance: 195 of
4,669, where 161 are expected.

`the-chain-shows-only-in-extension.md` records the figure (+2.73σ) under "no
word-clocked period at the DJU-BEI distance" and reads it as the phrase. It is not the
phrase: the phrase is removed. The distance was chosen by the phrase, so once the phrase
is out it is one pre-stated cell and its tail is its own.

## Measurement

`experiments/word_distance_residual.py`

| pairs | coincidences | rate | z against 1/29 |
|---|---|---|---|
| all, phrase included | 201 of 4,675 | 0.0430 | +3.19 |
| all, phrase removed | 195 of 4,669 | 0.0418 | **+2.73** |
| same-length words, phrase removed | 38 of 755 | 0.0503 | +2.39 |
| different lengths, aligned from the start | 157 of 3,914 | 0.0401 | +1.93 |
| different lengths, aligned from the END | 137 of 3,914 | 0.0350 | +0.18 |

- **Against every other distance.** The same statistic at the 2,726 other word distances
  has mean −0.04 and sd 1.00; six reach +2.73. Empirical P = 0.0026.
- **Size.** A full word-period would add 126 coincidences; the residual is 34, 0.27 of
  that. Among same-length pairs it is 0.59 ± 0.30 of the full rate.
- **Along the body.** In bins of 150 words: +1.4, +0.9, +0.7, +2.4, −0.6, +1.0, +0.4,
  +1.9, +0.1, +0.2. Nine of ten positive; nothing concentrated near the phrase.
- **By position in the word.** +2.0, +2.0, −0.2, +1.2, +2.2, +0.3 at positions 0 to 5.
- **Neighbours and divisors.** 1,448 reads −0.36 and 1,450 reads −1.44; the divisors
  483, 207, 161, 69, 63, 23 read between −0.96 and +1.21. It is 1,449 itself.
- **Alignment.** The effect is there when words are aligned from their starts and
  absent when aligned from their ends.

## Significance

About as strong as the lag-5 echo (family P 0.0045), on which rows C-0 to C9 and the
whole T2 tier were built. Nothing is built on this one, and nothing should be yet. It is
recorded because it was filed as explained when it is not.

What it would mean if real: about a quarter of the rune pairs 1,449 words apart share an
alphabet, start-anchored, everywhere in the body. A chain that returned with that period
would share all of them (287 hits, excluded at about 6σ). A key indexed by the word
number modulo 1,449 **and** by something the two words share about a quarter of the time
would fit; equal word length fits the same-length cell but leaves the different-length
cell at +1.93 unexplained. No model in this directory predicts a partial word-period.

## Status

**Status**: confirmed as a measurement; unexplained. One cell, P = 0.0026, no
independent replication possible on this corpus.

## Related

- `the-chain-shows-only-in-extension.md` — where the figure was first recorded.
- `repeated-phrase-dju-bei.md`, `dju-bei-stands-alone.md` — the phrase.
- `what-any-solution-must-satisfy.md` — T2's premise, the comparable signal.
