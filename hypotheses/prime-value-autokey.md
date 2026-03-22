# Hypothesis: Prime-Value Tabula Recta Autokey

## Claim

The cipher uses an autokey mechanism where the tabula recta is constructed from
Cicada's prime-rune associations (Gematria Primus) rather than standard
additive arithmetic.

## Status

**Status**: unresolved

## Mechanism

C[i] = TR[C[i-1]][P[i]], where TR[k][p] = (prime(k) + prime(p)) mod 29 or a
similar prime-based operation. Each rune maps to its Cicada-assigned prime
number, and encryption uses these prime values in modular arithmetic.

The codebase includes `valueTR()` which builds this kind of tabula recta.

## Evidence for

- Cicada explicitly associates primes with runes (Gematria Primus is central
  to their mythology)
- Prime arithmetic mod 29 is well-behaved (29 is prime, so the arithmetic
  forms a field)
- Still an autokey cipher, so it inherits the doublet-identity property (the
  specific identity element depends on the prime mapping)
- `valueTR()` exists in the codebase, suggesting this construction is known

## Evidence against

- No specific statistical evidence distinguishes this from standard additive
  autokey
- The identity element under prime-value arithmetic may not correspond to a
  plausible plaintext rune frequency

## Scripts

- Compute the identity element of the prime-value TR and check if it maps to a
  rune whose expected frequency matches the observed 0.68% doublet rate

## Verdict

Unresolved. A natural extension of the autokey hypothesis using Cicada's own
mathematical framework. Needs computational testing to determine the identity
element and whether the resulting decryption produces any signal.
