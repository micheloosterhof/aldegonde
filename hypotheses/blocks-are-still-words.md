---
type: observation
---
# Observation: The Blocks Behave Like Whole Words, Not Arbitrary Cuts


## The trend needs an error bar, and with one it is 1.75 sigma (October 2026)

This file compares point estimates: the body's d5 length-trend of +0.0369 against prose
words' +0.036 and arbitrary cuts' +0.0029. The floor argument is sound — attenuation can
only shrink an observed correlation, so the observed value bounds the plaintext's from
below whatever the leak fraction is. But a floor still has sampling error, and only
**806** of the body's blocks reach six runes and contribute a lag-5 pair at all.

`experiments/blocks_are_words_error.py` measures it two ways, which agree:

    naive Fisher se on the 2,073 pairs   0.0220
    bootstrap over the 806 blocks        0.0202
    95% interval                         [-0.0021, +0.0743]

| against | z |
|---|---|
| prose real words (+0.0169) | 0.99 |
| words with 2-rune joined at q = 0.40 (+0.0204) | 0.82 |
| **arbitrary cuts (+0.0016)** | **1.73** |

**So the test leans toward words and does not establish them**, and the 95% interval
reaches down to the cuts value. The third row is new: `short-units-are-written-joined.md`
says the body's blocks are words with the short ones joined, and that segmentation gives
+0.0204 — between words and the body, and indistinguishable from either.

This matters more than most weakenings, because E7 is what keeps every crib program
valid. If the blocks are cuts, an eight-rune block spans word boundaries and matches no
dictionary entry.

## Why it matters which

`separators-are-not-word-boundaries.md` shows the block lengths carry no language order.
Three readings survive that, and they are not interchangeable for anything downstream:

| | reading | crib programs |
|---|---|---|
| A | a **list** — blocks are words, in an order with no prose structure | valid |
| B | **reordering** — blocks are words, permuted | valid |
| C | **cuts** — blocks are arbitrary cuts of a continuous stream | **invalid** |

Under C an 8-rune block spans word boundaries and matches no dictionary entry, so
`d5_crib_targets.py`, the rubrication crib program and every length-matching argument
would be resting on a false premise. The distinction had not been tested.

## The d5 channel decides it

Under a letter step of order 5, positions five apart inside a block share an alphabet, so
`c[j] == c[j+5]` reads plaintext equality with no key. Two statistics of that channel
separate words from cuts, and both were **measured on runeglish prose rather than
assumed**:

| segmentation | d5 level | pairs | trend r | z |
|---|---|---|---|---|
| prose, real words | 0.0537 | 16,858 | **+0.0360** | +4.68 |
| prose, arbitrary cuts at the body's lengths | 0.0620 | 20,384 | **+0.0029** | +0.42 |
| **body, within-block** | **0.0492** | 2,073 | **+0.0369** | +1.68 |

The level goes the opposite way to intuition: cuts are *higher*, because a cut spans word
boundaries and English repeats common words at short distances.

**The body against each model:**

| | level z | trend z |
|---|---|---|
| vs real words | −0.90 | **+0.04** |
| vs arbitrary cuts | −2.42 | **+1.55** |

## The trend is the statistic that survives the leak

The d5 level is confounded by φ5, the fraction of d5 pairs that really share an alphabet,
which `period5-is-confirmed` records as undecidable between 0.64 and 0.85. Any level can
be matched by choosing φ5, so the level comparison is a lean at best.

The **trend** is not confounded in the same way. Chance matches — the (1−φ5) share —
carry no length trend at all, so attenuation can only *shrink* the observed correlation.
An observed r therefore sets a **floor** on the plaintext's r, whatever φ5 is:

> the body's blocks show r = +0.0369, so their underlying plaintext has r ≥ +0.0369.
> Real words offer +0.0360. Arbitrary cuts offer +0.0029.

Reading C would need the plaintext's trend to be an order of magnitude below what cuts
produce, in the wrong direction.

## Status

**Status**: confirmed (measurement) that the two models separate; the body's placement is
a **1.55σ lean toward words**, φ5-robust in the direction that matters.
`experiments/blocks_are_words.py`.

## What it settles and what it does not

- **Settles**: the crib programs' premise. A block is a word, so dictionary matching is
  legitimate, and reading C is disfavoured.
- **Does not settle**: A against B. Both keep blocks as words, and nothing here separates
  a list from a permutation.
- **Power**: 2,073 pairs is the whole d5 channel, so this cannot be sharpened without
  more corpus. A 1.55σ lean is what the data holds.

## Related

- `separators-are-not-word-boundaries.md` — the three readings.
- `period5-is-confirmed` (memory) — the key-free channel and the φ5 caveat.
- `crib-budget-for-g.md`, `rubrication-crib-candidates.md` — the programs this defends.
