---
type: hypothesis
---
# Hypothesis: First-Difference Cipher

## Claim

The ciphertext encodes the first differences of the plaintext:
C[i] = P[i+1] - P[i] mod 29.

## Status

**Status**: disproved

## Mechanism

Each ciphertext rune represents the difference between consecutive plaintext
runes. Decryption recovers plaintext by computing the running cumulative sum:
P[i] = (sum of C[0..i-1] + P[0]) mod 29, where P[0] is an unknown starting
value.

A doublet (C[i] = C[i+1]) requires P[i+2] - P[i+1] = P[i+1] - P[i]: the
same adjacent plaintext DIFFERENCE twice in a row. The rate of that event
is the collision probability of the difference distribution, ~3.6% for
runeglish (the difference stream has nIoC ~1.0501, see
`running-key-text.md`) — at or slightly above the chance rate of 1/29,
not suppressed.

## Evidence for

- Produces flat output distributions from structured input (differencing
  removes trends)
- Simple and elegant mechanism
- Decryption (cumulative sum) is straightforward

## Evidence against

- **Cumulative sum disproof**: Under first-difference, the running cumulative
  sum of the ciphertext IS the plaintext (offset by the primer). The IOC of
  this cumulative sum is 0.0345 for all 29 primers, indistinguishable from
  random. English runeglish IOC is 0.055-0.067.
- **Doublet rate disproof**: the mechanism predicts doublets at or above
  chance (~3.6%, the repeated-adjacent-difference rate). Observed: 0.66% —
  an independent second disproof.

## Scripts

None needed. The cumulative sum test is trivial.

## Verdict

Disproved. The cumulative sum of the ciphertext has random IOC (0.0345) for
every primer, but under first-difference it should equal the plaintext and
have English-like IOC (0.055-0.067). Independently, the mechanism predicts
doublets at or above chance (~3.6%) against the observed 0.66%.
