---
type: hypothesis
---
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

- **Repeated plaintext fragments propagate — quantified (July 2026)**: under
  ANY plaintext autokey C[i] = TR[P[i-1]][P[i]] (any tabula recta), a repeated
  plaintext (n+1)-gram forces a repeated ciphertext n-gram, position-free.
  Measured on the recovered solved-section plaintext (2,797 runes, the same
  author's register) and scaled to corpus size
  (`experiments/plaintext_autokey_closure.py`): predicted repeated 4-gram
  pairs >= ~27,500, 5-grams >= ~19,700, 6-grams >= ~14,300. Observed in the
  clean corpus: 129 / 6 / 1 — all at the doublet-corrected chance level
  (124 ± 10 / 4 ± 2). A kill margin of more than two orders of magnitude,
  independent of the tabula recta.
- **Less diffusion**: Plaintext autokey propagates errors in one direction
  during decryption (a wrong guess affects only one subsequent rune). This makes
  it more vulnerable to known-plaintext attacks, which is uncharacteristic of
  Cicada's design philosophy for the harder unsolved sections.
- **Ciphertext autokey was used in solved sections**: Cicada used ciphertext
  autokey (specifically Beaufort) in the solved LP sections, making plaintext
  autokey a less likely choice for the unsolved ones.

## Scripts

- `experiments/plaintext_autokey_closure.py` — the quantified repeat-rate
  comparison (predicted vs observed repeated n-grams, TR-independent).

## Verdict

Disproved, quantitatively and for every tabula recta at depth 1. Plaintext
autokey transports the plaintext's repeated (n+1)-grams into repeated
ciphertext n-grams; the author's own register predicts tens of thousands of
repeated 4-grams and the corpus has 129 — exactly chance. The style
arguments (diffusion, Cicada precedent) are secondary; the repeat census
alone closes the class.
