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

## Predictions

If the key source is identified, subtracting it from the ciphertext produces
English. Known candidate key texts can be tested directly.

## Scripts

None yet. Should test: solved LP sections as key, reversed LP, Cicada's
other published texts.

## Verdict

Unresolved. The near-perfect flatness of the distribution argues against
English+English running key (which would show slight non-uniformity). But
the key source might not be English.
