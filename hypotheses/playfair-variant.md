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
rune) would be reduced but not zero, potentially matching the ~0.68% rate.

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

## Verdict

Disproved. The perfectly uniform off-diagonal bigram distribution is
incompatible with Playfair's characteristic grid-based bigram patterns.
