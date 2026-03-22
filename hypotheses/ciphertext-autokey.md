# Hypothesis: Ciphertext Autokey Cipher

## Claim

The unsolved sections use a ciphertext autokey cipher (Vigenere or Beaufort
variant) with standard 0-indexed arithmetic.

## Status

**Status**: plausible

## Mechanism

In a ciphertext autokey cipher, each ciphertext rune feeds back as the key for
encrypting the next plaintext rune:

- Vigenere autokey: C[i] = P[i] + C[i-1] mod 29
- Beaufort autokey: C[i] = C[i-1] - P[i] mod 29

Under either variant, C[i] = C[i+1] (a doublet) implies that the plaintext
rune at position i+1 is the additive identity element (index 0, i.e. F/feh).

## Evidence for

- **Doublet-identity property**: Under ciphertext autokey, all 89 doublets
  decrypt to index 0 (the identity element). This is a mathematical certainty,
  not a statistical observation.
- **Flat distribution**: Autokey feedback naturally produces near-uniform output
  distributions from structured input.
- **No Friedman period**: Autokey ciphers have no fixed period, consistent with
  the Friedman test finding nothing.
- **Scrambled single-letter words**: Each word's encryption depends on the
  preceding ciphertext, explaining why single-letter words are uniformly
  distributed rather than concentrated on "a"/"I".
- **Historical precedent**: Cicada used Beaufort autokey in the solved LP
  sections.

## Evidence against

- **Simple autokey decryption has not cracked the text**: Decrypting with
  straightforward autokey (any key value) does not produce readable English.
  This suggests either additional layers, an unknown primer, or this hypothesis
  is wrong.
- **F frequency**: Under 0-indexed autokey, doublets correspond to F (feh) in
  the plaintext. The 0.68% frequency seems low for F in English text (~2.2%).

## Scripts

- `experiments/lp_ea_hypothesis.py` — Tests the autokey identity property and
  checks what plaintext rune doublets correspond to under various autokey
  models.
- `experiments/lp_deep_analysis.py` — General statistical analysis including
  doublet context and conditional probabilities.

## Verdict

Plausible. The statistical properties are all consistent with ciphertext
autokey, and Cicada has used it before. However, simple autokey decryption does
not produce readable text, and the F frequency mismatch (0.68% observed vs
~2.2% expected) is a concern. See also `beaufort-autokey-ea.md` for the
1-indexed variant where the identity element is EA instead of F.
