---
type: hypothesis
---
# Hypothesis: A Ciphertext Autokey Whose Identity Rune the Plaintext Never Uses

## Claim

The body is a ciphertext autokey through a per-word mixed alphabet,

    c_j = K_w( K_w⁻¹(c_{j−1}) + p_j − e )

whose identity element `e` is one of the four runes the author's plaintext never writes
(J, EO, OE, AE: five occurrences in the 2,882-rune register). A doublet needs `p_j = e`,
so the cipher emits **no doublet and no triplet, inside words or at seams, with no rule and
no tuning**. The 86 doublets on the page are runes written twice. Lag 5 is not used
anywhere in this file.

## Status

**Status**: unresolved. Proposed 2026-10-25 when the lag-5 echo was set aside and the
question became which mechanism reduces doublets while keeping everything else. It sits in
a stated gap: `ciphertext-autokey.md` excludes `C[i] = TR[C[i−1]][P[i]]` for one fixed
table by the preceding-rune split; a table keyed per word is not that case.

## Mechanism

- **Decryption is one subtraction**: `p_j = K_w⁻¹(c_j) − K_w⁻¹(c_{j−1}) + e`.
- **Flatness is free.** The running sum makes the ciphertext uniform whatever the
  plaintext, so no pool of 949 alphabets has to be supplied; A1 is met by the feedback.
- **The split is met by the per-word key.** One fixed table reads a group nIoC of 1.785;
  rotating one mixed alphabet by a per-word dial reads 1.07; a fresh mixed alphabet per
  word reads 1.04; the body reads 1.026.
- **The doublet condition is base-invariant.** `K_w` cancels from `c_j = c_{j−1}`, so the
  suppression is the same inside words and across separators, rune-blind and memoryless.
- **The lag cells are plaintext statistics.** `c_j = c_{j+k}` iff the k following
  plaintext letters sum to `k·e` mod 29. For `e` = EO the register gives 1.01, 0.80, 1.16
  at lags 2–4 against the body's 1.01, 1.07, 1.19 (±0.18 at lag 3 on the register); for
  J 2.28 at lag 2, for OE 0.44, for AE 0.34. EO is the one dead rune that fits.

## Evidence for

`experiments/dead_rune_autokey.py`, four keys each, cycled register plaintext:

| | d1w | seam | trip | nIoC | d2 d3 d4 | split |
|---|---|---|---|---|---|---|
| body | 0.0063 | 0.0079 | 0 | 1.000 | 1.01 1.07 1.19 | 1.026 |
| one fixed table (disproved case) | 0 | 0 | 0 | 1.000 | 1.00 0.79 1.14 | **1.785** |
| one table, per-word rotation | 0 | 0 | 0 | 1.000 | 1.00 0.79 1.14 | 1.07 |
| fresh mixed alphabet per word | 0 | 0 | 0 | 0.999 | 1.00 0.79 1.14 | 1.036 |
| per-word rotation, 86 runes written twice | 0.0097 | 0 | 0 | 1.000 | 0.98 0.79 1.12 | 1.058 |

- It is the only mechanism found in which the doublet rate falls out of the algorithm
  itself, with nothing added: the plaintext alphabet is 25 letters inside a 29-rune
  cipher alphabet, and the autokey's identity is one of the spare four.
- It uses the author's own idiom: the solved Beaufort page is an autokey, and the four
  spare runes are a fact of his writing.
- The key is small: one mixed alphabet, a per-word key, and `e`.

## Evidence against

- **The 86 doublets are not the cipher's.** They have to be runes written twice by the
  group's own hand, 0.66% of the stream, spread uniformly so that 27% fall at seams as
  the body's do. The same auxiliary assumption the writing-convention reading needs
  (`haplography-the-scribe-wrote-doubles-once.md`), from the opposite side: here the
  exemplar has zero doublets and the page gains 86.
- **Identical words.** With one table and a per-word rotation the effective pool is
  29 × 29 and repeated plaintext words come back identical about four times more often
  than with a fresh alphabet per word; the body's 17 (11 of them chance) will constrain
  how rich the per-word key must be once a non-cycled plaintext is used.
- **The lag-3 cell** reads 0.80 for EO against the body's 1.07, 1.5σ on the register's
  946 pairs. A larger plaintext sample decides it.
- `the-base-is-not-a-ciphertext-autokey.md` excludes the previous *word* as the key of
  the base; it does not touch a letter-level feedback with a per-word key.

## Predictions

1. **Decryption test with a planted key.** The solver is a hill-climb on `K` with a
   per-word dial chosen by exhaustive 29-way search each step, scoring the nIoC of the
   difference stream `K_w⁻¹(c_j) − K_w⁻¹(c_{j−1})`; for the true key it reads the
   register's 1.78 and for every wrong key about 1.0. Recover a planted key first, then run
   it on one page of the body.
2. Under this reading every visible doublet hides one spurious rune: at each of the 86,
   dropping one rune should repair the decryption of that word.
3. The identity is EO (ᛇ) if the plaintext is the author's English; the other three dead
   runes put the lag-2 cell far from the body.

## Scripts

- `experiments/dead_rune_autokey.py`

## Related

- `ciphertext-autokey.md` — the fixed-table disproof this is outside of.
- `no-natural-relation-suppresses-doublets.md` — why fixed alphabets cannot do this.
- `haplography-the-scribe-wrote-doubles-once.md` — the other zero-doublet reading, with
  the suppression outside the cipher; both need the 86 as drawing errors.

## Verdict

Open. The one mechanism in the directory where sub-chance doublets are a consequence of
the algorithm and the alphabet rather than a rule or an arrangement. It stands or falls on
the planted-key solver and on the 86 being errors.
