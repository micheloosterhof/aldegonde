---
type: hypothesis
---
# Hypothesis: The Body Was Produced by a Program, and the Key Is a Seed

## Claim

The body's ciphertext was computed, not worked by hand, and copied onto the pages by a
scribe who could not read it. Then the hand-cipher priors this directory carries (keyword
alphabets, natural square fills, a wheel to index) are the wrong priors: `g`, `σ` and
`base_0` may be pseudo-random permutations drawn from a seed, and the key to search is
the seed and the construction, not the permutations.

## Status

**Status**: unresolved. Proposed 2026-10-25.

## Mechanism

Any of: `random.seed(s)` and three Fisher–Yates shuffles (Python 2 and 3 differ);
`numpy.random`; OpenSSL `RAND`; `SHA-512(s ‖ counter)` sorted into a permutation; or a
hash chain supplying every per-word base directly, `base_w = perm(SHA-512(s ‖ w))`, in
which case there is no σ at all. The seed candidates come from the book: the 256-byte
block of the number grids in its four readings (`number-grids-are-bytes.md`), the
Gematria sums of the rubricated titles, "3301", and the author's known phrases.

## Evidence for

- `the-scribe-ignored-the-blocks.md`: in the body the scribe breaks lines mid-word 76% of
  the time and at word boundaries only where the text was readable to him. He copied
  output he did not understand.
- `is_there_an_unsuppressed_stretch.py`: the preventer never lapses across 12,955 pairs
  (a 500-pair lapse would read seven sigma). A hand rule applied through a book lapses.
- The number grids hold 256 uniform bytes, 2,048 bits: hashes, keys or ciphertext, not
  runes.
- The author's toolchain in the same puzzle: RSA, PGP, SHA-512, onion services.

## Evidence against

- A programmer with a modern toolchain had no need of a 29-letter walk with a dodge; the
  mechanism the ledger reconstructs is a hand design, which argues the program implements
  a hand design and the seed reading only replaces the key's representation.
- A hash chain of bases gives no state return except by collision at 1 in 29!; the
  DJU-BEI return then becomes a 1-in-2,700 accident, which the ledger allows but does not
  favour (D7).

## Predictions

1. For the right construction and seed, the generated `g` passes the 13-bit d-profile
   filter of `key-local-channel-is-empty.md` and the generated chain satisfies
   `M_1477 = M_2926`; both are base-free and cost nothing per candidate.
2. A seed derived from the 256-byte block decrypts the first page to text with nIoC near
   1.78 and a quadgram score in the register's range.

## Scripts

- To write: a generator per construction family and the two filters above, with a planted
  seed as the control. Each family is an afternoon; the prior per family is low and the
  result per family is decisive.

## Related

- `number-grids-are-bytes.md` — the seed material.
- `rotor-machine-compact-state.md` — why no small hand device fits, which this reads as
  evidence for a machine rather than against the walk.

## Verdict

Open. Low prior per construction, decisive per construction, and it changes what counts
as a natural key everywhere else in this directory.
