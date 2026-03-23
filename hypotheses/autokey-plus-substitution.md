# Hypothesis: Autokey Outer Layer + Unknown Inner Layer

## Claim

The cipher has (at least) two layers: an outer ciphertext autokey
(Beaufort/Vigenere) and an inner transformation. The delta text
D[i] = (C[i-1] - C[i]) mod 29 is the output of the inner layer, not
the plaintext directly.

## Status

**Status**: unresolved

## Mechanism

Layer 1 (inner, unknown): M[i] = transform(P[i])
Layer 2 (outer, autokey): C[i] = C[i-1] - M[i] mod 29

The delta text D[i] = (C[i-1] - C[i]) mod 29 recovers M (the inner
layer's output). M has specific properties that constrain the inner
layer.

## Evidence for

- **Delta text has structure**: The delta text's bigrams are significantly
  non-uniform (chi-sq 1433 vs 840 expected), unlike the ciphertext's
  uniform bigrams (chi-sq ~840). Peeling the autokey layer reveals structure.
- **F suppression in delta**: Delta value F (index 0) occurs at 0.68% instead
  of 3.45%. ALL bigrams involving F are suppressed. This is the "shadow" of
  the ciphertext's doublet suppression.
- **Normal doublets/triplets in delta**: The delta text has 443 doublets (vs
  453 expected) and 16 triplets — perfectly normal. The autokey layer is what
  creates the doublet suppression in the ciphertext.
- **Second-order delta is uniform**: The delta-of-delta has uniform
  distribution including F. The structure exists only in the first-order delta.
- **28-symbol effective alphabet**: The delta text excluding F has IOC =
  0.03576, matching 1/28 = 0.03571 perfectly. The inner layer output avoids
  value 0 (F), living in a 28-symbol alphabet.

## Evidence against

- The delta text IOC (0.0353 for 29 symbols, 0.0358 for 28 symbols) is still
  random — not English-like. So the inner layer is not a simple monoalphabetic
  substitution (which would preserve IOC).
- The split test on the delta text (group delta[i] by delta[i-1]) gives random
  IOC (0.0352). So the inner layer is not itself another autokey.

## Predictions

The inner layer maps 29 English runeglish plaintext runes to 28 non-zero
values (avoiding F/index 0). This inner layer must:
1. Flatten the English letter frequencies to near-uniform
2. Map 29 symbols to 28 (lossy, or the missing symbol is very rare)
3. Preserve word boundaries

Possible inner layer mechanisms:
- A homophonic-like encoding that redistributes letter frequencies
- A compression that eliminates one symbol
- A non-linear substitution that happens to flatten frequencies

## Scripts

None yet. Key next steps:
- Analyze the delta text bigram structure in detail — which bigrams are
  elevated may reveal the inner substitution
- Check if the delta text's word-level statistics differ from the ciphertext
- Try frequency analysis on the 28-symbol delta text

## Related

- `ciphertext-autokey.md` — Single-layer autokey is disproved
- `substitution-plus-autokey.md` — Substitution before autokey doesn't flatten
  IOC (preserves it). The inner layer here must be something that DOES flatten.

## Verdict

Unresolved. The delta text analysis provides the strongest signal we've seen:
significant bigram structure, F suppression, and a clean 28-symbol alphabet.
This suggests the outer layer IS autokey, and there's an inner layer that
flattens the English frequency distribution before autokey is applied. The
inner layer is the key unknown.
