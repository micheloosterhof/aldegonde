---
type: disproof
---
# Disproof: The Block Lengths Were Not Chosen to Steer the Key

## An attractive common cause

`what-any-solution-must-satisfy.md` names two facts a solution has to *explain* rather
than merely satisfy: the block lengths are detached from everything (E1/E2), and there is
exactly one state return, at the end of the body (D6).

One hypothesis covers both. Under the walk the base steps by `g^(a_w) ∘ σ`, where the
exponent **a_w = (cumulative runes − 1) mod 5** is fixed by the block lengths. An author
who chooses where the blocks break chooses the exponent sequence — and an author who
chooses the exponent sequence can force the product back to the identity after 1,449
blocks. The lengths would be detached from the plaintext because they are attached to the
**key**, and the return would be the thing they were arranged for.

It is the only idea so far that would make both facts one fact.

## It predicts structure, and there is none

| test | observed | null | |
|---|---|---|---|
| exponent marginal | [571, 596, 599, 596, 566] | uniform 586 | χ² 1.7 on 4 df |
| autocorrelation, lag 1 | −0.164 | −0.146 ± 0.014 | **z = −1.3** |
| lag 2 | +0.023 | +0.020 ± 0.017 | +0.1 |
| lag 3 | −0.015 | −0.003 ± 0.020 | −0.6 |
| lag 5 | −0.009 | −0.002 ± 0.017 | −0.4 |
| Σ exponents over the gap, mod 5 | **0** | 17.7% of shuffles give 0 | chance 20% |

The marginal is uniform, every autocorrelation sits on its null, and the one arithmetically
suggestive observation — the exponent sum over the gap being ≡ 0 mod 5 — lands exactly on
its chance rate.

**The block lengths were not chosen to steer the key.** The two unexplained facts stay
unconnected.

## The null decided this, and the obvious null is wrong

Exponents are a **deterministic transform** of the lengths — cumulative sums mod 5 — so a
null that shuffles the *exponents* destroys the modular arithmetic along with the
hypothesis, and then reports the arithmetic as a finding:

| lag-1 autocorrelation | value |
|---|---|
| observed | −0.164 |
| null from shuffled **exponents** | +0.019 → **z = −8.9** |
| null from shuffled **lengths**, re-transformed | −0.146 → **z = −1.3** |

The −8.9 σ is entirely the mod-5 wrap: when a_w is 4 and a length is added, the value
usually wraps to something small, so consecutive exponents are negatively correlated in
*any* such sequence. Shuffling the exponents removes that; shuffling the lengths preserves
it.

> **When a statistic is a deterministic transform of the data, the null must shuffle the
> input and re-apply the transform.**

That is the third time in this session the choice of null has decided an answer, after the
scan maxima and the analytic window formula.

## Status

**Status**: disproved (measurement against a transform-preserving null).
`experiments/length_steers_the_key.py`.

## Related

- `separators-are-not-word-boundaries.md` — the detached lengths.
- `dju-bei-needs-a-product-step.md` — the product whose exponents these are.
- `what-any-solution-must-satisfy.md` — the two facts this tried to join.
