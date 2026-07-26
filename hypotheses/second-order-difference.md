---
type: hypothesis
---
# Hypothesis: Second-Order Difference Cipher

## Claim

The ciphertext is produced by a second-order difference operation:
C[i] = P[i] - 2*P[i-1] + P[i-2] mod 29, or a similar construction involving
second differences of the plaintext.

## Status

**Status**: disproved

## Mechanism

Rather than a first difference (delta) of the plaintext, the cipher computes
the second difference (delta of deltas). This would add an additional layer of
diffusion beyond first-order differencing.

## Evidence for

- Second-order differencing would flatten distributions effectively
- ~~Could potentially explain the doublet suppression~~ — it cannot: a
  ciphertext doublet under this mechanism needs a repeated value in the
  (second-)difference stream, and language deltas collide at or above the
  1/29 chance rate, so the mechanism predicts no suppression

## Evidence against

- **Direct inversion is flat (the decisive test, July 2026)**: if
  C = delta²(P), the plaintext is recovered by double cumulative sum up to
  a constant (IoC-invariant) and a linear ramp — 29 slope candidates. All
  29 are flat: nIoC 0.999-1.001 vs plaintext ~1.7
  (`experiments/second_order_closure.py`). No integration constant yields
  anything but noise.
- **Normal delta-of-delta doublets**: The delta-of-delta stream (second
  differences of the ciphertext) has a normal doublet count: 443 observed vs
  453 expected. (Weak on its own: under the hypothesis this stream is
  delta⁴(P), about which the claim predicts nothing sharp — kept only as a
  consistency note; the cumsum test above is the real kill.)

## Scripts

- `experiments/second_order_closure.py` — double-cumsum inversion over all
  29 ramp slopes (the direct test).
- `experiments/lp_deep_analysis.py` — delta and delta-of-delta doublet
  statistics.

## Verdict

Disproved by direct inversion: recovering P from C = delta²(P) is a double
cumulative sum with 29 ramp candidates, and every candidate has random IoC.
This is the exact analogue of the first-difference cumsum test and replaces
the earlier delta-of-delta argument, which tested a stream the hypothesis
makes no prediction about.
