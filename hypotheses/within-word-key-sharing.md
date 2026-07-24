---
type: hypothesis
---
# Hypothesis: Within-Word Distance-5 Key Sharing (Per-Word 5-Periodic Key)

> Harvested from an earlier investigation branch and re-verified July 2026:
> `experiments/within_word_delta_mixture.py` reproduces the 3.63σ rejection
> and the 6.45-nat copy-over-mixture margin; the plaintext controls reproduce
> (in-domain 6.36%, lexicon 6.11%); `delta5_generalization.py` reproduces the
> zero-vs-nonzero split (sep-1 z=+3.31, sep-4 z=+3.13, nonzero at chance).
> Read the reconciliation note below before treating "literal copying" as a
> conclusion competing with the length-clocked walk — it is not.

## Reconciliation with the walk model (read first)

This file disproves **additive** key-sharing: if positions k and k+5 shared an
*additive* key element, the ciphertext delta would equal the plaintext delta
and imprint the plaintext's nonzero lag-5 difference structure on the histogram.
It does not — only the 0 (equality) bin is elevated. But that "0-bin only"
signature is **exactly what a mixed same-alphabet leak produces too**: under the
length-clocked walk (`length-clocked-walk.md`), positions 5 apart in a word use
the same *mixed* substitution `base_w`, so `P[k]=P[k+5]` gives `C[k]=C[k+5]`
(equality leaks) while nonzero deltas scramble flat. So the walk's echo and a
"literal back-reference copy" are **observationally identical on this statistic**
— both are equality-only mechanisms. This test therefore kills the *additive*
(Vigenère-style) reading and leaves the two survivors main already carries: the
walk's mixed-alphabet echo and the `lag5-back-reference.md` copy family. Where
the verdict below says "literal copying", read "an equality-only mechanism
(mixed-alphabet leak or back-reference copy), not an additive key".

## Claim

Within a word, positions k and k+5 are encrypted with the same key element
— e.g. a per-word key (re)started at each word with a 5-cycle, or any
mechanism that makes the key locally 5-periodic inside words. This was the
leading "word-scoped key state" reading of the within-word distance-5
coincidence excess (`within-word-d5-coincidence.md`).

## Status

**Status**: disproved

## Mechanism

If K[k+5] = K[k] whenever k and k+5 lie in the same word, then for those
pairs the ciphertext difference equals the plaintext difference:

    (C[k+5] - C[k]) mod 29 = (P[k+5] - P[k]) mod 29

so the within-word distance-5 delta histogram must be the mixture

    p = f * Q + (1 - f) * U

