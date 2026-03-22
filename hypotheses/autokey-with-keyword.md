# Hypothesis: Autokey with Keyword Interleaving

## Claim

A periodic keyword is added on top of a ciphertext autokey:
C[i] = P[i] + C[i-1] + K[i mod L] mod 29, combining autokey feedback with a
repeating key.

## Status

**Status**: unresolved

## Mechanism

The autokey feedback provides the dominant encryption, but a short periodic
keyword K of length L adds an additional layer. The "identity rune" (the one
causing doublets) cycles through L different values depending on position mod L.

## Evidence for

- Explains why simple autokey decryption fails (the keyword is unknown)
- The Friedman test would not detect the keyword period because autokey
  feedback dominates the periodic component
- The doublet rate becomes the average frequency of L different runes in the
  plaintext, which could match the observed 0.68%

## Evidence against

- Adds complexity without strong positive evidence from the data
- No statistical signature has been identified that distinguishes this from
  plain autokey
- Note: plain ciphertext autokey (L=1) is disproved by the preceding-rune
  split test (see `ciphertext-autokey.md`). This variant survives because the
  keyword makes the effective TR position-dependent, so the split gives a
  mixture of permutations that appears random.

## Scripts

None yet. Could test by trying autokey decryption with various short keyword
offsets and checking for English signal in the output.

## Related

- `ciphertext-autokey.md` — Plain autokey (L=1 case) is disproved.

## Verdict

Unresolved. The keyword makes the effective TR position-dependent, so the
preceding-rune split test does not apply. However, there is no positive
evidence specifically pointing to this mechanism.
