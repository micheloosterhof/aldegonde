---
type: observation
---
# The Measured Channels Reach Six Percent of the Key, and the Largest Part Has No Channel

## Status

**Status**: confirmed, and it corrects the information content claimed for C-0 and for
the d-profile filter. Both measurements stand; what they are worth as search constraints
does not.

## The correction that prompted it

`d-profile-pins-g-to-five-cycles.md` filters a pool drawn uniformly over cycle counts 1
to 5. The real space is nothing like uniform:

| five-cycles | permutations of 29 points | share |
|---|---|---|
| 1 | 2,850,120 | 0.000000 |
| 2 | 1,453,698,005,760 | 0.000000 |
| 3 | 135,228,803,287,818,240 | 0.000000 |
| 4 | 1,624,368,385,093,272,698,880 | 0.00165 |
| **5** | **982,417,999,304,411,328,282,624** | **0.99835** |

**"g has five five-cycles" is 99.8% of the space — 0.0024 bits.** The measurement is
real; as a search constraint it is vacuous. And the filter's hundredfold reduction was
measured against that same uniform pool, so part of it is the rejection of low-cycle g
the real space barely contains.

Re-measured inside the realistic class, by ranking a planted `g` in a pool drawn only
from the five-cycle permutations:

    trial ranks: 5, 1, 152, 542, 14, 782  of 6,000
    median 84  ->  about 6.2 bits

and **unreliable: three of six trials put the true g outside the top 2%.**

## The budget

| part of the key | bits | channel | supplied |
|---|---|---|---|
| g (five-cycle class) | 79.7 | d-profile filter | **6.2** |
| σ (A₂₉) | 101.8 | cross-seam cells | **< 10** |
| **base₀ (A₂₉)** | **101.8** | **none** | **0** |
| total | **283** | | **16 at best** |

**Under six percent**, and the σ column is the optimistic reading: the cross-seam channel
exists only under a right-acting base step, which `the-base-step-may-act-on-the-left.md`
leans against at about two sigma. Under a left action it is zero too, leaving 6 of 283.

## Why base₀ has no channel

Every block draws its own alphabet, and `base_changes_every_block.py` shows that
directly — at most 15% of block edges can carry an unchanged base. So nothing accumulates
across blocks about the starting alphabet: 2,928 blocks supply 2,928 separate unknowns
tied together only through the step, and the step is what σ is.

That is the structural reason the largest single part of the key is unreachable, and it
is not a limit of the statistics used. It is a property of the cipher.

## What follows

- **No statistical route exists.** Sixteen bits of 283 cannot be closed by a better
  estimator; the gap is two orders of magnitude.
- The only route left is a search that **decrypts** — that proposes a full key and reads
  the plaintext — which is what the parked sweep does.
- The channels retain their real uses. The filter ranks candidates, the cross-seam
  identity verifies a proposed (g, σ) for free, and the rule parameters (φ ≈ 0.90,
  q ∈ [0.003, 0.262]) constrain the cipher's shape rather than its key.
- C-0 should be quoted as *confirmation that the walk's default assumption is right*,
  not as a reduction of the search.

## The 283 is the model space, not necessarily the key

Every number in the table above is the size of a **free permutation space**, and a real
key is rarely a free permutation. This author's is not: the solved pages use `DIVINITY`
and `FIRFUMFERENFE`, keywords turned into mixed alphabets.

`how-big-is-the-key-really.md` costs the alternative. With a structured `g` — fix four
runes and step the other twenty-five by five, C(29,4) = 23,751 — and keyword-derived σ
and base₀, the key is **38 bits and about 2.9 × 10¹¹ keys**, falling to 4 × 10⁹ once the
filter and the cross-seam verifier have done their work.

That does not contradict anything here. It says the conclusion "no statistical route
exists" is right and the further conclusion "therefore the problem is out of reach" does
not follow — it depends entirely on an assumption about how the key was built, which
nothing in the body tests.

## Falsification

- The class counts are exact arithmetic and can be checked directly.
- The filter's 6.2 bits is a median over six planted trials; more trials would tighten it,
  and its unreliability (three of six outside the top 2%) matters as much as its median.
- If a channel is found that accumulates across blocks about base₀, the whole budget
  changes. The orbit theorem says only equality is base-invariant for pairs, which is why
  none has been found.

## Scripts

- `experiments/bit_budget.py`

## Related

- `d5-pattern-carries-no-identity.md` — the entropy rule this applies project-wide.
- `d-profile-pins-g-to-five-cycles.md` — the measurement whose worth this corrects.
- `unicity-distance.md`, G2 — the key is uniquely determined by the ciphertext; this says
  it is not reachable by measuring.
