---
type: hypothesis
---
# Hypothesis: Running Key from Another Text

## Claim

The cipher is C[i] = P[i] + K[i] mod 29, where K is derived from another
text (possibly the solved LP sections, another Cicada publication, or a
well-known text converted to runeglish).

## Status

**Status**: disproved

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
- **Simulation** (`experiments/mechanism_fingerprint.py`): Markov runeglish
  plaintext + Markov runeglish key, C = P + K mod 29, at full corpus length:
  doublet rate 3.55-3.63% (observed: 0.66%), nIoC 1.048-1.050 (observed:
  1.000 — at 13k runes a 1.05 ratio is many sigma), 17-19 triplets
  (observed: 0). Three independent contradictions.
- **Candidate key texts tested negative (2026-06)**: the Parable (forward and
  reversed) and the full master transcription were slid across the clean
  unsolved corpus at every alignment, both Vigenere (C-K) and Beaufort (C+K).
  Max |z| 6.2, but shuffled-key null scans reach 5.2-8.4 — noise, and the
  best-hit decrypt is gibberish. Keystream reuse *within* the corpus is also
  ruled out at every lag (diff/sum IOC scan). See
  `cryptodiagnostics-page0-58.md`.
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

- `experiments/mechanism_fingerprint.py` — simulated fingerprint comparison.
- `experiments/lp_cryptodiagnostics.py` (section H3) — Parable and master
  transcription as keys at all alignments. Still untested: decrypted
  plaintexts of the keyword-solved sections, Cicada's other published texts.
- `experiments/depth_search.py` — difference-stream IOC at every lag, with
  the runeglish-difference calibration and doublet-suppressed surrogate
  null. Conclusive negative for key depth / repeating or self-referential
  keys.

## Verdict

Disproved for any language-text key (runeglish/English statistics): the
simulated fingerprint contradicts the observed corpus on doublet rate, IoC,
and triplets simultaneously, the directly testable candidate key texts
(Parable, master transcription, the corpus against itself at every lag) are
ruled out, and the depth search excludes ANY repeating or self-referential
key. What survives is only a NON-repeating, non-language key from an
external source at least as long as the text (13,041 runes) and
statistically indistinguishable from uniform random — i.e. effectively a
one-time pad. That is not covered by this hypothesis — it is a generic
stream cipher, see `stream-cipher-no-repeat.md` (where the doublet
constraint requires ciphertext feedback that a fixed key text cannot
provide), and it leaves no statistical handle without identifying the
source.
