---
type: hypothesis
---
# Hypothesis: Block Cipher / Substitution-Permutation Network

## Claim

The unsolved sections use a block cipher (SPN, Feistel network, or similar)
operating on fixed-size blocks of runes.

## Status

**Status**: disproved (boundary-blind fixed-block ciphers, assuming
authentic word boundaries; the five-block edge-effect variant is tracked
separately in `five-block-boundary.md`)

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
  incompatible with fixed-block processing. (This argument assumes the word
  boundaries are authentic; `word-length-keystream-and-boundaries.md` carries
  "possibly synthetic boundaries" as unresolved, so the disproof is
  conditional on that.)
- **No fixed-phase block lattice**: doublet positions and gaps are flat mod 5
  and pairwise dependence is null at every distance 2-100
  (`five-block-boundary.md`, `pairwise-dependence.md`) — no positional block
  alignment shows at any tested size.

## Scripts

None here; the lattice evidence lives with `five-block-boundary.md` and
`pairwise-dependence.md`.

## Verdict

Disproved for boundary-blind fixed-block ciphers, conditional on authentic
word boundaries. This does not cover block-structured mechanisms with edge
effects and drifting phase — that variant is `five-block-boundary.md` and
remains unresolved.
