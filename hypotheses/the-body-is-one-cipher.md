---
type: observation
---
# Observation: The Body Is One Cipher, Uniformly Applied — There Is No Weak Page

## What this checks

Every result in this directory pools all 12,956 runes of the unsolved body. That is right
only if the body is one cipher. If a single page or section were enciphered differently —
a shorter key, a lapse, an earlier variant — pooling would bury it, and that page would
be the obvious way in. Nobody had checked.

Three statistics carry the body's structure, and each has a clean homogeneity test
against its own pooled rate:

| statistic | pooled value | what it measures |
|---|---|---|
| within-block doublet rate | 0.0063 | the suppression |
| within-block d5 rate | 0.0484 | the period-5 echo |
| normalised IoC | ~0.99 | the alphabet count |

## Result: homogeneous at both grains

| grain | units | doublets | d5 | IoC spread |
|---|---|---|---|---|
| sections | 9 | χ² 5.0 on 8 df | χ² 4.1 on 8 df | sd 0.0070 |
| master chunks (pages) | 55 | χ² 62.0 on 54 df | χ² 46.7 on 49 df | sd 0.0385 |

Every test is below its 5% critical value (14.6, 14.6, 71.1, 65.3). The per-chunk IoC
spread of 0.0385 is *smaller* than the 0.0954 sampling alone predicts at those page
lengths, which is the mild over-dispersion correction a shared alphabet pool produces —
not a sign of mixture.

The most extreme page is chunk 64 at nIoC 0.825 on 66 runes, −4.20 sd — the shortest page
in the set, and low rather than high, which is the wrong direction for a weaker cipher.

## The positive control was unplanned and is the strongest part

The first run included master chunks 71 and 72. Chunk 72 is the Parable, stored as
**plaintext**, and it surfaced immediately at nIoC **1.819**, **+7.06 sd** from the
others. The test found the one non-ciphertext page in the range without being told it was
there.

So this is not a null with unknown power. **A plaintext or monoalphabetic page in the
body would be visible**, and there is none.

## Consequence

There is no page to attack first. Every foothold strategy that hopes for a weak spot —
a page with fewer alphabets, a lapse in the schedule, an earlier draft enciphered more
simply — is looking for something that is not there. The body has to be taken whole,
which is what `unicity-distance.md` already implies from the other direction: the key is
over-determined 69× by the full corpus, and correspondingly under-determined by any page.

## Scope

- Three statistics, not all statistics. A page differing in some way none of them
  touches would pass.
- The chunk grain is 55 pages of ~230 runes. `no-plaintext-window.md` closes that gap by
  sliding a window instead: at widths 100, 200 and 400 the body's most coincidence-rich
  stretch is *below* a shuffled corpus's, while a spliced plaintext passage is located
  exactly. Nothing hides between 100 runes and a page.
- Section 3 of the clean corpus is a 9-rune fragment and is dropped by the 50-rune floor.

## Status

**Status**: confirmed (measurement), with a positive control that detects the known
plaintext page at +7 sd. `experiments/section_homogeneity.py`.

## Related

- `unicity-distance.md` — the same conclusion from the information side.
- `flat-ioc.md`, `doublet-suppression.md`, `within-word-d5-coincidence.md` — the three
  pooled statistics this shows are safe to pool.
