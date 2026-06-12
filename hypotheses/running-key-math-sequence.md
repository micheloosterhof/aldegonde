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

## Totient variants (June 2026)

3301 hinted at the Euler phi function and literally used phi(prime_n) as a
keystream on a solved page, so the totient family was re-attacked with
variants the original disproof did not cover
(`experiments/totient_strip.py` plus inline scans):

- **mod-28 keystreams against the inner J stream** (the 28-symbol step
  stream; note 28 = phi(29), so the inner cipher already lives in totient
  space), in BOTH doublet-interrupter alignments (doublets deleted /
  doublets as key gaps): primes, phi(prime), phi(n), Fibonacci, squares,
  triangular, both signs, 1,500 sequence offsets each — max nIoC 1.0030
  across 54,000 tests (an English residual would be ~1.5). Negative.
- **mod-29 keystreams against the doublet-COMPRESSED ciphertext** (same
  sequences, offsets, signs). Negative.
- **Solved-page-style rune interrupters**: key advances only when the
  ciphertext rune differs from a marker rune r, for all 29 candidate r,
  with phi(prime)/prime/phi(n) keys, 100 offsets, both signs — max nIoC
  1.0032 across 17,400 tests. Negative.
- **Discrete-log delta geometry**: lambda[i] = dlog(C[i]) - dlog(C[i-1])
  mod 28 over Z29* (three embeddings: index+1, GP mod 29, raw index). The
  apparent marginal anomaly (chi2 up to 311) decomposes exactly into the
  known doublet suppression (the lambda=0 cell) plus
  embedding-multiplicity artifacts (GP mod 29 is non-injective: F/I/D
  collide at residue 2, etc.); with the lambda=0 cell excluded and a
  corrected MC null, everything is flat. Negative.
- **Page 15 number grid**: the 3301-/+x prime table is known design (all
  16 cells decode to primes). The phi(3299)=3298 adjacency is a corollary
  of primes 2 and 3 being adjacent in that design, not an independent
  totient signature.

## Verdict

Disproved for all tested sequences, now including totient variants in
mod-phi(29)=28 space, doublet-interrupter alignments, compressed-stream
alignments, and rune-interrupter keying. If the totient hints are
architectural, the most economical reading is that the inner cipher
operating over 28 = phi(29) symbols (see `autokey-plus-substitution.md`)
IS the totient reference — not that phi generates the keystream.
