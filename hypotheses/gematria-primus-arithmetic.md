# Hypothesis: Autokey with Gematria Primus Arithmetic

## Claim

The cipher uses autokey where the encryption formula uses Cicada's Gematria
Primus prime values directly:
C[i] = (prime(P[i]) + prime(C[i-1])) mod 29.

## Status

**Status**: unresolved

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

- The identity element under prime arithmetic is different and may not
  correspond to a plausible plaintext rune frequency
- No statistical evidence distinguishes this from standard autokey
- The prime mapping is non-linear, making cryptanalysis harder but also making
  it harder to verify

## Scripts

- Compute what the "doublet-causing" plaintext rune would be under this
  arithmetic and check its expected frequency.
- See also `src/aldegonde/pasc.py` for `valueTR()` implementation.

## Verdict

Unresolved. Thematically appealing given Cicada's prime obsession, but needs
computational work to test.
