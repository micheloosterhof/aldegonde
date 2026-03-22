# Hypothesis: Prime-Value Tabula Recta Autokey

## Claim

The cipher uses an autokey mechanism where the tabula recta is constructed from
Cicada's prime-rune associations (Gematria Primus) rather than standard
additive arithmetic.

## Status

**Status**: disproved

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

- **Preceding-rune split disproof**: This is a ciphertext autokey with a
  specific fixed TR. Splitting the ciphertext by C[i-1] should give 29 streams
  with English-like IOC (permutations preserve IOC). Measured: mean IOC 0.0354,
  indistinguishable from random. See `disprove_autokey_split.py`.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof of all
  single-layer ciphertext autokey variants.

## Related

- `ciphertext-autokey.md` — General disproof applies here.

## Verdict

Disproved. This is a specific case of ciphertext autokey with a fixed TR,
ruled out by the preceding-rune split test.
