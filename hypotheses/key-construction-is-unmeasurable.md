---
type: observation
---
# The Key's Description Length Cannot Be Measured From the Body

## Status

**Status**: confirmed negative, and it closes the question the costing depends on. Two
statistics tried, neither sees the constructions, and the one departure found does not
replicate.

## Why it matters

`how-big-is-the-key-really.md` costs the search at anywhere from 38 to 283 bits depending
on whether σ and base₀ have a short description. That is the difference between 10¹¹ keys
and 10⁸⁵, and nothing else in the directory bears on it. So: can the ciphertext tell?

## The battery cannot

`which_key_constructions_are_visible.py`, six constructions, distance from the
free-permutation arm in its own units:

| construction | distance from free |
|---|---|
| classic keyword | 0.52 |
| columnar-mixed | 0.42 |
| shift | 0.29 |
| affine | 0.21 |
| keyword, rest reversed | 0.12 |

Only the classic keyword is appreciably displaced, and even that is worth a likelihood
ratio of about 3 to 1 once the control arm is scored
(`is_the_key_keyword_built.py`). The rest are invisible.

## Nor does a sharper statistic

The natural candidate is the **bigram difference histogram** — 29 cells rather than one
number, and a structured base should leave residue on particular offsets. Offset 0 has to
be dropped, since the preventer empties it and with it included every arm reads about 300
on 28 df and nothing else shows.

| construction | χ² on 27 df over 30 keys | z of the body |
|---|---|---|
| random | 27.0 ± 7.5 | +1.91 |
| keyword | 28.8 ± 5.8 | +2.19 |
| keyword-rev | 26.7 ± 6.9 | +2.12 |
| columnar | 25.3 ± 6.6 | +2.43 |
| affine | 29.3 ± 8.1 | +1.49 |
| shift | 25.2 ± 5.0 | +3.26 |

**Every construction is uniform** — 25 to 29 on 27 df is exactly what a flat histogram
gives — so the statistic sees none of them.

## The body's own departure does not replicate

The body reads **41.4 on 27 df**, about two sigma above every arm, which would be worth
following if it were real. It is not.

| half | χ² on 27 df | largest \|z\| | at offset |
|---|---|---|---|
| first | 31.9 | 2.41 | 9 |
| second | 47.9 | 3.18 | 22 |

**The two halves disagree about which offset is extreme, and their cell profiles
correlate at +0.037.** A real structure repeats; this does not. The 41.4 is a
fluctuation, and it came after two looks at the same histogram — the first, with offset 0
included, showed nothing.

## What this closes

- **The key's description length is unmeasurable from the body.** The costing's premise
  cannot be settled from the ciphertext, so the range stays 10¹¹ to 10⁸⁵ with no
  principled way to choose.
- That is not a limit of the two statistics tried but of what a flat ciphertext can
  carry: the walk composes base₀ with 2,928 different step products, and any structure
  base₀ had is gone by the second block.
- The one route that would settle it is a solved body page, whose key would show its own
  construction directly.

## Falsification

- A statistic that separates the constructions would reopen it. The bar is low — the
  arms sit within 0.42σ of each other, so almost anything that works would show a
  large effect.
- The split-half check is the standard to hold any future candidate to: cell profiles
  that correlate across halves, not a χ² that happens to be large once.

## Scripts

- `experiments/key_construction_is_unmeasurable.py`
- `experiments/which_key_constructions_are_visible.py`

## Related

- `how-big-is-the-key-really.md` — the costing this leaves unsettled.
- `is_the_key_keyword_built.py` — the 3-to-1 on the one visible construction.
