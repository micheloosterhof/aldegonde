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
- **Interrupt-tolerant test** (`experiments/lp_attack_battery.py`): the solved
  "AN END" page used K[n] = prime(n) - 1 *with ᚠ-rune keystream interrupts*
  (some ciphertext ᚠ are literal plaintext F and consume no key). Interrupts
  desynchronize the keystream, so a plain positional IOC subtraction test
  would fail even with the correct sequence — a loophole in the evidence
  above. A beam search over interrupt choices (scored by runeglish trigram
  fitness) closes it: run per page with K[n] = prime(n) - 1 in both Vigenere
  and Beaufort sense, with and without atbash, it fully recovers the "AN END"
  plaintext from scratch (fitness -3.42 vs plaintext reference -3.31), but
  every unsolved page stays at random-level fitness (~ -6.2 vs random
  reference -6.84).

## Predictions

If the keystream is a known sequence, subtracting it from the ciphertext
should produce English-like IOC. None do.

## Verdict

Disproved for all tested sequences. If the keystream is mathematical, it's
not any obvious sequence.
