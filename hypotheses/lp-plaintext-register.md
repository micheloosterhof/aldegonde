---
type: observation
---
# Observation: The LP's Own Plaintext Register, and a Doublet Rate 2.7 Sigma Below Chance

## Feature

Every register-matched control in this directory draws its English from an outside
prose corpus. `solved-page-testbed.md` now supplies the alternative: **1,963 runes in
486 words of the author's own plaintext**, pooled from the six pages that are
plaintext in the transcription and the five recovered as monoalphabetic (which are
position-preserving, so their word boundaries survive exactly).

**Word lengths**, mean 4.04 over 486 words:

| runes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8+ |
|---|---|---|---|---|---|---|---|---|
| share | 3.3% | 23.9% | 24.5% | 16.0% | 8.8% | 9.3% | 6.4% | 7.6% |

The unsolved body averages 4.42, so the registers differ by 0.38 runes per word. The
front matter is didactic and the body is not, so nothing here should be assumed to
carry over unchanged.

**This reproduces an existing result, which is the check that the corpus is built
right.** Against this register the body's length-2 bucket runs at ratio 0.67, z = −10.1,
and lengths 1, 3 and 6 match (z = +0.3, +0.4, −1.2). `two-rune-deficit.md` independently
reports ratio 0.66 and z ≈ −10 against the solved pages with the same buckets matching.
Two separately written pipelines agreeing to the second decimal is worth more than
either on its own.

**Unigrams**: commonest are E 248, O 190, A 144, R 135, S 133, T 128, N 112, I 97;
chi2 against uniform is 1,574 on 28 df. That is the distribution the cipher flattens
to the body's 26.4.

**Within-word coincidence profile** (chance = 1/29 = 0.0345):

| lag | matches | pairs | rate | × chance | z |
|---|---|---|---|---|---|
| 1 | 32 | 1477 | 0.0217 | 0.63 | **−2.70** |
| 2 | 43 | 1007 | 0.0427 | 1.24 | +1.43 |
| 3 | 37 | 653 | 0.0567 | 1.64 | +3.11 |
| 4 | 28 | 418 | 0.0670 | 1.94 | +3.64 |
| 5 | 15 | 261 | 0.0575 | 1.67 | +2.04 |
| 6 | 10 | 147 | 0.0680 | 1.97 | +2.23 |
| 7 | 6 | 78 | 0.0769 | 2.23 | +2.05 |

## The headline: plaintext doublets are rare, not chance

**The LP's plaintext repeats an adjacent letter at 0.0217, which is 2.70 sigma BELOW
1/29** (p = 0.007 against the null's own standard error). English avoids adjacent repeats inside words — and runeglish sharpens
that, because the digraph collapses (TH, EA, NG, OE to single runes) remove exactly
the cases that would otherwise produce them.

Every other lag runs *above* chance, 1.24x to 2.23x, which is ordinary letter-frequency
concentration. Distance 1 is the only suppressed one, and it is suppressed in the
plaintext before any cipher touches it.

## Status

**Status**: confirmed (measurement), n = 1,963 runes in 486 words.
`experiments/lp_plaintext_register.py`. Register caveat above is not a formality: this
is the front matter, not the body.

**Corrected 2026-09-21, same day as first written.** The first version of this file
tokenized on line wraps, which `lp_corpus.load_clean` explicitly treats as internal to
a word. That split words at every wrap and inflated the short buckets: it reported mean
length 3.67 (really 4.04), a 9.3% one-rune share (really 3.3%), and d1 = 0.0203 at 3.8
sigma (really 0.0217 at 2.70). The headline direction survives; its size does not, and
the agreement with `two-rune-deficit.md` above only appeared once the bug was fixed.

## What it does and does not settle

It **does** replace an assumption with a measurement anywhere a model needs the rate at
which LP plaintext repeats a letter. Any null that generates "would-be doublets" at
1/29 is mis-specified by a factor of 1.6.

It does **not**, on its own, refute `quagmire-dodge.md`'s parameter-free doublet fit,
and an earlier draft of this file claimed that it did. That model writes

    P(ciphertext doublet) = P(next schedule step is zero) x P(would-be doublet)
                          = 1/5 x (a shift diagonal)

and the second factor is the plaintext delta distribution evaluated at −s_k in K
coordinates, **not** the plaintext doublet rate. The two coincide only when s_k = 0.
Substituting 0.0217 for 1/29 there would move the prediction from 0.00690 (z = −0.78
against the body's observed 0.00628) to 0.00434, which looks like a two-sigma failure —
but the substitution is not licensed, so that number is not a result.

An earlier version of this section asked, as an open question, whether the correct
delta term still averages 1/29 on this register. **It does, by construction**: the
deltas are a distribution over 29 values and sum to 1, so their mean is exactly 1/29
whatever the register. `quagmire-dodge.md` already states that the second factor is
key-dependent and that only the 1/5 is parameter-free. There was nothing there to
settle, and the question is withdrawn.

What the measurement above *does* bear on is any model or null that needs the rate at
which LP plaintext repeats a letter — that quantity is 0.0217, not 1/29.

## Scripts

- `experiments/lp_plaintext_register.py` — the corpus and all the tables above.

## Related

- `solved-page-testbed.md` — the source of the plaintext.
- `quagmire-dodge.md` — the model whose second factor this bears on, unresolved.
- `doublet-suppression.md` — the ciphertext side, 0.00628 within words.
