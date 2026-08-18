---
type: observation
---
# The Crib Budget for `g`: ~400 Known Words, and the Titles Supply 29

## Claim

A crib constrains the letter step `g` directly, through a **base-free** channel
nobody had costed: inside one word the base cancels between two positions, so a
ciphertext collision at known plaintext is a constraint on `g` alone. Measured
on a planted key, the channel yields **one constraint per 10 crib runes**, and
`g` collapses to a brute-forceable candidate set at roughly **300 known words**
(~1,200 runes).

The ~31 title slots of `rubrication-crib-candidates.md` supply **29 words / 128
runes in total**. That is more than an order of magnitude short, so the title
program cannot pin the key. It remains a verifier, not a generator.

## Status

**Status**: confirmed (characterization), measured on `walk_reference.json`
where every derived constraint is checked against the planted `g` (the run
asserts both that each constraint is true and that each resolved point matches).

## The channel

Within word `w`, `c_j = psi_w(g^(j mod 5)(p_j))` with `psi_w` constant, so for
two positions the base cancels:

```
c_j == c_j'   <=>   g^(j mod 5)(p_j) = g^(j' mod 5)(p_j')   <=>   g^d(p_j) = p_j'
```

with `d = (j - j') mod 5`. With the plaintext **known**, that is a direct
constraint on `g` — no `base_0`, no `sigma`, no word position. Two consequences:

- **Cribs pool from anywhere in the book.** Scattered cribs are worth exactly as
  much as contiguous ones for `g`, unlike the `base_0` propagation of
  `crib_propagation.py`, which needs contiguity.
- `d = 0` degenerates to `p_j = p_j'` — the key-free d5 rule — and says nothing
  about `g`, so only 4 of every 5 position pairs are informative.

Resolution uses that `g` has order 5: `g^d(a) = b` places `a` and `b` in one
5-cycle at offset `d` (union-find with a mod-5 potential), and `g^d(a) = a` with
`d != 0` marks a fixed point since `gcd(d,5) = 1`.

This is the known-plaintext counterpart of `key-local-channel-is-empty.md`,
which measured the *plaintext-free* version of the same channel and correctly
found it nearly empty (~4 bits). Supplying the plaintext is what makes it rich.

## The budget

`experiments/crib_budget_g.py`, planted corpus of 2,928 words / 12,067 runes,
`g` of cycle type 5^5 1^4 (25 moving points, 4 fixed). Known words sampled at
random; residual = order-5 permutations still consistent with the pinned points.

| known words | runes | equalities | `g` points pinned | residual `g` |
|---|---|---|---|---|
| 25 | 103 | 10.8 | 2.6 | — |
| 50 | 208 | 20.0 | 4.8 | — |
| 100 | 422 | 50.8 | 9.2 | >200,000 |
| 200 | 823 | 95.2 | 15.2 | >200,000 |
| 400 | 1,667 | 180.0 | 18.8 | 60 |
| 800 | 3,334 | 348.0 | 20.2 | 20 |
| 2,928 (all) | 12,067 | 1,258.0 | 24.0 | 6 |

Yield is **0.104 constraints per crib rune**, one per 10 runes.

The residual collapses sharply, and a finer sweep (median of 3 samples, cap
2e6) locates the knee:

| known words | runes | pinned | residual `g` |
|---|---|---|---|
| 200 | 850 | 12 | >2,000,000 |
| 250 | 1,069 | 16 | >2,000,000 |
| 300 | 1,189 | 14 | 1,995,950 |
| 350 | 1,415 | 16 | 15,120 |
| 400 | 1,601 | 19 | 1,680 |
| 500 | 2,101 | 20 | 120 |

**The practical threshold is ~300 known words (~1,200 runes).** At that point
the residual (~2e6) is already brute-forceable — the DJU-BEI state-return
filter of `affine_sigma_state_return.py` runs at ~1.4 ms per candidate, so 2e6
is under an hour — and by 350-400 words it is trivial. The `base_0` quadgram
verifier then settles the survivors in seconds each.

## Saturation: rare runes bound what any crib can do

Even with the **entire book** as crib, only 24 of 29 points resolve. The
unresolved points are `[2, 12, 19, 22, 25]`, and the cause is rune coverage,
not the method:

- rune 25 (AE) never occurs in the plaintext at all — it can never be
  constrained;
- runes 12 (EO) and 22 (OE) occur at 0.02% and 0.04%;
- runes 2 and 19 are common but sit adjacent to a rare rune in their cycle, so
  their successor is the missing member.

Two of the five 5-cycles stall at four members each. The residual is therefore
never zero, but it is *tiny* (6 completions at saturation), so this bounds
precision rather than blocking the attack.

## Why the title program cannot be the generator

Measured on the real corpus (`experiments/djubei_context.py` tokenizer, title =
the word run ending at a 13-dot): **12 plausible title slots holding 29 words
and 128 runes in total**, median 2 words / 11 runes each.

Against a budget of ~300 words / ~1,200 runes, correctly guessing *every title
in the book* delivers roughly **13 constraints and 2-4 points of `g`** — the
residual stays far above the enumerable regime. The titles are **~10x short**,
and that gap is in word count, which no cleverness about *which* titles closes.

So the answer to "are the title cribs a route to the key?" is **no**. A
confirmed title still works as a *verifier* for a candidate key, which is what
`crib_propagation.py` already established; it cannot generate one.

## Scope and the open lever

- The measurement propagates **equalities only**. The same cribs carry 48,242
  *in*equalities (`g^d(a) != b`), ~29x more numerous and entirely unused, so
  every number here is a **lower bound** on what a full CSP could extract.
  Halving the budget by exploiting them is the one concrete way this conclusion
  could change, and it is a well-posed piece of work.
- The budget is for `g` only. `sigma` needs the cross-word collisions, which
  become usable once `g` is known; that leg is unmeasured.
- Random word sampling models scattered cribs. Contiguous cribs of the same
  rune count behave the same for this channel, by the cancellation argument.

## Scripts

- `experiments/crib_budget_g.py` — the measurement, the residual counter
  (validated: fully-known `g` counts exactly 1 completion), and the assertions
  against the planted key.

## Related

- `key-local-channel-is-empty.md` — the plaintext-free version of this channel,
  ~4 bits; this note is why supplying plaintext changes the picture.
- `crib_propagation.py` / `no-known-plaintext-foothold.md` — the `base_0` budget
  given `(g, sigma)`, median 80 contiguous runes.
- `rubrication-crib-candidates.md` — the title slots this note costs out.
- `length-clocked-walk.md` — the model supplying the cancellation.

## Verdict

Cribs buy real, base-free information about `g` at one constraint per 10 runes,
and ~300 known words would reduce `g` to a brute-forceable ~2e6 (350 words:
15,120) — a genuine route, if the plaintext existed. The book's title slots
supply 29 words, so that route is closed by an order of magnitude. Combined with the standing result that no
gradient exists over `(g, sigma)`, the attack remains candidate-generation
bound, and cribs are confirmed as verifiers rather than generators. The
unexploited inequality channel is the only measured way to move the number.
