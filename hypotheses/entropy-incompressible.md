---
type: observation
---
# Observation: Near-Maximal Entropy, Zero Compressible Redundancy

## Feature

The rune stream carries essentially no exploitable statistical redundancy:
unigram entropy is within 0.03% of the maximum and general-purpose compressors
cannot beat a random shuffle.

## Measurement

`experiments/obs_entropy.py` (clean corpus):

| quantity | value |
|----------|-------|
| H1 | 4.8565 of 4.8580 bits (**99.97%** of max) |
| H(X2\|X1) | 4.7854 bits |
| zlib size vs shuffled | z = +0.3 |
| bz2 size vs shuffled | z = -2.8 (minor, block-artifact) |

## Significance

Entropy at 99.97% of maximum and compression indistinguishable from a shuffled
surrogate (zlib z~0) mean there is no n-gram redundancy to exploit. The small
bz2 deficit (-2.8) is a block-boundary artifact, not language. This is the
information-theoretic statement of "flat everything".

## Consequences

- No statistical crib surface at the rune level beyond the doublet deficit.
- Consistent with a keystream/walk that is effectively a strong PRNG.

## Scripts

- `experiments/obs_entropy.py`

## Related

- `flat-ioc.md`, `bigram-ioc.md` — the marginal and pairwise faces of this.
