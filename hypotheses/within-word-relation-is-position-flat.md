---
type: observation
---
# Observation: Within-Word Coincidences Carry No Word-Position Structure, Which Disfavours One Global g

## Status

**Status**: confirmed (measurement, October 2026) for the flatness. The inference
against one global g is a Bayes factor of about e^5 under a uniform prior on g, not an
exclusion: a walk with an unusual g still fits.

## Claim

Inside a block the base cancels, so a lag-k coincidence reads a plaintext relation:

    c_i == c_(i+k)  <=>  p_i == R_(i,k)(p_(i+k))

The walk (`length-clocked-walk.md`) has R_(i,k) = g^k with one g for the whole body.
Then the coincidence rate at word position i passes the plaintext's position structure
(word-initial letters, the interiors of long words) through a fixed relation, and it
should vary with position. **It does not.** Across the five classes of i mod 5, at lags
2, 3, 4, 6 and 7, the body's rates are homogeneous: χ² H = 15.1 on 20 df (H5 = 13.7 on
the cells expecting 5 or more).

## Measurement

`experiments/within_word_relation_by_position.py --run`, 200 prose windows of the body's
2,928 words:

| model | mean H | min | P(H ≤ body) | P(H5 ≤ body) |
|---|---|---|---|---|
| walk, random g | 75.6 | 13.9 | 0.005 | 0.010 |
| walk, g fitted to the LP's d-values | 97.9 | 36.6 | 0.000 | 0.000 |
| dodge walk | 73.7 | 17.0 | 0.000 | 0.005 |
| five unrelated alphabets, word-anchored | 90.3 | 20.2 | 0.000 | 0.000 |
| walk, 2-rune words joined at q = 0.40 | 70.8 | 17.8 | 0.000 | 0.005 |
| walk, blocks re-cut at random | 19.5 | 7.6 | 0.210 | 0.490 |
| a fresh g for every word | 19.7 | 6.5 | 0.260 | 0.450 |
| walk with clock skips at q ≈ 0.2 | 44.4 | 10.7 | 0.020 | 0.035 |

**Word ends say the same, more strongly.** English endings (-S, -ED, -ING) are as
structured as beginnings, and one g passes them through too. Classing pairs by start
position {0, 1, 2+} and by the second rune's distance from the word end {0, 1, 2+}
(`--run --start-end`, 40 df): the body reads H = 28.9. Every one-g model above misses
in all 200 draws, with minima from 43 (clock skips) to 131 (fitted g). A fresh g per
word gives P = 0.08 and re-cut blocks P = 0.07.

Every model in which one relation serves the whole body and blocks are words lands far
above the body. The two models in which the relation does not track word position land
on it.

Checks:

- **Register.** Under the walk the author's own 723 words give H = 44.3 against 38.9
  for prose windows of the same size, so prose understates the position structure, if
  anything.
- **Tokenizer.** With page breaks joined (`load_clean(join_pages=True)`, 2,896 blocks)
  the body reads H = 15.7.
- **Fresh random runes** at every position give H ≈ 20, as a χ² on 20 df should.

## One g is not excluded, but it is disfavoured

`--fit`: a single g can match all 25 per-class body rates (misfit 3.6, lower than
planted walks reach). So the walk survives, but only with a g whose powers happen to be
flat across English word positions. About 1% of random order-5 g are. The g fitted to
the pooled d-values is not. On the 45 start-end cells the best g reaches 20.7, which is
what fitting a fresh-g corpus gives (22.2 ± 4.5): with about 80 bits in g, a fit can
absorb noise, so the fit is not evidence either way. The Bayes factor below is the
comparison that prices the freedom in g.

`--evidence`: a Bayes factor between one g drawn uniformly from the order-5
permutations with five 5-cycles, and a fresh such g for every word. Rates come from
prose position-class tables.

| | log evidence, one g against fresh per word |
|---|---|
| | start classes | start-end classes |
|---|---|---|
| body, converged (`--convergence`, 20 million sampled g) | −5.0 | about −10.5 (−10.3 to −10.8 from 10 million on) |
| body, each prose book held out of the tables (`--holdout`, 20,000 g) | −3.7 to −5.8 | −10.3 to −15.7 |
| planted walks on the held-out books | medians +11 to +36; at most 1 of 80 reach the body | medians +11 to +55; 0 of 80 |
| planted fresh-g corpora | median −4.0, range −7.6 to +4.3 | median −11.0, range −16.7 to −5.5 |

