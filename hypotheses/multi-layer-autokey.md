# Hypothesis: Multi-Layer Autokey

## Claim

The ciphertext was produced by two or more sequential autokey passes with
different tabula rectae, explaining why simple single-pass autokey decryption
fails.

## Status

**Status**: unresolved

## Mechanism

Plaintext is encrypted with autokey pass 1, then the output is encrypted again
with autokey pass 2 (possibly using a different TR variant, e.g. Vigenere then
Beaufort). Decryption requires reversing both passes in the correct order.

## Evidence for

- Explains why simple autokey decryption does not produce readable text
- Doublet suppression compounds across layers: each pass independently
  suppresses doublets
- Both passes preserve the statistical signature (flat distribution, no
  Friedman period)

## Evidence against

- **Doublet rate arithmetic**: Double autokey would square the doublet
  suppression, pushing the rate from ~3.45% to ~0.12%. The observed 0.68% is
  higher than this prediction, suggesting either single-layer autokey with a
  rare identity rune, or a more complex interaction between layers.
- **Parsimony**: A single-layer explanation is simpler and should be preferred
  unless single-layer autokey is definitively ruled out.

## Scripts

- Try decrypting with autokey twice (Vigenere then Beaufort, Beaufort then
  Vigenere, etc.) and check the resulting text for English-like statistics.

## Verdict

Unresolved. The doublet rate arithmetic weakly disfavors double autokey, but
the exact suppression depends on the interaction between layers and the
plaintext statistics. Worth testing computationally.
