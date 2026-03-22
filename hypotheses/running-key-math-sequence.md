# Hypothesis: Running Key from Mathematical Sequence

## Claim

The cipher uses C[i] = P[i] + K[i] mod 29 where the keystream K is derived
from a mathematical sequence (primes, Fibonacci, totient, etc.).

## Status

**Status**: disproved

## Mechanism

A deterministic mathematical sequence provides the keystream. Each element is
reduced mod 29 and added to (or subtracted from) the plaintext. No feedback;
the key depends only on the position i.

## Evidence for

- Cicada loves mathematical sequences (primes, totient)
- A long non-repeating sequence avoids Friedman period detection
- Simple and elegant

## Evidence against

- **IOC test**: Tried primes, GP primes cycling, naturals, triangular numbers,
  squares, cubes, Fibonacci, and Euler totient as keystreams. Both Beaufort
  and Vigenere modes with all 29 offsets. Every combination produces IOC
  ~0.0345, indistinguishable from random. English target: 0.055-0.067.
- These sequences are too "structured" to act as good keystreams — they have
  patterns that would partially cancel with English frequencies.

## Predictions

If the keystream is a known sequence, subtracting it from the ciphertext
should produce English-like IOC. None do.

## Verdict

Disproved for all tested sequences. If the keystream is mathematical, it's
not any obvious sequence.
