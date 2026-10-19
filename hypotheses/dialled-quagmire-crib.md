---
type: hypothesis
---
# Hypothesis: A Two-Alphabet Quagmire With Free Per-Word Dials Wrote the Body

## Claim

```
c_j = ( K2[ (pos_K1((p_j + a_w) mod 29) + S_k) mod 29 ] + b_w ) mod 29
```

`K1` and `K2` are two keyed alphabets, `S` the running sums of a five-step schedule with
exactly one zero offset, `k` the clock, and `a_w`, `b_w` two dials that may take any
value in any word: an odometer, a keyword, a running key from a text, an autokey, all
of them at once. The clock may start at any phase and either run on through word
breaks or restart at each word; the doublet preventer advances it on a would-be
repeat.

This is the union of `plaintext-dial-odometer.md` (K2 = K1, dials on a carry) with
every other way of moving the dials, and with a second alphabet on the cipher side.

## Status

**Status**: **negative for keyed and affine alphabets on both sides** (2026-10-20).
Every rotation of K2, the Beaufort form (K2 backwards) and the stutter reading of a
preventer fire are being run; see Results.

## Why this family

`within-word-relation-is-position-flat.md` (row C9): the relation between two
positions of one word must change from word to word, and a Caesar shift of the
plaintext taking all 29 values is enough. In this family the relation at clock phases
k and k' is `shift(-a_w) ∘ K1 ∘ shift(S_k' - S_k) ∘ K1^-1 ∘ shift(a_w)`: one
conjugated shift per word, which is exactly what C9 asks for. K2 and b_w cancel from
every within-word statistic, so nothing in the key-free record constrains them.

## Why the crib decides

Nothing in the family is free per rune. Given K1, K2, S and the clock, the ciphertext
of DIVINITY WITHIN is fixed up to the four dial values a_0, b_0, a_1, b_1, so a wrong
key reproduces the thirteen rubricated runes about once in 29^9.

DIVINITY has I at positions 1, 3 and 5. Whatever K1 and a_0 are,
`y_j = pos_K2(c_j - b_0) - S_k(j)` must take one value at those three positions, which
cuts the (K2, b_0, schedule, clock) combinations by 841 before K1 is looked at; the six
distinct letters of DIVINITY must then land on six distinct K1 positions, and K1 is
found through an index on pairs of its positions. Word 1 is checked last, with a_1 and
b_1 free. `experiments/dialled_quagmire_crib_check.py`; the self-test plants keys at
several phases, with and without a preventer fire inside the crib, with a restarting
clock and with a rotated cipher alphabet, and recovers each.

## Results

Alphabets: the 1,264 keyed alphabets from 3301's vocabulary (`priority_vocabulary`,
four construction rules) plus the standard order and its reverse; 105,980 one-zero
schedules; 130 clocks (five start phases × continuous or restarting × no fire or one
fire at any of twelve places).

| run | K1 | K2 | word-0 matches | full matches | expected false | time |
|---|---|---|---|---|---|---|
| keyed | 1,266 keyed | 1,266 keyed | 18,130 | **0** | 0.7 | 20 min |
| affine | 2,076 keyed + affine | 2,076 keyed + affine | 64,820 | **0** | 2.7 | 55 min |

The affine alphabets are every x → ux + v (812, the standard order and its reverse
among them), so the affine run holds Quagmire I, II and the Vigenère/Beaufort forms
with one affine alphabet; it is closed under rotation on the affine side.

A full match is one with both crib words right; the expected false count is the
word-0 matches times 29² dial choices over 29⁵ for word 1's five runes. The keyed run
covers the whole family of `plaintext-dial-odometer.md` at every start phase, so its
sweep (stopped at 12 of 240 tasks) is redundant unless the crib is wrong or the
preventer fired twice inside it.

## What a negative leaves

- A keyword outside 3301's vocabulary (the single-alphabet check over the 3,000 most
  frequent English words is in `plaintext-dial-odometer.md`).
- The schedules are normalised to S_4 = 0, which here is a rotation of K2; the
  `--rotations` run takes every rotation. `--rotations --reverse` takes K2 backwards,
  which is the Beaufort form `c = K2[S_k - pos_K1(p + a_w)] + b_w` and also stands in
  for K1 backwards.
- The dial inside K1's coordinates instead of on the plaintext side is the original
  odometer's relation, fixed across words, which C9 puts at P = 0.005.
- Two preventer fires inside the crib (about one chance in fourteen), or a crib that
  is not the first two blocks' plaintext. The crib is a conjecture, not a reading: the
  first rubricated title is 8 + 5 runes, the runeglish lengths of DIVINITY WITHIN,
  and the solved Parable ends "FIND THE DIVINITY WITHIN AND EMERGE"
  (`no-known-plaintext-foothold.md`). Nothing key-free confirms it, and every
  negative in this file and in `odometer_crib_check.py` is conditional on it.
- A schedule with no zero offset or two; the one zero is what the preventer needs to
  leave the body's 86 doublets (`quagmire-dodge.md`).

## Verifying a match

With the dials free in every word a trigram scorer cannot tell a true key from a
false match: the best of 4,205 readings of a five-rune block is as trigram-plausible
as a real word (−2.9 per trigram against about −3.5; a planted key reads z = +0.8).
`experiments/dialled_quagmire_verify.py` counts instead the blocks of six runes or
more, among the first 150 after the crib, that read as a dictionary word under some
dials: a planted key reads 38 of 50, random keys 0.8 ± 0.9. The rotations run expects
about twenty false full matches and every one goes through this.

## Scripts

- `experiments/dialled_quagmire_crib_check.py` — the check; `--run`, `--run --affine`,
  `--run --rotations --nproc 6`, `--run --rotations --reverse --nproc 6`; matches to
  `experiments/dialled_quagmire_crib_*matches.jsonl`.
- `experiments/dialled_quagmire_verify.py` — the dictionary count for a matches file.
- `experiments/odometer_crib_check.py` — the single-alphabet, dials-on-a-carry check
  this generalises.

## Related

- `plaintext-dial-odometer.md`, `quagmire-odometer.md` — the special cases.
- `within-word-relation-is-position-flat.md` — row C9, why the dial is on the
  plaintext side.
- `walk-with-per-word-shift.md` — the other C9-compatible family; its free base per
  word makes the crib weak there.
