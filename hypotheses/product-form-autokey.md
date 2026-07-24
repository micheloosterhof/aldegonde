---
type: hypothesis
---
# Hypothesis: Product-Form / Interpolation Autokey over GF(29)

> Harvested from an earlier investigation branch and re-verified July 2026:
> `experiments/product_form_ciphers.py` reproduces the joint two-tap split
> nIoC 1.028 (vs the forced ~1.7) and the fingerprint misses of forms F1-F5
> (F1 doublets 3.60% / 342 triplets, F5 6.56% / 1203 triplets vs LP
> 0.664% / 0). The two-tap split test here strengthens main's exclusion of
> ciphertext-autokey forms; it does NOT touch the length-clocked walk, whose
> alphabet depends on word position/state, not on (C[n-1], C[n-5]).

## Claim

The cipher is a deterministic algebraic rule over GF(29) in which
zero factors created by plaintext repeats generate the lag-5 and
doublet structure "for free", e.g.

    C(n) = C(n-5)*(P(n)-P(n-1)) + C(n-1)*(P(n)-P(n-5))   (mod 29)

or a variant with extra constants, subtraction, multiplication, or the
linear-interpolation form (the value at P(n) of the line through
(P(n-1), C(n-1)) and (P(n-5), C(n-5))), which yields literal equalities
C(n) = C(n-5) exactly when P(n) = P(n-5).

## Status

**Status**: disproved

## Why the idea is attractive

The zero-product structure ties C(n) to C(n-5) when the plaintext
repeats at distance 5 and to C(n-1) when it doubles — one algebraic
object appearing to explain both anomalies with no explicit rules.

## Evidence (the kill)

**Algebra first.** The proposed form is linear in P(n):
`C(n) = P(n)*(C(n-5)+C(n-1)) - [C(n-5)P(n-1) + C(n-1)P(n-5)]`. When
P(n) = P(n-5) it makes C(n) *proportional* to C(n-5)
(scalar P(n)-P(n-1)), not equal — literal equality only when the scalar
is 1 (~1/28 of cases), 28x too weak for the observed copies. Being
generically a bijection in P(n), every conditional event (doublet,
lag-5 match) occurs at ~1/29 — no suppression, no excess. And when
P(n) = P(n-1) = P(n-5), it forces C(n) = 0 (a ᚠ spike English would
produce ~50 times; the LP unigram distribution is flat).

**Simulation** (`experiments/product_form_ciphers.py`, 260k runes of
bag-of-words runeglish; LP targets in the header row):

| form | uni chi2 | dbl% | triplets | mono5% | d1/13k | usage in/cross |
|---|---|---|---|---|---|---|
| **LP** | 25.9 | **0.664** | **0** | 3.70 | **29** | word-aware ~25/~10 (marks) |
| F1 (proposed) | 42 | 3.60 | 342 | 3.79 | 21 | word-blind 9.5/8.6 |
| F2 (subtraction) | 80 | 3.56 | 326 | 3.78 | 22 | word-blind |
| F3 (constants) | 61 | 3.47 | 301 | 3.41 | 15 | word-blind |
| F4 (multiplicative) | degenerate | 99.97 | — | — | — | — |
| F5 (interpolation) | 47 | 6.56 | 1203 | 9.08 | 144 | word-blind 97/96 |

F1's zero-product does create a *mild* d1/d4-flavored excess (21 vs
chance 15.4) — the intuition pushes in the right direction — but it is
5x short on copy strength, has no doublet suppression (3.6% vs 0.664%),
produces hundreds of triplets (LP: zero), and is word-blind. The
interpolation form F5, which does produce literal copies, overshoots
catastrophically: it marks ~97% of ALL plaintext lag-5 repeats
including cross-word ones (LP usage is word-aware, ~25% in-word / ~10%
cross-word), CREATES doublets on plaintext doubles instead of
suppressing them, and floods the corpus with triplets.

**Class closure on the real corpus** (same script): the JOINT TWO-TAP
SPLIT TEST groups C(n) by the pair (C(n-1), C(n-5)) — 841 groups. For
ANY deterministic `C(n) = f(P(n), C(n-1), C(n-5))` injective in P(n),
each group is a substitution image of the plaintext and the mean group
nIoC must approach plaintext IoC (~1.7). Measured on the LP: **1.028**
— exactly the no-doublet-corrected random value (conditioning on
C(n-1) removes one candidate glyph: 29/28 = 1.036), nowhere near 1.7.
This closes every deterministic two-tap form at once — all four
variants above, any constants, any operations — extending the earlier
single-tap depth-1..8 split tests.

**The general obstruction** (from `README.md` structural constraint 1
and the reference-encoder note): deterministic emission cannot produce
the doublet suppression at all — for any fixed history exactly one
plaintext value creates a doublet, so the rate stays ~3.4%. The 0.66%
requires non-deterministic rejection (output-watching redraw). No
algebra escapes this.

## What survives

The observed structure needs exactly what the algebra cannot supply:
non-determinism (an OTP-grade key with a rejection rule) plus a
word-aware, shape-aware, sub-availability marking of plaintext repeats
— the conditional key-reuse / back-reference encoder of
`lag5-back-reference.md`.

## Scripts

- `experiments/product_form_ciphers.py` — all five variants simulated
  and fingerprinted; the joint two-tap split test on the real corpus.

## Related

- `lag5-back-reference.md` — the surviving mechanism family.
- `ciphertext-autokey.md` — single-tap deterministic feedback,
  disproved earlier by depth-wise split tests.
- `gematria-primus-arithmetic.md`, `experiments/gf29_battery.py` —
  earlier GF(29) arithmetic probes.

## Verdict

Disproved on four independent grounds: the algebra yields
proportionality rather than equality (28x too weak), deterministic
emission cannot suppress doublets, the simulated fingerprints miss on
every diagnostic (doublets, triplets, unigrams, usage word-awareness),
and the joint two-tap split test on the real corpus (mean group nIoC
1.028 vs the forced ~1.7) excludes the entire deterministic
f(P(n), C(n-1), C(n-5)) class in one measurement.
