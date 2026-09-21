---
type: observation
---
# Observation: The Seam-to-Within-Word Doublet Ratio Measures g's Graph Mass

## The repair that works, and the one that does not

`models-on-the-informative-cells.md` scores the deterministic dodge at 2 of the 5
discriminating cells and shows *how* it fails: d1w at 0.0040 against the corpus's 0.0063,
the seam at 0.0001 against 0.0079. **Over-suppressed, not under** — the rule fires too
reliably. The obvious repair is to let it fire with probability φ.

That helps. At φ ≈ 0.8 the model reaches **3 of 5**, the best score in this directory:

| φ | d1w | seam | seam/d1w | gap_min | d6w | lands |
|---|---|---|---|---|---|---|
| **corpus** | **0.0063** | **0.0079** | **1.25 ± 0.30** | **6.0** | **0.0245** | |
| 0.00 | 0.0165 | 0.0315 | 1.91 | 1.00 | 0.0234 | 1/5 |
| 0.60 | 0.0066 | 0.0146 | 2.21 | 1.72 | 0.0238 | 3/5 |
| 0.80 | 0.0033 | 0.0089 | 2.68 | 4.82 | 0.0236 | **3/5** |
| 0.90 | 0.0017 | 0.0057 | 3.37 | 12.15 | 0.0239 | 3/5 |
| 1.00 | 0.0001 | 0.0031 | 48.34 | — | 0.0239 | 2/5 |

**But d1w and the seam cannot land together.** Fitting d1w at φ ≈ 0.6 overshoots the seam
by a factor of two; fitting the seam at φ ≈ 0.8 undershoots d1w by the same. The ratio
never falls below **1.91**, against the corpus's **1.25 ± 0.30**.

## Corrected the next day: it is a readout of g, not a family constraint

The sweep above varies φ with **g held fixed**, and the conclusion drawn from it — that
the family cannot reach the corpus's ratio — does not survive varying g.

Substituting on collision instead of skipping (`substitution_preventer.py`) keeps the seam
rate constant while d1w tracks **g's graph mass on the plaintext bigram table**,
Σₓ P(prev = g(x), cur = x). Over three order-5 permutations drawn from the extremes of
4,000:

| g's graph mass | d1w | seam | ratio |
|---|---|---|---|
| 0.0047 | 0.0014 | 0.0135 | **9.77** |
| 0.0317 | 0.0093 | 0.0136 | **1.46** |
| 0.0959 | 0.0259 | 0.0135 | **0.52** |

The seam does not move — it is context-free, as the mechanism says. **d1w scales with the
mass, and the ratio spans 0.52 to 9.77.** The corpus's 1.25 sits inside that range, at a
mass close to the median of random order-5 permutations (0.0317 over 4,000 draws).

So the ratio is not a barrier the dodge family fails. It is a **one-parameter readout of
g**, and the corpus's value corresponds to an ordinary g rather than a tuned one. The
1.91 floor reported below is the floor *for the single g those runs happened to use*.

**What survives, now calibrated.** Across eighteen order-5 permutations spanning the mass
range of four thousand, the relation is an inverse law — the numerator is the seam rate,
which does not depend on g at all:

    ratio = 0.0325 / mass(g),    mass(g) = Σₓ P(previous = g(x), current = x)

Inverting it on the corpus's 1.25 ± 0.30:

| | ratio | mass | percentile of random order-5 g |
|---|---|---|---|
| +1σ | 1.56 | 0.0209 | 15.8% |
| **point** | **1.25** | **0.0259** | **31.6%** |
| −1σ | 0.95 | 0.0343 | 59.5% |

**g's graph carries about 0.026 of the plaintext bigram mass**, below the 0.0345 an
unrelated graph would carry — its arcs avoid common adjacencies slightly. The one-sigma
interval spans the 16th to the 60th percentile, about **1.2 bits**: modest, and the first
measurement of g's *graph* rather than its cycle count
(`experiments/g_graph_mass.py`).

## Why the two contexts differ at all

The two contexts are not alike from the mechanism's point of view.

- **Inside a word** the base is constant, so a would-be repeat needs `g(p_j) = p_{j−1}`.
  It is *schedule-determined*, and the rule's failures are structured.
- **Across a seam** the base has just changed, so a would-be repeat is a chance event at
  roughly 1/29, and the rule's failures are unstructured.

A rule cannot change *which* of the two is which, but the size of the gap is set by g's
graph mass, and that is free.

This is the same conclusion `separators-are-the-cipher-unit.md` reaches from the other
direction: sliding every block boundary by a fixed number of runes leaves the doublet rate
unchanged (0.193 against 0.182) while destroying the d5 echo — so **the suppression
belongs to the emitted stream, not to the block schedule**. Two independent measurements,
one conclusion: whatever suppresses repeats does not know where the blocks are.

## Strength

The corpus's ratio rests on 63 within-word doublets and 23 at the seam: **1.25 ± 0.30**.
Read as a measurement of g's graph mass that is a wide interval, but it is the only handle
on that quantity in the directory.

## The substitution preventer, which came out of this

Substituting on collision — emit `tau(c)` for a fixed permutation tau instead of re-running
the clock — reaches **4 of 5** informative cells with tau fixing 8 points, the best score
in this directory. Its rate is set by how many points tau holds still, one integer of key,
and its seam rate is context-free by construction.

## Status

**Status**: the exclusion claimed in the first version is **retracted** — it held g fixed.
What is confirmed is that the ratio is a monotone readout of g's graph mass, spanning 0.52
to 9.77 over random order-5 permutations, with the corpus at 1.25 ± 0.30.
`experiments/probabilistic_preventer.py`, `experiments/substitution_preventer.py`.

## Related

- `models-on-the-informative-cells.md` — the five cells and the scores.
- `separators-are-the-cipher-unit.md` — the boundary-shift result this agrees with.
- `doublet-dodge-walk.md`, `quagmire-dodge.md` — the family constrained.
