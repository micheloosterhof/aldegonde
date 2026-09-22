---
type: hypothesis
---
# The 283-Bit Budget Assumes Free Permutations; a Naturally Built Key Is 38 Bits

## Status

**Status**: a hypothesis with a costing, not a measurement. It reframes
`the-bit-budget.md` rather than contradicting it — every number there is right for the
model space it describes.

## The point

`the-bit-budget.md` totals the key at **283 bits** — g 79.7, σ 101.8, base₀ 101.8 — and
concludes no statistical route can close a gap that size. Each of those three is the size
of a **free permutation space**.

A real key is rarely a free permutation, and **this author's demonstrably is not.** The
solved pages use `DIVINITY` and `FIRFUMFERENFE`: English keywords turned into mixed
alphabets. That is direct evidence of how he builds keys.

## Three readings, costed

| how the key was built | g | σ | base₀ | bits | keys |
|---|---|---|---|---|---|
| every part a free permutation | 79.7 | 101.8 | 101.8 | **283** | 10⁸⁵ |
| g structured, the rest free | 14.5 | 101.8 | 101.8 | 218 | 10⁶⁶ |
| **every part naturally built** | **14.5** | **11.8** | **11.8** | **38** | **10¹¹** |

- **structured g** — fix four runes and step the other twenty-five by five in alphabet
  order, which is how you build an order-5 permutation of 29 points by hand. There are
  C(29,4) = 23,751 of them, 14.5 bits against 79.7.
- **keyword alphabets** — 3,518 prose word types have all-distinct runes and 3 to 12 of
  them, 11.8 bits each.

**Under the third reading the search is 2.9 × 10¹¹.** The d-profile filter is worth 6.2
bits on g and the cross-seam identity verifies a (g, σ) pair at no cost, bringing it to
about **4 × 10⁹** before any decryption is attempted — roughly **220 core-hours** at the
compiled scorer's 5,000 keys per second, the same order as the sweep already costed and
parked.

## The consistency check

A structured `g` has to survive what is already measured. Against the body's coincidence
profile:

| pool | n | best χ² | 1st percentile | median |
|---|---|---|---|---|
| structured: fix 4, step 25 by five | 23,751 | 1.19 | 6.06 | 37.2 |
| free five-cycle permutations | 23,751 | 0.42 | 6.09 | 42.9 |

The tails match. **A structured g is consistent, and this is not evidence for one** — the
filter is worth 6.2 bits on individuals, not on populations, so it cannot prefer a family.

## What makes the costing optimistic

Said plainly, because the number is the point of the file.

1. The structured family above is **one invention**. Others exist — a keyword-mixed order
   before the step, a different step size — and each multiplies the space.
2. The keyword list is **prose vocabulary**, 10,334 types. A dictionary is ten times
   larger, adding about 3 bits to each of σ and base₀.
3. The filter's pruning is **unreliable**: three of six planted trials put the true `g`
   outside the top 2%. Keeping the top 20% instead costs a factor of ten.
4. The whole reading is **a hypothesis**, supported by the author's habits on the solved
   pages and by nothing in the body itself.

Taken together those plausibly move 220 core-hours to a few thousand. The conclusion that
survives is the order of magnitude: **10⁹ to 10¹¹ keys, not 10⁸⁵.**

## Falsification

- The direct test is to run it, which is a decision rather than a measurement.
- If a solved body page appears, its key settles how the key was built at once.
- If the structured family is wrong, the g component returns to 79.7 bits and the search
  is hopeless again. Nothing in the body distinguishes them, so this is the load-bearing
  assumption and it is unsupported.

## Scripts

- `experiments/how_big_is_the_key_really.py`

## Related

- `the-bit-budget.md` — the 283 bits this reframes.
- `crib-budget-decides-crib-programs.md` — the other place a search cost is computed.
- `mixed-alphabet-vigenere.md` — keyword-derived alphabets excluded for a *periodic* key,
  which is a different cipher.
