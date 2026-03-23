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

- **Normal doublets/triplets in delta**: The delta text has 443 doublets (vs
  453 expected) and 16 triplets — perfectly normal. The autokey layer is what
  creates the doublet suppression in the ciphertext.
- **F suppression in delta**: Delta value 0 (= EA under 1-based indexing)
  occurs at 0.68% instead of 3.45%. This is the "shadow" of the ciphertext's
  doublet suppression: C[i]=C[i-1] iff delta=0.
- **28-symbol effective alphabet**: The delta text excluding value 0 has IOC =
  0.03576, matching 1/28 = 0.03571 perfectly. The inner layer output avoids
  the identity value.

## Evidence against

- **Bigram structure is only from F suppression**: The delta bigram chi-sq
  (1433 vs 840) is entirely explained by the rarity of value 0. Non-zero
  bigrams are perfectly uniform (chi-sq 766 vs 783 expected). No hidden
  bigram structure beyond the F/EA suppression.
- **Delta text is random over 28 symbols**: IOC 0.03576 = 1/28 exactly.
  Repeat counts match 28-symbol random text. No word-boundary effects.
- The split test on the delta text (group by delta[i-1]) gives random IOC.
  So the inner layer is not another autokey.
- A monoalphabetic inner layer is ruled out (would preserve IOC at
  English-like levels, not flatten to 1/28).

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
