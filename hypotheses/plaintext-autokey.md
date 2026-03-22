# Hypothesis: Plaintext Autokey Cipher

## Claim

The unsolved sections use a plaintext autokey cipher, where each plaintext rune
(rather than ciphertext rune) feeds back as the key for the next encryption.

## Status

**Status**: disproved

## Mechanism

In a plaintext autokey cipher, the previous plaintext rune is used as the key:

- Vigenere plaintext autokey: C[i] = P[i] + P[i-1] mod 29
- Beaufort plaintext autokey: C[i] = P[i-1] - P[i] mod 29

The feedback comes from the plaintext side, not the ciphertext side.

## Evidence for

- Autokey ciphers (in general) have no fixed period, consistent with the
  Friedman test finding nothing
- Plaintext autokey is a classical technique contemporary with Cicada's other
  cipher choices

## Evidence against

- **Repeated plaintext fragments propagate**: In plaintext autokey, if the same
  plaintext sequence appears at two different positions, it produces the same
  ciphertext sequence (because the feedback depends on plaintext, which is
  identical in both cases). This creates repeated ciphertext fragments at a rate
  that reflects the natural repetition rate of the plaintext language. The
  unsolved sections show very few repeated fragments, consistent with ciphertext
  autokey (where feedback depends on position-dependent ciphertext) but not with
  plaintext autokey on English text.
- **Less diffusion**: Plaintext autokey propagates errors in one direction
  during decryption (a wrong guess affects only one subsequent rune). This makes
  it more vulnerable to known-plaintext attacks, which is uncharacteristic of
  Cicada's design philosophy for the harder unsolved sections.
- **Ciphertext autokey was used in solved sections**: Cicada used ciphertext
  autokey (specifically Beaufort) in the solved LP sections, making plaintext
  autokey a less likely choice for the unsolved ones.

## Scripts

- Compare the rate of repeated n-grams (n >= 4) in the ciphertext against what
  plaintext autokey would produce from English-like input. Ciphertext autokey
  produces fewer repeats because the feedback is position-dependent.

## Verdict

Disproved. Plaintext autokey produces more repeated ciphertext fragments than
observed, because identical plaintext sequences encrypt identically regardless
of position. The low repeat rate in the unsolved sections is consistent with
ciphertext autokey but not plaintext autokey.
