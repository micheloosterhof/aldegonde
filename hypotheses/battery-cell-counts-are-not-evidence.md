---
type: observation
---
# Observation: A Maximally Wrong Cipher Lands 16 of the Battery's 19 Cells

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
| **independent alphabet per rune** | **16 / 19** | d1w, seam, triplets |
| one random alphabet per word | 12 / 19 | d1w, d3w, d4w, d6w, seam, triplets, kappa_max_z |
| plain Vigenère, key length 11 | 8 / 19 | eleven cells |

**A fresh random permutation at every position lands sixteen of nineteen.** It has no
structure whatsoever beyond being polyalphabetic, and it scores better than any model in
this directory reports.

## What follows

**A cell count is not evidence.** The baseline is 16, not 0, so "twelve cells land" is
four cells *worse* than a cipher built to have nothing in common with the corpus. Every
tally in this directory should be read against that number, and none of them beat it.

**The discriminating power sits in three cells.** All three wrong models fail exactly
`d1w`, `seam` and `triplets` — the within-word doublet rate, the seam doublet rate, and
the triplet count. Everything else is passed by construction by anything polyalphabetic.

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
- `triplets` is a count and is far from normal; it fails for all three wrong models and is
  worth separating from the two doublet cells in any future comparison.

## Status

**Status**: confirmed (measurement on three constructed ciphers, 20–25 prose corpora each).
`experiments/battery_null_calibration.py`.

## Related

- `doublet-dodge-walk.md` — the model whose real claim this clarifies.
- `length-clocked-walk.md`, `quagmire-odometer.md` — the other files reporting tallies.
