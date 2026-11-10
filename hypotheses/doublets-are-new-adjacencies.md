---
type: hypothesis
---
# Hypothesis: The Preventer Is Perfect and the 86 Doublets Are New Adjacencies

## Claim

The cipher never emits the rune it has just emitted. The 86 doublets were made
afterwards, by a step that put side by side two runes that were not neighbours when the
rule was applied. Two such runes are equal at the chance rate, so

    doublet rate = f / 29,    f = the share of adjacent pairs that are new adjacencies

and the body says f = 0.193 ± 0.021. Proposed 2026-11-10.

## Status

**Status**: unresolved. Two of its three carriers are tested and fail; the third has one
parameter-free success and one prediction against it at 1.9σ.

## Mechanism

Every other reading makes the preventer imperfect (the dodge that fails one time in
five, `quagmire-dodge.md`), or tunes a relation to the rate (the walk), or removes the
rule from the cipher (`haplography-the-scribe-wrote-doubles-once.md`). This one keeps
the simplest rule, "re-encipher until the rune differs", and asks what was done to the
stream afterwards. It reproduces for free the properties rows D5, D11 and D3 record:
the survivors are rune-blind, the suppression has memory of exactly one rune, and it
ignores block boundaries, provided the after-step ignores them too.

It also gives every carrier a hard test. The carrier fixes WHERE new adjacencies can
be, and all 86 doublets must be there. A wrong rule touching a fifth of the pairs covers
all 86 with probability 0.2⁸⁶.

## Evidence for

`experiments/new_adjacency_probes.py`.

**Inserted nulls predict the block lengths with no parameter.** A null makes two new
pairs, so nulls are ν = f/2 = 0.096 of the runes, and the blocks should be longer than
the plaintext's words by 1/(1 − ν). The author's words average 3.986 runes; the
prediction is 4.411; the body reads 4.425 (4.474 with page breaks joined). On the whole
marginal:

| model | mean | 2-rune share | χ² on 11 df against the body |
|---|---|---|---|
| the body | 4.474 | 0.155 | |
| the author's words as written | 3.986 | 0.242 | 45.4 |
| nulls at 0.096 of the final runes | 4.410 | 0.201 | 16.0 |
| THE joined to the next word | 4.238 | 0.194 | 14.1 |
| THE joined, then nulls at 0.096 | 4.692 | 0.161 | 18.0 |

The doublet count fixes ν; nothing is fitted to the lengths. The agreement on the mean
is within 0.2σ of the two means' errors, which chance would give about one time in six
for an unrelated inflation.

**A by-product, independent of this hypothesis.** One word accounts for most of the
2-rune hole (row E3). THE is two runes and 43 of the author's 723 words; writing it
joined to the next word takes χ² from 45.4 to 14.1 with no parameter, where the general
joining model (row E9) needs q ≈ 0.40. The two are not separated by the marginal. If it
is THE, many blocks begin TH-E.

## Evidence against

**Block reversal is excluded.** Reversing fixed blocks of b runes, or boustrophedon rows
of width b, makes one pair in b new, and b = 5 gives 89 doublets. Then every doublet
sits in one residue class mod b. Over b = 4 to 7 and nine index rules (runes, or runes
and separators; from the start of the body, section, page, line or word) the largest
share in one class is 0.38. The reading needs 1.00.

**No ruled null position.** If the nulls sit where a rule puts them, every doublet
touches a null position. Over 288 rules (primes, squares, Fibonacci numbers, multiples
of 3 to 15; the same index rules; counting from 0 or 1) the best cover among rules
touching under half the pairs is 0.62.

**Lag 2 is not lowered.** The two runes either side of a null were neighbours in the
no-repeat stream and are never equal, so nulls lower the lag-2 coincidence rate by ν:
404 expected. The body has 441 of 12,954, z −0.27 against chance and **+1.89** against
the null reading.

**A random null cannot be removed by the reader.** A null the recipient can identify
has to follow a rule or be a rune the plaintext never writes; the first is not found
above, and the second is `null-rune-preventer.md`, which inserts only on a would-be
repeat (ν = 1/29) and predicts no survivors by this route.

## Predictions

- Any proposed after-step names the pairs it creates. All 86 doublets are among them.
- Keyed null positions (gaps drawn from a key sequence) are the untested carrier. The
  test is the same cover count, run for each candidate sequence of gaps.
- Under inserted nulls the lag-5 echo is diluted by (1 − ν)⁵ ≈ 0.60 inside blocks, so a
  real echo would be about 1.7 times stronger in the plaintext stream than row D2 reads.

## Scripts

- `experiments/new_adjacency_probes.py`

## Related

- `doublet-suppression-requires-design.md` — the two classes this sits beside.
- `null-rune-preventer.md`, `haplography-the-scribe-wrote-doubles-once.md` — the other
  readings in which the survivors are not a failed dodge.
- `block-lengths-have-a-hole-at-two.md`, `short-units-are-written-joined.md` — rows E3
  and E9, which the THE reading bears on.

## Verdict

Open, leaning against. The lens is the useful part: a perfect preventer plus an
after-step turns the doublets from a rate to be matched into 86 positions to be covered,
which is a far sharper test than any battery cell.
