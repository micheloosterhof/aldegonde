# Hypothesis: Shared Positional Keystream Resetting at Page/Section Boundaries

## Claim

The cipher is C[i] = f(P[i], K[i]) for some per-position combining function f
(Vigenere, Beaufort, or any fixed family of 29 substitution alphabets indexed
by K), where the keystream K is the SAME for every page (or section) and
restarts at each page (or section) boundary. The keystream itself can be
anything — a math sequence, a passage of text, true random — it only has to
be reused across pages.

## Status

**Status**: disproved

## Mechanism

Each page is encrypted independently with an identical keystream starting at
its first rune (the way the solved AN END page restarts the prime-1 stream).
Because the same K[k] is applied at offset k of every page, aligning two
pages position-by-position cancels the key: positions where the plaintexts
agree produce identical ciphertext runes, so the aligned coincidence rate
equals the plaintext IOC (~1.7 normalized, i.e. ~70% more coincidences than
random) regardless of what the keystream is.

## Evidence for

- The solved AN END page restarts its keystream (prime(n)-1) at the top of
  the page, so per-page keystream reset is an attested Cicada behavior.
- Preserved word boundaries suggest per-page, position-synchronous
  encryption rather than fractionation across pages.

## Evidence against

- **Page-aligned kappa**: all 1,485 pairs of the 55 unsolved pages, aligned
  position-by-position: 10,751 coincidences vs 10,729 expected by chance,
  z = +0.22 sigma (ratio 1.002). An identical reused keystream would give
  ratio ~1.7 (hundreds of sigma at this sample size).
- **Section-aligned kappa**: all pairs of the 10 `$`-sections: z = -0.80
  sigma (ratio 0.978). Same conclusion for section-boundary reset.
- Top single page pair is (28,42) at +3.9 sigma, consistent with the
  expected maximum order statistic over 1,485 pairs; no pair stands out
  enough to suggest two pages sharing a key.

## Predictions

If any two text units shared a positional keystream of this form, their
aligned coincidence ratio would approach the plaintext IOC. None do.

## Scripts

- `experiments/aligned_kappa_nulls.py`

## Related

- `running-key-math-sequence.md` — disproved the specific sequences with
  positional subtraction; this file generalizes to ALL shared boundary-reset
  keystreams, known or unknown.
- `periodic-polyalphabetic.md` — a periodic key is a special case of a
  shared keystream and is independently disproved.

## Verdict

Disproved. Whatever the cipher is, pages do not share a positional keystream
that resets at page or section boundaries. Remaining keystream-style options
require either a different keystream per page (e.g. keyed by page number or
content) or feedback from the text itself (autokey-like state), which aligned
kappa cannot cancel.
