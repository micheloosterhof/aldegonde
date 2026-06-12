# Hypothesis: Running Key from Another Text

## Claim

The cipher is C[i] = P[i] + K[i] mod 29, where K is derived from another
text (possibly the solved LP sections, another Cicada publication, or a
well-known text converted to runeglish).

## Status

**Status**: unresolved

## Mechanism

A "book cipher" variant: the keystream comes from a specific text source.
Each key rune is the rune at the corresponding position in the key text.
Simple additive or subtractive combination.

## Evidence for

- Running key ciphers have no period (key is as long as the message)
- If the key text is also English runeglish, the output would have specific
  statistical properties that depend on the interaction of two English texts
- Cicada has multiple texts (solved LP sections, other publications) that
  could serve as key material

## Evidence against

- Running key of English + English produces IOC ≈ sum of squares of
  convolution, which is typically detectable (IOC around 0.038-0.042 for
  26-letter English, not as flat as observed 0.0345). Quantified: a
  runeglish-minus-runeglish difference has nIoC ~ **1.0501** (computed from
  the corpus unigrams), well above the observed flat 1.0.
- The output distribution of English+English mod 29 would not be perfectly
  flat — it would have slight peaks
- The doublet suppression mechanism is unclear for simple additive running key
- The word-aligned repeated phrase ᛞᛄᚢ-ᛒᛖᛁ (`repeated-phrase-dju-bei.md`)
  would be pure chance (p < 1e-3) under a non-repeating running key
- **No key depth anywhere** (`experiments/depth_search.py`, June 2026): the
  decisive test for a running key is the difference-stream IOC at every lag
  — wherever the key realigns, Diff_d = P[i]-P[i+d] reveals a
  runeglish-difference at nIoC ~ 1.05. Scanned ALL lags 2..6520 (including
  every section-length-scaled lag, in case the key is a section of the
  book), in both Vigenere and Beaufort directions. After correcting the IOC
  variance law (sd ~ 1/n, not 1/sqrt(n)) and using a doublet-suppressed
  surrogate as the null, the observed excess (16 lags at z>4, max z 5.52,
  all at nIoC <= 1.02) is INDISTINGUISHABLE from the no-depth surrogate
  (mean 11.9 lags at z>4, max z 5.19) — i.e. it is entirely the
  doublet-suppression baseline, not a repeating key. No spike anywhere
  reaches the ~1.05 a real depth requires; none is localized.

## Predictions

If the key source is identified, subtracting it from the ciphertext produces
English. Known candidate key texts can be tested directly. But a SELF-key
(the cipher's own text, any section, forward or reversed, at any offset) is
now excluded by the depth search: self-keys necessarily create depth, and
there is none.

## Scripts

- `experiments/depth_search.py` — difference-stream IOC at every lag, with
  the runeglish-difference calibration and doublet-suppressed surrogate
  null. Conclusive negative for key depth / repeating or self-referential
  keys.

## Verdict

Unresolved but tightly bounded. The near-perfect flatness argues against a
single English+English running key (which would leave nIoC ~ 1.05), and the
depth search rules out ANY repeating or self-referential key (no depth at
any lag). What survives is only a NON-repeating key from an external source
at least as long as the text (13,041 runes) and at least as flat as a
single English difference — i.e. effectively a one-time pad or a long
high-entropy external source. Such a key leaves no statistical handle; the
hypothesis is unfalsifiable without identifying the source.
