---
type: hypothesis
---
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
  specific fixed TR. The prime values mod 29 are NON-injective (F, I and D
  all collide at residue 2; see `running-key-math-sequence.md`), so the TR
  rows are not permutations — but merging symbols can only RAISE a group's
  IOC, so each C[i-1] stream should still show English-like IOC or higher.
  Measured: mean IOC 0.0354, indistinguishable from random. See
  `disprove_autokey_split.py`.
- **Non-invertibility**: because the rows are non-injective, runes sharing
  a prime residue (e.g. F, I, D) encrypt identically under the same key
  rune and cannot be distinguished on decryption. The mechanism is not a
  workable cipher at all, independent of any statistic.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof of all
  single-layer ciphertext autokey variants.

## Related

- `ciphertext-autokey.md` — General disproof applies here.

## Verdict

Disproved. This is a specific case of ciphertext autokey with a fixed TR,
ruled out by the preceding-rune split test — and independently unworkable:
the non-injective prime-value rows make decryption impossible.
