---
type: observation
---
# Observation: The Base Family Passes a Sharpened 2-Transitivity Test, and Its One Blind Spot Is Harmless

## Why this matters

`local-channel-is-exactly-coincidence.md` proves that the only base-invariant statistic
of a within-word pair is whether the two runes are equal — so the local channel's 13
bits are the whole local channel, and no further local test can exist. The proof needs
one condition: the per-word base family must act **2-transitively** on the 29 runes.

That file checks the condition by measuring the within-word difference distribution,
since a family of pure shifts would preserve b − a. The differences are uniform, so the
family is not shifts. The check is sound but blunt in two ways: it spreads any signal
over 27 degrees of freedom, and shifts are not the natural non-2-transitive family.

## What the natural failures look like

The natural ones are the proper subgroups of AGL(1,29). For a base x → m·x + c with m
drawn from a multiplicative subgroup H of order k, the family is transitive but is
2-transitive **only when k = 28**. The invariant is not the difference; it is the coset
H·(b − a) in F₂₉*. With 28/k cosets, a chi² on 28/k − 1 degrees of freedom concentrates
what the 27-df test dilutes — by a factor of 27 at the quadratic-residue split.

Since 29 is prime, F₂₉* is cyclic of order 28, so k ∈ {1, 2, 4, 7, 14, 28}. k = 1 is the
plain difference test already on record. A second family is tested alongside: x → m·x
with no additive part fixes rune 0 and preserves the ratio b/a.

## Result: nothing, at any subgroup, any lag, either invariant

60 tests (5 within-word lags × 6 subgroups × 2 invariants), against a surrogate null
that shuffles the corpus and so reproduces the coset-size artifacts exactly. **The
largest deviation is z = +2.5**, which is what 60 tests produce by chance.

Lag 1, chi² / df:

| | k=1 | k=2 | k=4 | k=7 | k=14 |
|---|---|---|---|---|---|
| **body** | 34.3/27 | 17.2/13 | 9.1/6 | 1.8/3 | 0.0/1 |

The ratio invariant needs one correction to be read at all: a doublet gives ratio 1, and
doublets are suppressed, so the ratio-1 cell is depleted and the raw test reads z = +30
at every k. Excluding a = b — which is what the difference test already does by dropping
the zero cell — the signal vanishes entirely. This is the `bigram-ioc.md` trap again in
a new coordinate.

## Power: the scan sees H₂, H₄ and H₇, and is blind to H₁₄

Planting each family into the LP's own plaintext, at the body's size, one fixed g of
order 5 applied before the base:

| planted base family | k=1 | k=2 | k=4 | k=7 | k=14 |
|---|---|---|---|---|---|
| H₂ | 1285/27 | 1276/13 | 420/6 | 2/3 | 1/1 |
| H₄ | 454/27 | 438/13 | 420/6 | 9/3 | 5/1 |
| H₇ | 180/27 | 22/13 | 14/6 | **138/3** | 1/1 |
| H₁₄ | 45/27 | 19/13 | 13/6 | 6/3 | 1/1 |
| H₂₈ (2-transitive) | 34/27 | 10/13 | 6/6 | 5/3 | 0/1 |

The body reproduces the H₂₈ row almost cell for cell. H₂, H₄ and H₇ are excluded by one
to two orders of magnitude, and the concentration earns its keep at H₇, where the
targeted 3-df cell scores 138 while the blunt 27-df test manages 180 on nine times the
degrees of freedom.

**H₁₄ is not excluded, and the reason is g rather than the sample size.** The invariant
an H₁₄ base exposes is the quadratic-residue class of g^j(p_j) − g^i(p_i), not of
p_j − p_i. The LP's plaintext does carry a residue bias at lag 1 — chi² 2.9 on 1 df in
1,445 pairs, which scales to about 20 at the body's 9,965 — and with g the identity the
plant duly scores 18.6. With a non-affine g of order 5 it scores 0.79. **g scrambles the
residue classes before the base ever applies.**

## Consequence: the theorem's conclusion survives where its hypothesis is untested

The one surviving non-2-transitive family would expose one extra bit per pair, and that
bit is a function of g^j(p_j) − g^i(p_i). Unless g is affine, that is not a plaintext
statistic and carries nothing to read. So the local channel stays closed either way:
the orbit theorem's conclusion holds whether or not the family is exactly 2-transitive.

The escape hatch this leaves is narrow and named: **an affine g together with an H₁₄
base family**. `mobius-order5-thirty-points.md` and `g-from-5x5-grid.md` bear on whether
g can be affine at all — an affine map of order 5 on F₂₉ needs m of multiplicative order
5, and 5 does not divide 28, so the only affine maps of order 5 are translations, which
`local-channel-is-exactly-coincidence.md` already excludes by the uniform difference
distribution. **The hatch is shut.**

## Status

**Status**: confirmed (measurement with positive controls), n = 9,965 within-word pairs
at lag 1. `experiments/coset_invariant_scan.py`, `--power` for the planted table.

## Related

- `local-channel-is-exactly-coincidence.md` — the theorem whose condition this sharpens.
- `bigram-ioc.md` — the doublet trap, met again in ratio coordinates.
- `mixed-alphabet-vigenere.md` — the shift-family case, already excluded.
