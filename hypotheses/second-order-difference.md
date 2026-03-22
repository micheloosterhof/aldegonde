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
- Could potentially explain the doublet suppression

## Evidence against

- **Normal delta-of-delta doublets**: The delta-of-delta stream (second
  differences of the ciphertext) has a normal doublet count: 443 observed vs
  453 expected. If the cipher were a second-order difference operation, the
  second-difference stream would show anomalous statistics, but it does not.

## Scripts

- `experiments/lp_deep_analysis.py` — Computes delta and delta-of-delta
  streams and their doublet statistics.

## Verdict

Disproved. The second-difference stream has normal statistics, which is
inconsistent with a second-order difference cipher.
