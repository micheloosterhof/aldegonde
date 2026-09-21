---
type: observation
---
# One Skip Probability Reproduces Both the Doublet Rate and the Seam

## Status

**Status**: confirmed. It is the cleanest model fit in this directory — one parameter,
two independent observables, both landing — and it dissolves the seam-to-d1w ratio
constraint for good.

## The constraint that was never there

`seam-to-d1w-ratio-is-a-constraint.md` argued that the ratio of the seam rate to the
within-block doublet rate excluded the whole clock-perturbing family: the corpus reads
**1.25** while every dodge gave at least 1.91. That was retracted once the sweep behind it
was found to hold `g` fixed — varying `g` moves the ratio from 0.52 to 9.77 — but no
replacement was ever fitted.

Two corrections make the replacement possible.

- **The right parameter is φ**, the probability of acting on a would-be repeat, not a
  count of τ's fixed points (`survivors-use-every-rune.md` closes the substitution form)
  and not a derived percentage.
- **The right baseline is the walk without a preventer**, not 1/29
  (`how_strong_is_the_preventer.py`). Inside a block a would-be repeat needs the plaintext
  bigram mass on `g`'s graph; at a seam it needs the cross-word mass on `g^u ∘ σ ∘ g^v`.
  Both are key-dependent, which is exactly why the ratio moved so far.

## The fit

`experiments/one_phi_fits_both.py`, twelve keys, twelve prose corpora. The body reads
within-block d1 **0.0063** and seam **0.0079**, ratio 1.25.

| φ | within-block d1 | z | seam | z | ratio |
|---|---|---|---|---|---|
| 0.00 | 0.0415 ± 0.0155 | −2.27 | 0.0341 ± 0.0064 | −4.07 | 0.82 |
| 0.80 | 0.0108 ± 0.0033 | −1.37 | 0.0105 ± 0.0037 | −0.70 | 0.97 |
| 0.85 | 0.0090 ± 0.0026 | −1.01 | 0.0086 ± 0.0035 | −0.21 | 0.96 |
| **0.90** | **0.0071 ± 0.0020** | **−0.39** | **0.0075 ± 0.0036** | **+0.09** | 1.07 |
| 0.95 | 0.0050 ± 0.0019 | +0.67 | 0.0059 ± 0.0037 | +0.53 | 1.18 |
| 1.00 | 0.0031 ± 0.0021 | +1.53 | 0.0042 ± 0.0037 | +1.00 | 1.35 |

**Both observables sit within one sigma for φ ∈ [0.90, 0.95]**, and at φ = 0.90 they read
−0.39 and +0.09.

**The ratio falls out rather than being fitted**: 1.07 at φ = 0.90 and 1.35 at φ = 1.00,
bracketing the corpus's 1.25. There was never a tension. The 1.91 floor came from holding
`g` fixed, and the ratio of two key-dependent quantities was never going to sit still.

Note also the φ = 0 row: with no preventer the walk gives an **elevated** within-block
rate (0.0415, above chance, from `g`'s graph mass) and a **chance** seam (0.0341). The
body has both suppressed, and one φ does it.

## The preventer, fully characterised

Four measurements, none of which needs a key:

| property | value | source |
|---|---|---|
| reach | **strictly adjacent** — one rune back, nothing more | `the-preventer-is-strictly-adjacent.md` |
| failures | **rune-blind** — survivors use 28 of 29 runes at χ² 27.8 on 28 df | `survivors-use-every-rune.md` |
| form | **not a fixed substitution** — \|fix(τ)\| ≥ 28 and ≈ 5.6 cannot both hold | same |
| strength | **φ ≈ 0.90**, [0.90, 0.95] fitting both observables | this file |

The plain clock dodge is φ = 1 and sits at +1.53 and +1.00 — inside two sigma on both, so
**not excluded**, only mildly disfavoured against φ = 0.90.

## Falsification

- The fit uses twelve keys. If the key-to-key spread is underestimated the interval
  narrows and φ = 1 could fall outside; more keys is the direct check and it is cheap.
- The seam row assumes the base steps on the right, since the cross-word mass is on
  `g^u ∘ σ ∘ g^v`. Under the left action leaned to in
  `the-base-step-may-act-on-the-left.md` the seam's un-suppressed rate is an average over
  conjugates instead, which changes its spread but not its mean; the fit should be
  repeated for a left-acting walk.
- If the body's plaintext bigram mass on `g`'s graph is far from prose's, the φ = 0 row
  moves and every other row with it.

## Scripts

- `experiments/one_phi_fits_both.py`
- `experiments/how_strong_is_the_preventer.py`

## Related

- `seam-to-d1w-ratio-is-a-constraint.md` — the constraint this dissolves.
- `survivors-use-every-rune.md`, `the-preventer-is-strictly-adjacent.md` — the other
  three properties.
