# Hypothesis: Multi-Layer Autokey

## Claim

The ciphertext was produced by two or more sequential autokey passes with
different tabula rectae, explaining why simple single-pass autokey decryption
fails.

## Status

**Status**: disproved

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
  much higher.
- **Peel-and-split disproof**: After peeling the outer layer (trying both
  Beaufort and Vigenere), the intermediate text M was split by M[i-1]. If the
  inner layer were standard autokey, each group's IOC should be English-like
  (0.055-0.067). Measured: mean IOC 0.0352, random. The inner layer is not
  standard autokey.
- **Double-peel IOC**: Fully decrypting with two standard autokey layers
  (all 4 Beaufort/Vigenere combinations) gives IOC 0.0345, dead random.

## Scripts

None yet. The peel-and-split test was run inline.

## Related

- `ciphertext-autokey.md` — Single-layer case disproved by split test.

## Verdict

Disproved. Peeling the outer autokey layer and applying the split test to the
intermediate text shows random IOC, ruling out standard autokey as the inner
layer. Combined with the doublet rate mismatch (0.68% vs predicted 0.12%),
double standard autokey is eliminated.
