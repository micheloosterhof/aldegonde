# Hypothesis: Bifid or Trifid Fractionation Cipher

## Claim

The cipher uses fractionation: each rune is split into two (or three)
components, the components are interleaved or transposed across positions,
then recombined into ciphertext runes.

## Status

**Status**: disproved

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

Disproved for fixed-period bifid (periods 5, 7, 10 tested over keyed 6x5
grids; `experiments/mechanism_fingerprint.py`): output retains residual
language structure with nIoC 1.19-1.26 (observed: exactly 1.000), doublet
rate 3.6-4.3% (observed: 0.66%), and 20+ triplets (observed: 0). Notably,
period-5 bifid DOES couple lag-5 positions strongly (T5 z ~ +7), but with
the wrong shape: it elevates all separations d=1..4 and the monographic
lag-5 kappa (1.45 vs observed 1.07), unlike the selective d=1/d=4 pattern in
`lag5-digraph-structure.md`. The doublet and IoC failures are structural for
fractionation (it has no mechanism to avoid output doublets and preserves
coordinate-level language statistics), so other periods and per-word
variants are very unlikely to survive, though not individually simulated.

GF(29)-native constructions also tested (29 is prime, GF(29) has no
subfields, so a rune cannot be split losslessly into two field digits;
these are the principled alternatives):

- **Binary 5-bit fractionation** (rune -> 5 bits via 2^5 >= 29, transpose
  the block bit-matrix, regroup): the closest tested match to the lag-5
  shape — period 5 gives d1 and d4 near observed levels (T5z +3.5 to +4.1)
  — but it is not selective (d2 rises equally) and fails the base
  fingerprint (doublets 3.3-3.5%, nIoC ~1.20, 20+ triplets).
- **GF(841) seriation** (vertical pairs as a + b*x in GF(29^2), multiplied
  by a key unit): diffuses well (nIoC ~1.01) but no doublet suppression and
  no lag-5 signature.
- **Sparse linear mix** C[i] = aP[i] + bP[i+5] (the degenerate bifid analog
  inside the prime field): flat-ish, no signature, full doublets.

All stateless fractionation variants share the fatal flaw: no output
feedback, hence no way to produce the observed doublet suppression. And
composing them with a doublet-avoiding output stream would erase the very
lag-5 coupling that makes them interesting.