So the body looks like a fresh-g corpus and not like a walk: about e^5 ≈ 150 : 1 on
start classes and e^10.5 ≈ 36,000 : 1 on start-end classes, with a uniform prior on g.
The start-end figure is a Monte Carlo average dominated by rare g, and it was still
moving by about ±0.5 at 20 million samples. A designed g would have to be chosen for flatness across
word positions; the doublet-tuned g goes the other way.

**The datum against.** Lag 6 is low: 31 coincidences on 1,267 pairs, 0.0245, where a
fresh rich g per word predicts 0.0378 (z −2.44). The other four lags fit that model
(z −0.04, +0.13, +1.26, +0.63; χ² 8.0 on 5 df overall). A global g fitted to lag 6 can
match it, which is what the record has read as the g relation shared by lags 1 and 6.
The Bayes factor above includes those cells.

## What C-0 and F3 do and do not show

- **C-0** ("g has five 5-cycles", `d-profile-pins-g-to-five-cycles.md`). Its filter
  run on fresh-g-per-word corpora gives the same top-1% profile ([0 0 7 19 34],
  [0 0 12 20 28]) as on the body ([0 0 4 20 36]) (`--c0`). The profile records that
  the lag-k relations scramble the plaintext. It does not need one g.
- **F3** ("one g runs through the body at 5 to 1") compares the two halves' d-values.
  A relation that changes per word puts both halves near chance, so they agree as well
  as under one g. F3 separates one g from a g that changes at the midpoint, not from a
  g that changes at every word.

## Alternatives

| reading | H | status |
|---|---|---|
| (a) the relation changes per word: alphabet base_w ∘ g_w^j, g_w different each word, e.g. g conjugated by a per-word permutation | fits (P 0.26–0.45) | live; lag 6 at −2.44σ |
| (b) blocks are cut from the stream without regard to words | fits (P 0.21–0.49) | live on H; conflicts with the 2-rune excess after sentence marks, which needs blocks to start at words |
| (c) five fixed alphabets with a clock that runs through the text | body shows no absolute-position structure (H_abs 19.2, 20.3) where (c) gives 53–55 | disfavoured for the two clock conventions tried |
| (d) one g applied after the base, c_j = g^j(base_w(p_j)) | would leave a permutation-shaped excess in the ciphertext pair tables: +1.24 ± 0.96 for ten planted g, body −1.43 (`--cipher-side`) | disfavoured, 0 of 10 |
| the walk with one g | needs a g flat at both ends of words | disfavoured about e^10 under a uniform prior on g |

Additive per-word keys are already disproved (`within-word-key-sharing.md`); (a) is the
mixed-alphabet, equality-only version that test leaves open.

## Consequences

Programs that assume one global g lose their footing if (a) holds: the crib budget for
g (`crib-budget-for-g.md`), the injectivity constraints on (g, σ) from crib words, the
g constructions (`g-from-5x5-grid.md`, `magic-square-grid-key.md`), and any key search
over (g, σ). Under (a) each word carries its own step as well as its own base, and the
key-free channels say nothing about g beyond "order 5 inside a word".

The doublet suppression does not depend on this. It is in the emitted stream, not the
block's alphabet schedule (`separators-are-the-cipher-unit.md`, row D3), and the
preventer supplies it under either reading.

## Next tests

- Whether the per-word relations share a cycle type. Under (a) with conjugates of one
  g, every word's relation fixes exactly 4 runes, so plaintext repeats leak at 4/29 per
  lag. A relation drawn arbitrarily per word fixes 1 rune on average.
- The lag-6 deficit under (a): whether a preventer or clock rule can lower lag 6
  without position structure.

## Scripts

- `experiments/within_word_relation_by_position.py`: `--run`, `--fit`, `--evidence`,
  `--convergence`, `--holdout`, `--c0`, `--cipher-side`; `--start-end` for the joint
  classes.

## Related

- `length-clocked-walk.md`: the model this tests.
- `d-profile-pins-g-to-five-cycles.md` (C-0), `does_g_change_mid_book.py` (F3).
- `distance-6-has-no-power.md`: the lag-6 count.
- `within-word-key-sharing.md`: the additive version, disproved.
