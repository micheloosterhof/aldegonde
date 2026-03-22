# Hypothesis: Transposition Cipher

## Claim

The unsolved sections use a transposition cipher that rearranges rune positions
without substituting rune values.

## Status

**Status**: disproved

## Mechanism

Runes are rearranged according to a permutation pattern (columnar
transposition, rail fence, etc.) without changing their values. The alphabet
remains the same; only positions change.

## Evidence for

- Transposition is a fundamental classical cipher technique
- Could potentially disrupt adjacency statistics (affecting doublet rates)

## Evidence against

- **Only skip=1 kappa is anomalous**: A transposition would affect kappa at
  multiple skip values corresponding to the transposition's column width or
  period. The observed data shows anomalous kappa only at skip=1, with all
  other skip values normal.
- **Word boundaries preserved**: Word boundaries are preserved and match
  English word lengths. A transposition cipher operating across word boundaries
  would scramble them. A within-word transposition would not affect cross-word
  adjacencies, yet cross-word doublets are also suppressed.
- **Flat distribution**: Pure transposition preserves letter frequencies. The
  text has a uniform distribution, which requires substitution (not just
  rearrangement) to achieve from English.

## Scripts

None needed. The statistical properties rule this out directly.

## Verdict

Disproved. The combination of preserved word boundaries, flat distribution, and
the adjacency-only kappa anomaly eliminates all transposition-based
explanations.
