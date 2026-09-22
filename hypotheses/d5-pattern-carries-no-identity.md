---
type: observation
---
# The d5 Pattern Does Not Identify Words, and the Arithmetic Says So Before Any Test

## Status

**Status**: confirmed negative. Recorded because the idea is attractive enough to occur
again, and because the information calculation kills it in one line.

## The idea, which is good

A repeated ciphertext word needs a **base return** — the two blocks must draw the same
alphabet, which happens about once in 2,700 (`dju-bei-is-more-surprising-than-recorded`).
That is why `identical` is chance-dominated and why the corpus has only one candidate
return.

But under the walk `c[j] == c[j+5]` iff `p[j] == p[j+5]`, so **the pattern of which lag-5
pairs coincide inside a block is a function of the plaintext word alone.** Two blocks with
the same plaintext share a pattern whatever their bases are. That would be a key-free
detector of repeated plaintext, sensitive exactly where `identical` is not — and it needs
no base return at all.

## It does not work

`experiments/d5_pattern_carries_no_identity.py`, blocks of eight runes or more, against
prose drawn to the body's own length profile.

| statistic | body | prose, matched shape | z |
|---|---|---|---|
| pairs sharing a pattern | 12,736 | 11,412 ± 642 | +2.06 |
| among blocks carrying a coincidence | 71 | 168.0 ± 48.8 | −1.99 |
| fraction of blocks with a coincidence | 0.191 | 0.219 ± 0.022 | −1.29 |

The first two point opposite ways at about two sigma, which is the signature of a
statistic driven by the coincidence **rate** rather than by word identity: a lower rate
means more all-zero patterns, hence more matches among all blocks and fewer among those
carrying a coincidence. The rate itself is the d5 leak, already measured and bounded by
D10.

## Why, in one table

How many bits does a pattern carry, against how many are needed to name a word?

| length | prose words | distinct | pattern bits | words per pattern |
|---|---|---|---|---|
| 8 | 4,827 | 1,255 | 1.01 | 623 |
| 10 | 2,299 | 755 | **1.62** | **246** |
| 12 | 557 | 258 | 1.93 | 68 |
| 13 | 205 | 118 | 2.40 | 22 |

Naming a ten-rune word takes about ten bits. **The pattern supplies 1.6**, leaving some
250 candidates. Even at thirteen runes it supplies 2.4.

The reason is that the pattern is nearly always all-zero: **only 65 of the body's 340
blocks of eight runes or more carry any coincidence at all.** A detector whose output is
one bit on a fifth of the data cannot tell words apart.

## What to take from it

- The attraction was real — needing no base return is a genuine advantage over
  `identical` — and it is outweighed by the channel's thinness. Sensitivity is worth
  nothing without information.
- The arithmetic settles it before any test: entropy of the pattern against entropy of
  the word list. That check costs nothing and should come first next time.
- It leaves `identical` and `returns` as the only word-repeat channels, both
  chance-dominated, which is why `word-repeat-accounting.md` has to subtract a floor.

## Falsification

- If the body's blocks were much longer the pattern would carry more; at length 20 it
  would be about four bits. The body has no such blocks.
- If the plaintext repeats long words far more than prose does, the concentration test
  would show it. It reads +2.06 and −1.99 on two halves of the same statistic, which is
  no signal.

## Scripts

- `experiments/d5_pattern_carries_no_identity.py`

## Related

- `period5-is-confirmed`, `d5-bounds-the-clock-perturbation.md` — the channel and its
  measured strength.
- `word-repeat-accounting.md` — the word-repeat channels this would have supplemented.
