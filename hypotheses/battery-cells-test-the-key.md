---
type: observation
---
# Eleven of the Battery's Nineteen Cells Test the Key, Not the Mechanism

## Status

**Status**: confirmed. It retracts the model verdict recorded in
`models-on-the-informative-cells.md` earlier the same day, and corrects the
arithmetic that was used to retire `returns`.

## Claim

Every battery run in this directory has held one key and varied the corpus. That
answers *is the corpus a plausible draw from this model with this key*. It does not
answer *is the corpus a plausible draw from this model*, and for 11 of the 19 cells
the two questions have different answers.

Draw K keys, generate D corpora under each, and split the variance:

    within    sd across corpora at one key    -- the spread the battery already uses
    between   sd of the per-key means         -- the spread the battery never sees
    key ratio = between / within

Below 1 the cell is decided by the mechanism: every key agrees, so a miss is a
verdict on the shape. Above 1 it is decided by the key, and a miss says only that
this key was the wrong one.

## What was measured

`experiments/cells_that_test_the_key.py`, substitution preventer with τ fixing 8
points, **24 keys × 60 corpora**. `hit` is how many of the 24 keys put the corpus
inside their own 0.05 tail.

| cell | corpus | mean | within | between | key ratio | hit | verdict |
|---|---|---|---|---|---|---|---|
| d1w | 0.0063 | 0.0097 | 0.0013 | 0.0038 | 3.02 | 6/24 | key * |
| d2w | 0.0347 | 0.0355 | 0.0039 | 0.0095 | 2.44 | 17/24 | key |
| d3w | 0.0370 | 0.0413 | 0.0052 | 0.0103 | 1.98 | 15/24 | key |
| d4w | 0.0410 | 0.0367 | 0.0058 | 0.0048 | 0.84 | 23/24 | mechanism |
| d5w | 0.0492 | 0.0548 | 0.0084 | 0.0011 | **0.13** | 24/24 | mechanism |
| d6w | 0.0245 | 0.0404 | 0.0086 | 0.0076 | 0.88 | 11/24 | mechanism * |
| seam | 0.0079 | 0.0096 | 0.0019 | 0.0017 | 0.91 | 21/24 | mechanism * |
| d5x | 0.0347 | 0.0348 | 0.0018 | 0.0015 | 0.81 | 22/24 | mechanism |
| ioc | 0.9999 | 1.0029 | 0.0010 | 0.0083 | 8.04 | 21/24 | key |
| entropy | 4.8565 | 4.8534 | 0.0008 | 0.0094 | **11.03** | 21/24 | key |
| triplets | 0 | 3.62 | 2.05 | 2.36 | 1.15 | 14/24 | key |
| bigram_chi2 | 841.2 | 1208.6 | 85.7 | 270.3 | 3.15 | 4/24 | key |
| kappa_max_z | 2.91 | 4.00 | 1.06 | 1.10 | 1.04 | 22/24 | key |
| doublet_pos | 0.5532 | 0.5161 | 0.0481 | 0.0986 | 2.05 | 15/24 | key |
| doublet_gap_min | 6.0 | 1.62 | 0.95 | 1.35 | 1.41 | 7/24 | key * |
| returns | 1.0 | 0.0007 | 0.0054 | 0.0034 | 0.63 | **0/24** | mechanism |
| identical | 17.0 | 10.48 | 4.35 | 2.12 | 0.49 | 22/24 | mechanism |
| long | 0.0 | 0.22 | 0.46 | 0.06 | 0.13 | 24/24 | mechanism |
| clock | 1.0071 | 1.0054 | 0.0073 | 0.0092 | 1.26 | 23/24 | key |

**Eight mechanism cells, eleven key cells.** Two of the four cells the directory
calls reachable-informative — `d1w` and `doublet_gap_min` — are on the wrong side.

The draw count matters and the same run at 8 corpora per key gives a different
split: below 40 draws the empirical tail is one-sided, and the within-key spread is
badly estimated. **Only the 60-draw table above should be cited.**

## What this retracts

`models-on-the-informative-cells.md` recorded, hours earlier, that the substitution
preventer with τ fixing 8 lands all four reachable informative cells, calling it the
strongest model result in the directory. **That was one key.** The `hit` column
shows how thin the ground is: `d1w` is landed by 6 keys of 24, `doublet_gap_min` by
7, `d6w` by 11.

Scored at the mechanism level — for each of 24 keys, how many of the four that key
lands — the ranking inverts and the plain clock-dodge comes out ahead:

| shape | 0 of 4 | 1 | 2 | 3 | 4 of 4 | median |
|---|---|---|---|---|---|---|
| substitution | 1 | 9 | 7 | 6 | 1 | 2.0 |
| probabilistic | 3 | 10 | 5 | 4 | 2 | 1.0 |
| dodge | 1 | 5 | 9 | 6 | 3 | 2.0 |

The substitution preventer reaches 4 of 4 under **1 key in 24**. That is what the
earlier result was: a lucky draw, not a property of the substitution rule.

