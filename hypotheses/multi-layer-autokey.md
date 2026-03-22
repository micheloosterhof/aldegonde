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
- Note: Single-layer ciphertext autokey is disproved by the preceding-rune
  split test (see `ciphertext-autokey.md`). Multi-layer autokey survives this
  test because the first layer already flattens the intermediate text, so
  splitting the final ciphertext by C[i-1] gives flat IOC as expected.

## Scripts

- Try decrypting with autokey twice (Vigenere then Beaufort, Beaufort then
  Vigenere, etc.) and check the resulting text for English-like statistics.

## Related

- `ciphertext-autokey.md` — Single-layer case is disproved.

## Verdict

Unresolved. Survives the preceding-rune split test (first layer already
flattens). The doublet rate arithmetic weakly disfavors it (predicted ~0.12%
vs observed 0.68%). Worth testing computationally but the doublet rate mismatch
is a concern.
