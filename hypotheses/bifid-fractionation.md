# Hypothesis: Bifid or Trifid Fractionation Cipher

## Claim

The cipher uses fractionation: each rune is split into two (or three)
components, the components are interleaved or transposed across positions,
then recombined into ciphertext runes.

## Status

**Status**: unresolved

## Mechanism

Bifid example for 29 symbols:
1. Map each plaintext rune to a (row, col) pair in a grid (e.g. 6x5 with
   one unused cell, or indexed differently)
2. Write out all rows, then all columns (or interleave them)
3. Read off pairs and convert back to runes

This creates dependencies between non-adjacent plaintext positions. The
ciphertext at position i depends on plaintext at positions i and i+k (where
k depends on the block size), not on adjacent ciphertext runes.

## Evidence for

- Fractionation creates long-range dependencies that defeat the split test
  (plaintext at position i is not a function of a small ciphertext window)
- Produces flat output from structured input when the grid is well-mixed
- Can suppress doublets (same mechanism as Playfair — same component pairs
  are unlikely to recombine into the same rune)
- 29 is prime, so no clean grid exists — this might explain the unusual
  alphabet size if Cicada chose a fractionation scheme

## Evidence against

- **Word boundaries**: Fractionation typically operates on fixed-size blocks.
  The ciphertext has variable-length words matching English. Unless the
  fractionation operates within each word independently.
- **29 is prime**: No clean grid factorization. Would need an awkward grid
  layout (e.g. 6x5-1 or radix-based decomposition).
- Playfair (a digraphic fractionation) was ruled out by uniform bigrams.
  Other fractionation schemes may share this problem.

## Predictions

Under bifid, the ciphertext at position i depends on plaintext at positions
i and i+k. Rearranging the ciphertext to undo the interleaving should
produce two streams that, when combined, decode to English.

## Scripts

None yet. Would need to try various block sizes, grid layouts, and
interleaving patterns.

## Related

- `playfair-variant.md` — A specific digraphic cipher, disproved by uniform
  bigrams.

## Verdict

Unresolved. The variable-length words are the main obstacle — standard
fractionation uses fixed blocks. Per-word fractionation with a 29-symbol
alphabet is unusual but worth investigating.
