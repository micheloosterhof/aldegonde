---
type: observation
---
# g's Bigram Graph Mass Cannot Be Recovered, Because the Preventer Hides It

## Status

**Status**: confirmed negative. C-1's 0.026 is withdrawn with no replacement, and the one
route that could still close the system is named.

## The quantity

C-1 records that g's graph carries about 0.026 of the plaintext bigram mass. The quantity
is

    m₁(g) = P(p_i = g(p_(i+1)))

— how often the cipher *would* emit an adjacent repeat if it had no preventer. It is a
real and important number: it is what the preventer acts on, and it is the only numerical
constraint on `g` beyond its cycle structure.

C-1 was read off the seam-to-within-word ratio, which
`one-parameter-fits-both-suppressions.md` dissolved. So the question is whether anything
else supplies it.

The body's within-block d1 is that rate *after* suppression:

    observed d1 = f(m₁, φ) = 0.0063

**One equation, two unknowns.** Pin either and the other follows.

## The obvious route fails

The d-profile filter constrains `g` through lags 2, 3, 4, 6 and 7. **Lag 6 uses the same
power of g as lag 1**, so it looks like the way in.

`experiments/graph_mass_is_not_recoverable.py`, 4,000 order-5 permutations:

| lag | g power | mean mass | sd | correlation with lag 1 |
|---|---|---|---|---|
| 1 | g¹ | 0.0309 | 0.0110 | 1.000 |
| 2 | g² | 0.0353 | 0.0087 | −0.076 |
| 3 | g³ | 0.0456 | 0.0104 | −0.207 |
| 4 | g⁴ | 0.0435 | 0.0080 | −0.047 |
| **6** | **g¹** | 0.0496 | 0.0117 | **−0.134** |
| 7 | g² | 0.0518 | 0.0127 | −0.112 |

**Same power of g, correlation −0.13.** English has strong bigram structure and almost
none at distance six, so `m₁` and `m₆` are near-independent functions of the same
permutation.

And the filter confirms it directly — the g it keeps have the same bigram graph mass as
the ones it discards:

| g population | m₁ |
|---|---|
| all 4,000 | 0.0309 ± 0.0110 |
| top 5% by the d-profile | 0.0313 ± 0.0121 |
| top 1% by the d-profile | 0.0312 ± 0.0112 |

## Nor does the seam

The seam adds a second equation and a **third** unknown — the cross-word mass on
`g^u ∘ σ ∘ g^v` (`the-preventer-is-strictly-adjacent.md`). Two equations, three unknowns.
The system does not close.

## The one route left

If the base steps on the **left**, the seam's un-suppressed rate averages over conjugates
of a single step. Conjugates share a cycle type, so that average is nearly a constant
rather than a free parameter — and the system would close, giving both `m₁` and `φ`.

That depends on `the-base-step-may-act-on-the-left.md`, which is a lean at about two
sigma from three converging measurements, not a settled fact. It is the only reason left
to care which side the step acts on.

## Consequences

- **C-1 is withdrawn.** 0.026 has no support and nothing replaces it.
- `g` is constrained by its cycle structure (C-0, five five-cycles) and by nothing
  numerical.
- The φ ≈ 0.90 of `one-parameter-fits-both-suppressions.md` is conditional on prose
  supplying `m₁`. It is a fit given a plaintext model, not a measurement of the cipher.

## Falsification

- If some statistic correlating with `m₁` above about 0.5 exists, the recovery works.
  Six lags were checked and the best is −0.21.
- A solved body page gives the plaintext directly and with it `m₁` for any candidate `g`,
  which would close everything at once.
- If the left action is established, redo the seam arithmetic and the system closes
  without new data.

## Scripts

- `experiments/graph_mass_is_not_recoverable.py`

## Related

- `one-parameter-fits-both-suppressions.md` — which dissolved C-1's derivation.
- `d-profile-pins-g-to-five-cycles.md` — the filter, which constrains cycle structure and
  not this.
- `the-base-step-may-act-on-the-left.md` — the lean that would close the system.

## The firing rate is recoverable even though m₁ and φ are not

`experiments/measure_the_drift_from_d5.py`

This file concludes that m₁ and φ form an underdetermined pair — one equation, two
unknowns — and that neither can be recovered. That is right for those two, and it is not
right for the quantity most of the directory actually needs.

    q = φ · m₁          (the preventer's firing rate)
    observed = (1 − φ) · m₁ = 0.0063
    ⇒  q = m₁ − observed

**φ cancels.** The firing rate depends on m₁ alone, so the prior on m₁ (0.0309 ± 0.0110
over order-5 permutations) transfers directly: **q = 0.0246 ± 0.0110**.

That matters because q is what every drift correction here needs — the `(1−q)^k`
attenuation on the d-profile, and the d5 recalibration in
`within-word-d5-coincidence.md`.

**And it can be checked independently.** The d5 attenuation gives a second estimate from
completely different inputs — the distance-5 rate against a length-matched English
reference rather than the adjacent rate against a prior over g:

| source | q |
|---|---|
| the doublets | 0.0246 ± 0.0110 |
| the d5 attenuation | 0.0949 ± 0.0573 |
| difference | +0.0703 ± 0.0583, **z = +1.20** |
| combined | **0.0271 ± 0.0108** |

They agree at 1.2σ with nothing tuned to make them meet — a consistency check on the walk
plus preventer.

**Assumptions:** the arithmetic takes a firing to always remove the doublet (otherwise q is
overestimated), and the d5 arm inherits the English-register question.
