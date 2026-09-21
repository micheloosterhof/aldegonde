---
type: observation
---
# Observation: The LP's Own Plaintext Register, and a Doublet Rate 3.8 Sigma Below Chance

## Feature

Every register-matched control in this directory draws its English from an outside
prose corpus. `solved-page-testbed.md` now supplies the alternative: **1,963 runes in
535 words of the author's own plaintext**, pooled from the six pages that are
plaintext in the transcription and the five recovered as monoalphabetic (which are
position-preserving, so their word boundaries survive exactly).

**Word lengths**, mean 3.67:

| runes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8+ |
|---|---|---|---|---|---|---|---|---|
| share | 9.3% | 24.7% | 23.4% | 15.5% | 8.6% | 7.3% | 5.4% | 5.8% |

The unsolved body averages 4.43 runes per word (12,956 / 2,928), so the two registers
differ by 0.76 runes per word. That gap is itself a caution: the front matter is
didactic and aphoristic, the body is not, and no measurement here should be assumed to
carry over unchanged.

**Unigrams**: commonest are E 248, O 190, A 144, R 135, S 133, T 128, N 112, I 97;
chi2 against uniform is 1,574 on 28 df. That is the distribution the cipher flattens
to the body's 26.4.

**Within-word coincidence profile** (chance = 1/29 = 0.0345):

| lag | matches | pairs | rate | × chance | z |
|---|---|---|---|---|---|
| 1 | 29 | 1428 | 0.0203 | 0.59 | **−2.94** |
| 2 | 41 | 943 | 0.0435 | 1.26 | +1.51 |
| 3 | 33 | 590 | 0.0559 | 1.62 | +2.86 |
| 4 | 26 | 362 | 0.0718 | 2.08 | +3.89 |
| 5 | 13 | 217 | 0.0599 | 1.74 | +2.05 |
| 6 | 7 | 118 | 0.0593 | 1.72 | +1.48 |
| 7 | 4 | 58 | 0.0690 | 2.00 | +1.44 |

## The headline: plaintext doublets are rare, not chance

**The LP's plaintext repeats an adjacent letter at 0.0203 ± 0.0037, which is 3.8 sigma
BELOW 1/29.** English avoids adjacent repeats inside words — and runeglish sharpens
that, because the digraph collapses (TH, EA, NG, OE to single runes) remove exactly
the cases that would otherwise produce them.

Every other lag runs *above* chance, 1.26x to 2.08x, which is ordinary letter-frequency
concentration. Distance 1 is the only suppressed one, and it is suppressed in the
plaintext before any cipher touches it.

## Status

**Status**: confirmed (measurement), n = 1,963 runes.
`experiments/lp_plaintext_register.py`. Register caveat above is not a formality: this
is the front matter, not the body.

## What it does and does not settle

It **does** replace an assumption with a measurement anywhere a model needs the rate at
which LP plaintext repeats a letter. Any null that generates "would-be doublets" at
1/29 is mis-specified by a factor of 1.7.

It does **not**, on its own, refute `quagmire-dodge.md`'s parameter-free doublet fit,
and an earlier draft of this file claimed that it did. That model writes

    P(ciphertext doublet) = P(next schedule step is zero) x P(would-be doublet)
                          = 1/5 x (a shift diagonal)

and the second factor is the plaintext delta distribution evaluated at −s_k in K
coordinates, **not** the plaintext doublet rate. The two coincide only when s_k = 0.
Substituting 0.0203 for 1/29 there moves the prediction from 0.00690 (z = −0.78
against the body's observed 0.00628) to 0.00406 (z = +2.04), which looks like a
two-sigma failure — but the substitution is not licensed, so that number is not a
result. What is open, and worth a proper test, is whether the correct delta term
evaluated on this register still averages 1/29.

## What would settle it

`delta_vectors` in `quagmire_schedule_census.py` already computes the delta
distribution a model needs. Running it against this register instead of the prose
tables, and reporting the diagonal at each candidate −s_k, would replace the averaged
1/29 with the LP's own figure and decide the question. That is a small change and has
not been done.

## Scripts

- `experiments/lp_plaintext_register.py` — the corpus and all the tables above.

## Related

- `solved-page-testbed.md` — the source of the plaintext.
- `quagmire-dodge.md` — the model whose second factor this bears on, unresolved.
- `doublet-suppression.md` — the ciphertext side, 0.00628 within words.
