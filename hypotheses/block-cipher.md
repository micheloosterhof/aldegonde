# Hypothesis: Block Cipher / Substitution-Permutation Network

## Claim

The unsolved sections use a block cipher (SPN, Feistel network, or similar)
operating on fixed-size blocks of runes.

## Status

**Status**: disproved

## Mechanism

The plaintext is divided into fixed-size blocks and each block is encrypted
independently through rounds of substitution and permutation (or a Feistel
structure).

## Evidence for

- Block ciphers can produce flat output distributions
- Could potentially suppress doublets through diffusion

## Evidence against

- **Word boundaries preserved**: Block ciphers operate on fixed-size blocks and
  would not respect word boundaries. The ciphertext has word boundaries that
  match English word-length distributions, with words of varying length. This is
  incompatible with fixed-block processing.
- **No block structure**: There is no evidence of block-aligned patterns in the
  ciphertext at any block size.

## Scripts

None needed.

## Verdict

Disproved by the preservation of word boundaries with variable-length words.
Block ciphers cannot produce this structure.
