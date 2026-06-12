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
  26-letter English, not as flat as observed 0.0345)
- The output distribution of English+English mod 29 would not be perfectly
  flat — it would have slight peaks
- The doublet suppression mechanism is unclear for simple additive running key
- **Tested negative (2026-06)**: the Parable (forward and reversed) and the
  full master transcription were slid across the clean unsolved corpus at
  every alignment, both Vigenere (C-K) and Beaufort (C+K). Max |z| 6.2, but
  shuffled-key null scans reach 5.2-8.4 — noise, and the best-hit decrypt is
  gibberish. Keystream reuse *within* the corpus is also ruled out at every
  lag (diff/sum IOC scan). See `cryptodiagnostics-page0-58.md`.

## Predictions

If the key source is identified, subtracting it from the ciphertext produces
English. Known candidate key texts can be tested directly.

## Scripts

- `experiments/lp_cryptodiagnostics.py` (section H3) — Parable and master
  transcription as keys at all alignments. Still untested: decrypted
  plaintexts of the keyword-solved sections, Cicada's other published texts.

## Verdict

Unresolved but weakened. The near-perfect flatness of the distribution argues
against English+English running key, and the directly testable candidate key
texts (Parable, master transcription, the corpus against itself at every lag)
are now ruled out. The key source, if any, is not among Cicada's available
rune texts and is statistically indistinguishable from uniform random.
