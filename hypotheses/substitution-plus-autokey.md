# Hypothesis: Monoalphabetic Substitution + Autokey Layering

## Claim

The plaintext is first encrypted with a monoalphabetic substitution (to
scramble letter frequencies), then the result is encrypted with a ciphertext
autokey cipher.

## Status

**Status**: disproved

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

- **Preceding-rune split disproof**: The substitution layer maps P to M =
  subst[P], which has the same IOC as English (permutations preserve IOC). The
  autokey layer then gives C[i] = TR[C[i-1]][M[i]]. Splitting by C[i-1] gives
  permuted versions of M, which has English-like IOC. Measured: mean IOC 0.0354,
  indistinguishable from random. See `disprove_autokey_split.py`.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof.

## Related

- `ciphertext-autokey.md` — General disproof applies here. The substitution
  layer does not help because it preserves IOC.

## Verdict

Disproved. The substitution layer preserves letter frequency structure (IOC),
so the autokey layer still operates on non-uniform input. The preceding-rune
split test detects this and rules it out.
