---
type: observation
---
# Observation: A Maximally Wrong Cipher Lands 12 of the Battery's 19 Cells

## The count that gets quoted

`length-clocked-walk.md`, `quagmire-odometer.md` and `doublet-dodge-walk.md` each report
their standing as a tally — "twelve free cells land, three do not" — and the tally is read
as support. `dodge_three_cells.py` showed the five-cell joint rate matching independence,
which raises the question nobody had asked: **what does a cipher with no relationship to
the corpus score?**

## Three deliberately wrong models

None has a letter step, an order-5 structure, a per-word step or a doublet rule — none of
the machinery this project models.

| model | lands | misses |
|---|---|---|
| **independent alphabet per rune** | **12 / 19** | d1w, d6w, doublet_gap_min, returns, seam, triplets, entropy |
| one random alphabet per word | 12 / 19 | d1w, d3w, d4w, d6w, seam, doublet_gap_min, returns |
| plain Vigenère, key length 11 | 5 / 19 | fourteen cells |

**A fresh random permutation at every position lands twelve of nineteen** — exactly what
the models in this directory report for themselves. It has no structure whatsoever beyond
being polyalphabetic.

**Corrected the same day.** The first version of this file said sixteen, from a run at 25
draws. The battery's tail is `2 · min(below, 1 − below + 1/n)`, which is **asymmetric**: a
corpus value above every model draw yields `2/n` at best, so at 25 draws it returns 0.08
and *cannot* register as a miss however wrong the model is. Forty draws is the minimum for
a two-sided test at 0.05; the battery's own `compare` uses sixty, and so does this now.
Three cells were mis-scored as landing.

## What follows

**A cell count is not evidence.** The baseline is 12, not 0, so "twelve cells land" is
exactly what a cipher built to have nothing in common with the corpus achieves. Every
tally in this directory should be read against that number, and none of them beat it.

**The discriminating power sits in five cells.** All three wrong models fail `d1w`,
`d6w`, `doublet_gap_min`, `returns` and `seam` — the within-word doublet rate, the
distance-6 coincidence, the minimum gap between doublets, the state-return count and the
seam doublet rate. Everything else is passed by construction by anything polyalphabetic.

Three of the five are about **repeats**: the rate within a word, the rate across a
boundary, and how far apart they sit. That is where a model earns its keep.

That reframes what the models are competing on. `doublet-dodge-walk.md`'s real claim is
not its twelve cells; it is that **d1w and the seam come out structurally**, from one rule,
with no tuned diagonal — and those are two of the three cells that carry information.
Stated as a tally that claim is invisible; stated against this baseline it is the strongest
thing the model has.

## Scope

- The three wrong models are a floor, not a distribution. A systematic null would draw
  many ciphers per family; three point estimates establish that the baseline is high, not
  exactly where it sits.
- The battery's tolerance is its own empirical two-sided tail at 0.05, unchanged here.
- `triplets` fails for the per-rune and Vigenère models but not the per-word one, so it is
  not in the common set; it is largely implied by `d1w` anyway, since a corpus with
  doublets at 0.0063 predicts about half a triple in 12,956 runes and has none.
- The draw count is part of the method, not a convenience: below forty, the test is
  effectively one-sided.

## Status

**Status**: confirmed (measurement on three constructed ciphers, 20–25 prose corpora each).
`experiments/battery_null_calibration.py`.

## Related

- `doublet-dodge-walk.md` — the model whose real claim this clarifies.
- `length-clocked-walk.md`, `quagmire-odometer.md` — the other files reporting tallies.
