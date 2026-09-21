---
type: observation
---
# Observation: On the Five Cells That Discriminate, No Model Scores Above 2 of 5

## The comparison the tally was standing in for

`battery-cell-counts-are-not-evidence.md` calibrates the fingerprint battery: twelve of
its nineteen cells are passed by any polyalphabetic cipher, which is exactly what the live
models report for themselves. Five cells are failed by every deliberately wrong model —
`d1w`, `seam`, `doublet_gap_min`, `d6w`, `returns` — and three of those five are about
**repeats**.

So the comparison worth making is on those five, and it had never been made. Scored by the
battery's own protocol, one key against 60 prose corpora:

| model | d1w | seam | gap_min | d6w | returns | |
|---|---|---|---|---|---|---|
| **corpus** | 0.0063 | 0.0079 | 6.0 | 0.0245 | 1.0 | |
| independent alphabet per rune | 0.0346 ✗ | 0.0344 ✗ | 1.0 ✗ | 0.0339 ✗ | 0 ✗ | **0/5** |
| one random alphabet per word | 0.0268 ✗ | 0.0350 ✗ | 1.07 ✗ | 0.0672 ✗ | 0 ✗ | **0/5** |
| plain walk, no doublet rule | 0.0165 ✗ | 0.0315 ✗ | 1.0 ✗ | 0.0234 ✓ | 0 ✗ | **1/5** |
| doublet-dodging walk | 0.0040 ✗ | 0.0001 ✗ | 11.7 ✓ | 0.0355 ✓ | 0 ✗ | **2/5** |

## What it shows

**The ordering is real and the tally hid it.** Over all nineteen cells these four models
score 12, 12, and around 12 — indistinguishable. Over the five that discriminate they
score 0, 0, 1 and 2. The dodge is ahead of the plain walk, and both are ahead of noise, by
a margin a tally cannot express.

**But nobody is close.** The best model reaches 2 of 5, and the two it misses worst are
the two it was built for: with this key it drives d1w to 0.0040 against the corpus's
0.0063 and the seam to 0.0001 against 0.0079 — over-suppressed, not under. The dodge's
rule fires too reliably.

**`returns` is missed by everything, 0 against 1.** That is the DJU-BEI state return, and
no model in this directory produces it. It has been known as an outlier; seen here it is
the single cell that separates the corpus from *every* candidate, wrong ones included.

## Correction: `returns` is unreachable by any unfitted key, so it is four cells not five

`returns` is scored against every model above and missed by all of them. It should not
have been scored at all.

A state return needs two of the 2,928 bases to coincide. With bases drawn effectively at
random from A₂₉ — which `base-family-is-the-symmetric-group.md` establishes and
`two-rune-depth-no-base-reuse.md` confirms empirically — that is

    4,285,128 pairs / |A₂₉| = 4.4 × 10³⁰  ≈  **10⁻²⁴**

So **no unfitted key can produce it**, and the cell measures the particular key rather
than the mechanism. Under the other reading — that the corpus's repeat is the 1-in-2,700
coincidence rather than a return — a model should produce a *repeat* at that rate, and
zero in sixty corpora is entirely consistent. Either way the cell carries no information
about the mechanism.

**The informative set is four cells**: `d1w`, `seam`, `doublet_gap_min`, `d6w`.

## And on four cells, one model lands all of them

The substitution preventer of `seam-to-d1w-ratio-is-a-constraint.md` — emit `τ(c)` on a
collision instead of re-running the clock — scored over 60 prose corpora:

| τ fixes | d1w | seam | gap_min | d6w | |
|---|---|---|---|---|---|
| corpus | 0.0063 | 0.0079 | 6.0 | 0.0245 | |
| 6 | 0.0034 ✗ | 0.0065 ✓ | 2.77 ✓ | 0.0237 ✓ | 3/4 |
| 7 | 0.0040 ✗ | 0.0075 ✓ | 2.62 ✓ | 0.0237 ✓ | 3/4 |
| **8** | **0.0046 ✓** | **0.0085 ✓** | **2.12 ✓** | **0.0237 ✓** | **4/4** |
| 9 | 0.0052 ✓ | 0.0099 ✓ | 1.20 ✗ | 0.0237 ✓ | 3/4 |
| 10 | 0.0056 ✓ | 0.0110 ✓ | 1.37 ✗ | 0.0237 ✓ | 3/4 |

**One integer of key is fitted** — how many points τ holds still — and it is fitted to the
doublet rate. The other three cells are free and land. τ = 8 is a sharp optimum: 6, 7, 9
and 10 all give 3 of 4.

That is a materially stronger statement than the "4 of 5" it replaces, and it is the
strongest model result in this directory. It is not a solution: four cells is four cells,
and `battery-cell-counts-are-not-evidence.md` is the reason to say so quietly.

## A caveat on the dodge's numbers

`dodge_three_cells.py` finds fixed-point sets landing d1w and the seam. That sweep varies
the **key** against one fixed prose corpus; the battery varies the **corpus** against one
key. They answer different questions, and the battery's is the harder one: a key that
lands a cell on one corpus need not land it across sixty. The set used here, {3, 16, 21,
26}, was the best from that sweep and still misses both cells under this protocol.

## Status

**Status**: confirmed (measurement, 60 prose corpora per model).
`experiments/informative_cell_comparison.py`.

## Related

- `battery-cell-counts-are-not-evidence.md` — which five cells and why.
- `doublet-dodge-walk.md`, `length-clocked-walk.md` — the models scored.
- `repeated-phrase-dju-bei.md` — the `returns` cell nothing reaches.
