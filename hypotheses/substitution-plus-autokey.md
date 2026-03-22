# Hypothesis: Monoalphabetic Substitution + Autokey Layering

## Claim

The plaintext is first encrypted with a monoalphabetic substitution (to
scramble letter frequencies), then the result is encrypted with a ciphertext
autokey cipher.

## Status

**Status**: unresolved

## Mechanism

Two layers:
1. Apply a fixed substitution key: M[i] = subst[P[i]]
2. Apply ciphertext autokey: C[i] = M[i] + C[i-1] mod 29

Decryption requires knowing both the substitution key (29! possibilities) and
the autokey primer.

## Evidence for

- Explains why simple autokey decryption does not produce readable text: the
  substitution layer must be removed first
- The autokey layer produces the doublet suppression and flat distribution
- The substitution layer prevents frequency analysis of the autokey output
- Both layers are classical techniques that Cicada would plausibly use

## Evidence against

- No specific evidence in the ciphertext statistics distinguishes this from
  single-layer autokey (the substitution is invisible after autokey flattening)
- Large key space (29!) makes brute force infeasible without cribs
- Parsimony: no positive evidence for the substitution layer beyond explaining
  why simple autokey fails

## Scripts

None yet. Testing would require crib-based attacks: for known plaintext
fragments, try autokey decryption and look for consistent monoalphabetic
mappings.

## Verdict

Unresolved. A natural explanation for why simple autokey decryption fails, but
the substitution layer is essentially invisible in the statistics. Testable
only through crib-based approaches.
