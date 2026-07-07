# Hypothesis: Position-Within-Word Dependent Cipher

## Claim

The cipher uses the position of each rune within its word as part of the
encryption key. The first rune of a word is encrypted differently from the
second, third, etc.

## Status

**Status**: disproved

## Mechanism

C[i] = f(P[i], word_key, position_in_word) mod 29

The word_key could come from:
- The previous word's ciphertext
- A fixed key
- The word length

The position_in_word (0, 1, 2, ...) adds a varying component within each
word. This defeats both the rune-level split test and the within-word split
test.

## Evidence for

- Defeats the split test (the effective key varies by position within word)
- Word boundaries are preserved
- Could explain why the within-word split test shows random IOC
- Average word length is 3.9 runes, so position-in-word has small range

## Evidence against

- No specific statistical evidence points to this mechanism
- Adds complexity without clear motivation from the ciphertext properties

## Predictions

Group runes by position-within-word (0, 1, 2, ...). If the cipher is
position-dependent, each group should have different statistical properties.
Also: words of the same length with the same ciphertext should have the same
plaintext.

## Scripts

None yet. Should test: IOC per position-within-word group, and compare
statistics of runes at different word positions.

## Verdict

Disproved. Simulation (`experiments/mechanism_fingerprint.py`) of
C = P + S[position-in-word] on Markov runeglish with the real LP word-length
sequence gives nIoC 1.12-1.14 (only ~12 effective alphabets; observed corpus
nIoC is exactly 1.000, many sigma apart at 13k runes) and doublet rate
3.3-3.7% vs the observed 0.66%. The same doublet argument as in
`word-level-autokey.md` applies: any key determined by word structure alone
is fixed before emission and cannot suppress ciphertext doublets.
