---
type: hypothesis
---
# Hypothesis: Playfair / Seriated Playfair Variant

## Claim

The cipher is a Playfair-type bigram substitution adapted to 29 symbols.

## Status

**Status**: disproved

## Mechanism

A Playfair cipher encrypts pairs of letters using a grid. Standard Playfair
never produces a doublet within its output bigrams. A 29-symbol variant would
need a non-square grid (e.g. 5x6 with one unused cell, or some other
arrangement).

Cross-bigram doublets (where one bigram ends and the next begins with the same
rune) would be reduced but not zero, potentially matching the ~0.66% rate.

## Evidence for

- Playfair naturally suppresses doublets (by design, same-letter pairs are
  split before encryption)
- Could work with a 29-symbol alphabet given a suitable grid arrangement

## Evidence against

- **Uniform off-diagonal bigrams**: Playfair produces structured bigram
  statistics with characteristic patterns (certain bigram pairs are more common
  based on grid adjacency). The observed off-diagonal bigrams are perfectly
  uniform (chi-sq p=0.23), which is inconsistent with Playfair's signature.
- **Odd alphabet size**: 29 does not factor into a clean grid. Standard Playfair
  uses a 5x5 grid for 25 letters.

## Scripts

None needed. The bigram uniformity test is sufficient.

## Mechanism-specific tests (July 2026) — both variants closed

The original bigram-uniformity argument pooled ALL adjacencies, which
dilutes a within-pair signature ~2x, and never addressed the seriated
variant in the title. Both are now tested directly, using the sharpest
Playfair property: **a Playfair pair can never emit a doublet** (all
three rules — same row, same column, rectangle — force the two output
letters apart unless the plaintext pair is itself a doublet, which
Playfair forbids by insertion). So every observed doublet must sit
ACROSS a pair boundary.

**Standard Playfair (adjacent pairing) — excluded.** Classifying the 86
doublets by the parity of their first position: **44 even / 42 odd**.
Whichever alignment the pairs use, roughly half the doublets fall
within a pair, where Playfair permits none. The split holds in every
section separately (2/2, 3/3, 3/6, 5/5, 5/6, 7/6, 9/3, 9/9, 1/2), so
per-section realignment does not rescue it either.

**Seriated Playfair (vertical pairing) — excluded.** Under seriation
with period P the plaintext is written in rows of length P and pairs are
formed vertically, so ciphertext positions i and i+P are a pair whenever
(i mod 2P) < P and can never be equal, while the other half of
distance-P pairs is unconstrained. Measured for P = 2..12, the
constrained class sits at the chance rate throughout (rates 0.029-0.038,
z from −2.5 to +1.3 against 1/29) where it must be ~0. No period works.

Together these close the family on its own defining property rather than
on a pooled statistic that could not have detected it.

## Verdict

Disproved. The perfectly uniform off-diagonal bigram distribution is
incompatible with Playfair's characteristic grid-based bigram patterns.