## And a correction to the arithmetic that retired `returns`

The same file argued that `returns` is unreachable by any unfitted key, because a
state return needs two of the 2,928 bases to coincide and that is about 10⁻²⁴.
**The premise is wrong.** `recurrence_counts` defines a return as two consecutive
*ciphertext* words of six runes or more repeating, which a base collision produces
but does not require — a chance ciphertext coincidence produces it too, at roughly
29⁻⁶ per shape-matching phrase pair.

Measured rather than assumed, the model produces one return in 1,440 corpora
(24 keys × 60), a rate of 7 × 10⁻⁴. That agrees with the independent estimate in
`dju-bei-is-more-surprising-than-recorded.md`, which puts the DJU-BEI event at 1 in
2,700, and it is twenty orders of magnitude from the figure committed earlier.

So `returns` is reachable, rare, and a genuine mechanism-level miss: 0 keys of 24
land it, and the key ratio of 0.63 puts it on the mechanism side. It stays out of
the *discriminating* set for a different reason — every model gives the same near-zero
rate, so it separates none of them — but "no unfitted key can produce it" is
withdrawn.

## The shapes are nearly indistinguishable anyway

`experiments/preventer_discriminator.py` runs the battery model-against-model rather
than model-against-corpus, 60 corpora per shape at one key. Separation is
`|mean_A − mean_B| / pooled sd`.

| cell | substitution | probabilistic | dodge | sep s–p | sep s–d |
|---|---|---|---|---|---|
| d1w | 0.0044 | 0.0041 | 0.0001 | 0.32 | **6.43** |
| seam | 0.0086 | 0.0102 | 0.0031 | 0.77 | **2.97** |
| bigram_chi2 | 909.1 | 809.7 | 809.6 | **2.14** | **2.31** |
| triplets | 1.97 | 0.50 | 0.00 | 0.88 | **1.25** |

**Four cells of 19 separate the shapes at all, and only two of the four
reachable-informative cells.** Fifteen cells are blind to which preventer is in use,
so even a correctly-scored landing count is mostly measuring the walk.

## A third instance of the same error, caught by this run

`doublet_pos` looked like a new failure of the substitution preventer: 0.400 ± 0.060
against the corpus's 0.553, while the dodge appeared to land it. Two controls
dissolve it.

- **The dodge's pass is empty.** It emits 0.6 within-word doublets per corpus, so
  the cell is undefined in 40 draws of 60 and is one doublet's position in the rest.
  The substitution preventer emits 40, against the corpus's 63 — the first time the
  cell has had anything to measure.
- **The early bias is not the preventer's and not structural.** The bare walk with
  no doublet rule gives 0.396 ± 0.037 at the same key, but over 40 random `g` the
  cell ranges 0.279 to 0.676 with mean 0.508, and the corpus's 0.553 sits at the
  65th percentile. 35% of keys reach or exceed it. Key ratio 2.05 in the table above.

Uniform rune placement in the LP's own word shapes gives 0.5010 ± 0.0210, so the
normalisation is unbiased and the corpus's late doublets are a real but modest
departure (z = +2.48). It constrains the key, not the shape.

## Correction to the `returns` row (same day)

`returns` is listed above as a mechanism cell that every shape fails identically. That
is true of its marginal value and false of its conditional one.
`the-chain-shows-only-in-extension.md` shows the cell is the base chain's only
observable once it is read as a rate per identical pair: a chained base extends one
repeat in 79, independent per-word draws one in 2,390. The corpus's single return is
about 30 times more likely under a chain.

So the cell carries information, but not in the form the battery reports it.

## Consequences

- No "model lands N cells" statement in this directory is evidence about a mechanism
  unless every cell counted is a mechanism cell, or the count is averaged over keys.
- The informative-cell programme needs restating: the question is *what fraction of
  keys make the corpus plausible*, not *does this key*.
- On that footing the three preventer shapes are within noise of each other, with the
  plain dodge marginally ahead — so the seam-ratio reasoning that motivated the
  substitution shape has produced no measurable gain.
- The battery keeps its value as a key filter. It is a poor model discriminator.

## Falsification

- A cell called mechanism-determined must keep key ratio below 1 at more keys and
  more corpora. `d4w`, `d6w` and `seam` sit at 0.84, 0.88 and 0.91 and could cross.
- The histogram must survive the draw count, which is why it is reported at 60 and
  not at the 8 the first run used.

## Scripts

- `experiments/cells_that_test_the_key.py`
- `experiments/preventer_discriminator.py`

## Related

- `models-on-the-informative-cells.md` — the file this retracts.
- `battery-cell-counts-are-not-evidence.md` — which warned the count was not a
  score; this says why, and that the problem is worse than counting.
- `seam-to-d1w-ratio-is-a-constraint.md` — the first instance of the error.
- `dju-bei-is-more-surprising-than-recorded.md` — the 1-in-2,700 figure the measured
  return rate now agrees with.
