# Hypothesis: Homophonic Substitution

## Claim

The unsolved sections use a homophonic substitution cipher, where common
plaintext runes map to multiple ciphertext symbols to flatten the frequency
distribution.

## Status

**Status**: disproved

## Mechanism

Each plaintext rune maps to one or more ciphertext symbols, with common runes
having more homophones. The total number of ciphertext symbols exceeds the
plaintext alphabet size.

## Evidence for

- Homophonic substitution is a well-known technique for flattening frequency
  distributions
- The flat output distribution is consistent with what homophones achieve

## Evidence against

- **Same-size alphabet**: The ciphertext uses exactly 29 symbols (the full
  Elder Futhark alphabet), and the plaintext runeglish alphabet is also 29
  symbols. There is no room for homophones when input and output alphabets are
  the same size. Each plaintext rune can map to at most one ciphertext rune,
  reducing this to monoalphabetic substitution.

## Scripts

None needed.

## Verdict

Disproved. A 29-to-29 symbol mapping cannot accommodate homophones. This
hypothesis requires a larger output alphabet than is observed.
