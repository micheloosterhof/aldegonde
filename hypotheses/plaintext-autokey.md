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
- **Every tapped depth dies the same way (July 2026)**: for
  C[i] = TR[P[i-L]][P[i]] the cipher n-gram is a function of the
  augmented n-gram over A[i] = (P[i-L], P[i]), so repeated A-stream
  n-grams force repeated ciphertext n-grams — the depth-1 argument,
  exactly generalized. Measured on the same register and scaled
  (`experiments/plaintext_autokey_depth_closure.py`, validated against
  direct simulation): predicted repeated 4-grams range from 27,550
  (L=1) to 4,785 (L=10) against 129 observed — margins 214x down to
  37x. The lag-5 tap, the variant the lag-5 anomaly most suggests,
  predicts 8,475 (66x). Split tests cannot see plaintext-side feedback
  at any depth; this closure does, and closes the stream-running form
  at depths 1-10 (word-boundary-reset variants are a different
  mechanism, closed in `word-boundary-reset-autokey.md`).
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
- `experiments/plaintext_autokey_depth_closure.py` — the same closure at
  taps L = 1..10 via the augmented-stream bound, simulation-validated.

## Verdict

Disproved, quantitatively, for every tabula recta and every
stream-running tap depth 1-10 (including the lag-5 tap the d5 anomaly
might have suggested; reset variants are closed separately in
`word-boundary-reset-autokey.md`).
Plaintext autokey transports the plaintext's repeated joint windows into
repeated ciphertext n-grams; the author's own register predicts thousands
to tens of thousands of repeated 4-grams at every depth and the corpus
has 129 — exactly chance. The style arguments (diffusion, Cicada
precedent) are secondary; the repeat census alone closes the class.
