# Hypothesis: Autokey with Gematria Primus Arithmetic

## Claim

The cipher uses autokey where the encryption formula uses Cicada's Gematria
Primus prime values directly:
C[i] = (prime(P[i]) + prime(C[i-1])) mod 29.

## Status

**Status**: disproved

## Mechanism

Each rune has a prime value assigned by Cicada's Gematria Primus. Instead of
using the rune's index in modular arithmetic, the cipher uses the prime value.
This makes the encryption non-linear in the rune index.

This differs from the prime-value tabula recta hypothesis in that primes are
used directly in the formula rather than to construct a lookup table (though
the two are mathematically related).

## Evidence for

- Cicada's entire mythology revolves around primes and the Gematria Primus
- Thematically consistent with Cicada's style of encoding mathematical
  concepts into their puzzles
- 29 being prime ensures the arithmetic works cleanly

## Evidence against

- **Preceding-rune split disproof**: This is a ciphertext autokey with a
  specific fixed TR (defined by prime arithmetic). Splitting the ciphertext by
  C[i-1] should give 29 streams with English-like IOC. Measured: mean IOC
  0.0354, indistinguishable from random. See `disprove_autokey_split.py`.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof of all
  single-layer ciphertext autokey variants.
- See also `src/aldegonde/pasc.py` for `valueTR()` implementation.

## Related

- `ciphertext-autokey.md` — General disproof applies here.

## Verdict

Disproved. This is a specific case of ciphertext autokey with a fixed TR,
ruled out by the preceding-rune split test.
