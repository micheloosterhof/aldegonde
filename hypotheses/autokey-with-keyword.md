# Hypothesis: Autokey with Keyword Interleaving

## Claim

A periodic keyword is added on top of a ciphertext autokey:
C[i] = P[i] + C[i-1] + K[i mod L] mod 29, combining autokey feedback with a
repeating key.

## Status

**Status**: disproved

## Mechanism

The autokey feedback provides the dominant encryption, but a short periodic
keyword K of length L adds an additional layer. The "identity rune" (the one
causing doublets) cycles through L different values depending on position mod L.

## Evidence for

- Explains why simple autokey decryption fails (the keyword is unknown)
- The Friedman test would not detect the keyword period because autokey
  feedback dominates the periodic component

## Evidence against

- **Split by (C[i-1], i mod L) disproof**: Under this model, grouping
  positions by both C[i-1] and (i mod L) fixes both the autokey key and the
  keyword offset, giving a fixed permutation of the plaintext. Each group's
  IOC should be English-like (0.055-0.067). Tested for all L from 2 to 29:
  mean IOC stays in the 0.034-0.037 range (random) for every L. No keyword
  period produces English-like IOC in any group.
- Plain ciphertext autokey (L=1) is disproved by the preceding-rune split
  test (see `ciphertext-autokey.md`).

## Scripts

None yet. The (C[i-1], i mod L) split test was run inline.

## Related

- `ciphertext-autokey.md` — Plain autokey (L=1 case) is disproved.

## Verdict

Disproved. Splitting by (C[i-1], i mod L) should isolate groups where both
the autokey key and keyword offset are constant. Every tested keyword length
(L=2 through 29) produces random IOC in these groups.
