---
type: hypothesis
---
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

The measured negative (aligned kappa flat at page and section boundaries)
is recorded as a standalone observation in `aligned-kappa-no-reset.md`;
this file is the hypothesis it disproves.

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
kappa cannot cancel. The per-page-keyed variant is not tracked as a separate
file: with a different pad per page it is observationally an OTP with no
handle, i.e. the standing `stream-cipher-no-repeat.md` problem (and the
page-spanning doublet-suppression continuity plus the mid-word page breaks
argue against any per-page state reset at all — see `five-block-boundary.md`
co-tiling notes and `aligned-kappa-no-reset.md`).

## The disproof survives a preventer, unlike the Friedman one (September 2026)

Page-aligned kappa indexes runes by absolute position, so
`preventer-blinds-absolute-tests.md` puts it in the category a clock perturbation
damages. It is worth checking whether the damage is enough to matter, because the same
category contains the Friedman scan, which a 2.4% interrupt rate blinds completely.

Simulating 20 pages of 230 runes sharing one positional keystream, plaintext drawn from
the author's own runes, with interrupts shifting the phase:

| interrupt rate | aligned ratio | sigma |
|---|---|---|
| 0.000 | 1.799 | 31.0 |
| 0.012 | 1.320 | 12.4 |
| 0.024 | 1.112 | 4.3 |
| 0.050 | 1.147 | 5.7 |

At the 2.4% rate that makes a period-8 Vigenère invisible to Friedman, a shared
positional keystream still shows at **z = +4.3 on 190 simulated page pairs**. The real
corpus has 1,485 pairs, so the same effect there would read near **z = +12**. The
observed value is z = +0.22.

**So this disproof is robust where the Friedman one was not.** The difference is that
aligned kappa compares two pages at the same index: an interrupt shifts one of them, but
the two still agree wherever their interrupt counts happen to match, which is often
enough to keep most of the signal. Friedman instead assigns every rune to a coset by
absolute index, so one interrupt corrupts everything downstream.

*Simulation caveat:* rates above ~5% are not reported because the harness emits a fixed
rune as the interrupter, so at high rates the pages share that rune at aligned positions
and the ratio rises again spuriously — an artifact of the harness, not a property of the
cipher. The rates that matter here are well below that.
