# Hypothesis: Ciphertext Autokey Cipher

## Claim

The unsolved sections use a ciphertext autokey cipher (Vigenere or Beaufort
variant), with either standard or custom tabula recta.

## Status

**Status**: disproved

## Mechanism

In a ciphertext autokey cipher, each ciphertext rune feeds back as the key for
encrypting the next plaintext rune:

- Vigenere autokey: C[i] = P[i] + C[i-1] mod 29
- Beaufort autokey: C[i] = C[i-1] - P[i] mod 29
- Custom TR autokey: C[i] = TR[C[i-1]][P[i]]

Under any of these, C[i] = C[i+1] (a doublet) implies that the plaintext
rune at position i+1 is the identity element of the TR.

## Evidence for

- **Doublet-identity property**: Under ciphertext autokey, all 89 doublets
  decrypt to the identity element. This is a mathematical certainty.
- **Flat distribution**: Autokey feedback naturally produces near-uniform output
  distributions from structured input.
- **No Friedman period**: Autokey ciphers have no fixed period.
- **Historical precedent**: Cicada used Beaufort autokey in the solved LP
  sections.

## Evidence against

- **Preceding-rune split disproof**: Under ciphertext autokey with ANY TR,
  grouping all C[i] values by C[i-1] should produce 29 streams that are
  permuted versions of the plaintext. Since permutations preserve IOC, each
  stream's IOC should match English/runeglish IOC (well above 1/29 = 0.0345).
  Measured result: mean IOC across all 29 groups is 0.0354, indistinguishable
  from random. Every group is within 1.00-1.07x of random IOC. This rules out
  ciphertext autokey with any TR, standard or custom.
- **Single-letter word contradiction**: Under continuous autokey, grouping
  single-letter words by their preceding ciphertext rune should produce at most
  2-3 distinct values per group (for "a", "I", and possibly "O"). Observed:
  6-13 distinct values per group, all 29 groups exceeding 2. Independently
  rules out continuous ciphertext autokey.
- **Bigram split also random**: Splitting by (C[i-2], C[i-1]) gives mean IOC
  0.0348, also random. Rules out 2-deep autokey variants.

## Predictions

Under autokey, the preceding-rune split should produce English-like IOC.
It does not.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Splits ciphertext by preceding rune
  and computes IOC per group. Definitive disproof.
- `hypotheses/crib_single_letter_words.py` — Groups single-letter words by
  preceding rune. Shows 6-13 distinct values per group, far exceeding the 2-3
  expected.

## Related

- `beaufort-autokey-ea.md` — Specific variant with 1-based indexing. Also
  disproved by the same evidence.
- `plaintext-autokey.md` — Plaintext feedback variant, separately disproved.
- `multi-layer-autokey.md` — Multiple autokey passes, needs re-evaluation.
- `autokey-with-keyword.md` — Autokey + keyword, needs re-evaluation.

## Verdict

Disproved. The preceding-rune split test is definitive: under ciphertext
autokey with any tabula recta, splitting by C[i-1] must recover permuted
English letter frequencies (and thus English-like IOC). The observed IOC is
random. This applies to standard Beaufort, standard Vigenere, and any custom
TR.
