---
type: observation
---
# The Per-Block Collision Count Measures the Key, Not the Plaintext

## Status

**Status**: closed channel. `experiments/collision_dispersion_is_key_noise.py`.

## What looked promising

The within-block collision count aggregates every lag at once. The body carries **811
collisions across 2,896 blocks** — an order of magnitude more events than the 86 doublets
that the doublet-gap work foundered on — and the *dispersion* of that count across blocks
should distinguish words from cuts, because words repeat letters in structured ways and
arbitrary cuts of a rune stream do not.

The null must carry the per-lag rates, which differ by a factor of eight:

| lag | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| rate | 0.0063 | 0.0348 | 0.0371 | 0.0405 | 0.0494 | 0.0248 | 0.0410 |

## Why it is empty

On one key it separates cleanly, with the corpus on the wrong side for
`blocks-are-still-words.md`:

| corpus | var/mean | per-lag null | z |
|---|---|---|---|
| enciphered real words | 1.922 | 1.641 ± 0.070 | **+3.99** |
| enciphered arbitrary cuts | 1.565 | 1.722 ± 0.078 | **−2.00** |
| the body | 1.408 | 1.497 ± 0.063 | −1.40 |

Across six keys it does not separate at all:

| plaintext structure | z |
|---|---|
| real words | −0.38 ± 3.22 |
| words joined at q = 0.35 | −0.41 ± 3.35 |
| arbitrary cuts, same lengths | −0.58 ± 1.95 |
| **the body** | **−1.40** |

The key-to-key spread is about 3σ; the words-against-cuts difference is about 0.2σ. Every
band contains the corpus. **The statistic varies more with the key than with the thing
being tested**, so no amount of extra corpus rescues it.

## Two traps, recorded because both nearly landed

- **A control that was not one.** The first "cuts" corpus concatenated the words and cut
  at the *original* word lengths, which reproduces the words exactly — words and cuts
  returned identical numbers to three decimals, which is what exposed it. Shuffling the
  length sequence first leaves 5 of 2,896 cut blocks coinciding with a word.
- **One key.** The single-key run would have been a five-sigma finding against
  `blocks-are-still-words.md`. `vary-the-key-not-just-the-corpus` is the standing rule and
  this is exactly the case it exists for.

## What it does not say

Nothing about whether the blocks are words. The channel cannot address it either way, so
`blocks-are-still-words.md` is untouched — neither supported nor weakened.

## Related

- `blocks-are-still-words.md` — the question this cannot answer.
- `short-units-are-written-joined.md` — the joining applied to the middle arm.
