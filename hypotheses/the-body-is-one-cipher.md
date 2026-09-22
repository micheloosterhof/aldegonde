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

## The body's two halves also agree on the letter step, weakly

`experiments/do_the_body_halves_share_g.py`

The three statistics above — doublet rate, d5, IoC — carry no information about `g`. The
within-block d-profile does: the base cancels at every distance, so the rate at distance k
is set by g^(k mod 5), and d5 (identity power) is a plaintext control while d2, d3, d4, d6
and d7 carry the step.

The body's two halves, 1,464 blocks each, give **χ² = 6.9 on 5 df**, against a planted
same-`g` median of 7.3 and a different-`g` median of 23.3: **4.8 to 1 for one letter step
across the body.**

Weak, and the same strength as the front-matter claim withdrawn below. It is reported
because it agrees with every other statistic here, where that one stood against rune
frequencies at P = 5e-79 and a doublet rate at z = +4.16.

## WITHDRAWN: the enciphered front matter is a different cipher

**Scope: this withdrawal does not touch anything above it.** Constraint F1 in
`what-any-solution-must-satisfy.md` cites this file for the body's internal homogeneity,
which is unaffected — the withdrawal concerns only the comparison with the front matter.

`experiments/does_the_front_matter_share_g.py`

This file tests the body against itself. It does not compare the body with the nine
enciphered ASCII-convention chunks (0, 1, 2, 4, 5, 6, 7, 12, 13), which are still
unsolved and supply 1,796 runes in 467 blocks.

The instrument is the within-block d-profile. The base cancels at every distance, so the
rate at distance k is set by g raised to k mod 5. **At k = 5 the power is the identity**,
so d5 measures the plaintext alone and is a built-in register control; d2, d3, d4, d6 and
d7 carry g. d1 is unusable, because the body's adjacent rate is pushed down by the doublet
preventer and no other part of the book suppresses repeats.

| corpus | pairs | d2 | d3 | d4 | d5 | d6 | d7 |
|---|---|---|---|---|---|---|---|
| the body | 19,284 | 0.0347 | 0.0370 | 0.0410 | 0.0492 | 0.0245 | 0.0421 |
| the body, first half | 9,735 | 0.0370 | 0.0348 | 0.0364 | 0.0512 | 0.0172 | 0.0476 |
| the body, second half | 9,549 | 0.0324 | 0.0393 | 0.0457 | 0.0472 | 0.0318 | 0.0365 |
| the enciphered front matter | 2,218 | 0.0326 | 0.0430 | 0.0401 | 0.0586 | 0.0625 | 0.0986 |

Register control: d5 reads 0.0492 ± 0.0048 against 0.0586 ± 0.0158, **z = −0.57**. The two
sections do not differ in plaintext.

| pair | χ² on 5 df |
|---|---|
| the body's two halves (known same g) | 6.9 |
| **the body against the enciphered front matter** | **6.0** |
| simulated at these sizes, same g | median 5.1 |
| simulated at these sizes, different g | median 15.6 |

The observed 6.0 sits at 60.5% of the shared-g arm and 14.0% of the different-g arm:
a likelihood ratio of 4.3 to 1 for one letter step — **which is withdrawn.**
`experiments/the_preventer_is_only_in_the_body.py` settles it the other way by rune
frequency: the enciphered front matter is non-uniform at P = 5e-79, the body uniform at
P = 0.55, and the doublet rates differ at z = +4.16 (0.0241 against 0.0063). The
d-profile agreement was shared plaintext structure at distance five, not a shared key.

Weak, and reported as weak. The front matter supplies 2,218 within-block pairs against the
body's 19,284, and most of the χ² comes from d6 and d7, which have the fewest pairs.

Its value is mainly that `encipherment_does_not_break_the_link.py` uses the front matter
as its control for the sentence-final lengthening. That control is now somewhat better
founded and still not established.