where Q is the plaintext lag-5 difference distribution, U is uniform, and
f is the fraction of affected pairs. The match excess (the 0 bin) pins f:
with Q(0) measured at 1.77x uniform (frequency-weighted runeglish lexicon)
to 1.84x (Cicada's own solved plaintext), the observed 4.92% match rate
forces f ~= 0.55. The same f must then imprint Q's nonzero structure on
the nonzero bins — that is the falsifiable content.

## Evidence (the kill)

Two independent plaintext controls (`experiments/plaintext_control_corpus.py`):

- IN-DOMAIN: the six constant-transform-decodable solved sections of the
  master transcription (A WARNING, SOME WISDOM, A COAN, THE LOSS OF
  DIUINITY, AN INSTRUCTION, PARABLE — 2,058 runes, decodes printed and
  eyeballed). Within-word d=5 match rate **6.36%** (18/283).
- LEXICON: top-30k English words transliterated to Gematria-Primus
  runeglish, frequency-weighted (within-word statistics depend only on
  the word multiset). Within-word d=5 match rate **6.11%**; full 29-bin
  Q measured with tight error bars. Both controls agree with the
  corpus-wide runeglish IoC (~1.78/29 = 6.1%).

The discriminator (`experiments/within_word_delta_mixture.py`), on the
2,073 within-word (k, k+5) pairs of the clean unsolved corpus:

| model (1 parameter each) | fit | log-likelihood |
|---|---|---|
| uniform | — | -6980.40 |
| **copy: only the 0 bin inflated** | e = 0.0152 | **-6974.42** |
| mixture, ML f, lexicon Q | f = 0.265 | -6976.13 |
| mixture, ML f, in-domain Q | f = 0.007 | -6980.39 |
| mixture, f pinned by the 0 bin | f = 0.554 | -6980.87 |

- The observed delta histogram is **flat off zero** (nonzero bins 0.62–1.18
  x uniform, noise-compatible); only the 0 bin (1.43x) is special.
- Optimal one-number test (projection of nonzero-bin deviations onto the
  lexicon-Q direction, word-length permutation null preserving the rune
  stream byte-for-byte): observed T = +0.32, null -0.07 ± 0.29
  (z = +1.34, n.s.). Key sharing at the pinned f = 0.554 predicts
  T = +1.52 ± 0.33 — **rejected at z = +3.6**, and it loses 6.4 nats of
  log-likelihood to the copy model.
- Power check: even at the unconstrained ML value f = 0.265 the projection
  test had 83% power at the 5% level; at f = 0.554 essentially 100%. The
  null result is not for lack of power.
- Caveat considered: a plaintext whose lag-5 difference distribution has
  an inflated 0 bin but flat nonzero bins would evade the test, but that
  requires a single-hot letter distribution, which English/runeglish is
  not (both controls show clear nonzero structure, e.g. bins at 1.45x and
  0.58x uniform).

Corroborating negatives from the same battery:

- Stream-level generalization (`experiments/delta5_generalization.py`):
  repeated **nonzero** lag-5 deltas at separations 1 and 4 are exactly at
  chance (z = +0.21 / -0.14 against 4,000 doublet-suppressed surrogates)
  while the zero value is elevated (z = +3.3 / +3.1). Any locally
  5-periodic-up-to-drift key (K[i+5] = K[i] + t) would elevate all delta
  values equally; only literal equality is special.
- No word-edge anchoring of matches (start-aligned z = -0.97, end-aligned
  z = -0.76; `experiments/within_word_match_anatomy.py`) and no spatial
  clustering of the 91 hit words (window-variance z = -0.99) — no sign of
  persistent per-word key state.
- d=10 within-word tail: 2/88 = 2.3% (key 5-cycle predicts ~6%; low power
  but leaning the wrong way for key-sharing).
- Negative control: the encrypted-but-solved Vigenère-class sections of
  the master transcription (1,563 runes) show 12/254 = 4.7% (p = 0.30,
  underpowered but consistent with no excess for a non-copy cipher).

## What replaces it

The within-word d=5 excess behaves like **literal glyph copies**: ~1.5% of
within-word (k, k+5) pairs (~31 pairs) carry a verbatim repeat of the
glyph five back, with no additive relation, no positional anchor, no
memory, and no leak of plaintext difference structure. This is the same
conclusion the value-literal stream test reaches for the paired {1,4}
events. See `lag5-back-reference.md` (nulls / back-references / stutters —
still mutually indistinguishable) and the word-boundary constraint: the
copy mechanism is word-scoped (cross-word pairs match at exactly 1/29,
even though plaintext would offer ~6% cross-word repeats too — the rule
sees word boundaries).

## Scripts

- `experiments/plaintext_control_corpus.py` — builds both plaintext
  controls, writes `experiments/plaintext_control_stats.json`.
- `experiments/within_word_delta_mixture.py` — the model comparison,
  projection test, permutation null, and power analysis.
- `experiments/delta5_generalization.py` — the stream-level value-literal
  test.
- `experiments/within_word_match_anatomy.py` — position/alignment/
  clustering anatomy.
- `experiments/solved_section_control.py` — the solved-ciphertext
  negative control and position-profile comparison.

## Related

- `within-word-d5-coincidence.md` — the anomaly this hypothesis tried to
  explain.
- `lag5-digraph-structure.md` — the paired-event face; value-literality
  added there.
- `lag5-back-reference.md` — the surviving explanation family.
- `position-within-word.md`, `word-level-autokey.md` — earlier word-keyed
  families, already disproved by split tests.

## Verdict

Disproved with power to spare. The within-word distance-5 excess is not
shared key material: the pinned mixture over-predicts the nonzero-bin
structure by 3.6 sigma and loses 6.4 nats to a one-parameter copy model.
Together with the stream-level value-literality of the {1,4} pairing,
every additive reading of the lag-5 phenomenon is now dead; what remains
is literal, word-scoped copying (nulls, back-references, or composition
stutters).
