---
type: observation
---
# Characterization: The Seam Channel is Clean (Suppressed Diagonal Only)

## Claim

The 2,927 word seams — the bigram (last rune of word w, first rune of
word w+1) — carry exactly one structure: the suppressed diagonal (the 23
cross-word doublets, z = −8.1 against random word pairing). Everything
else is flat: the off-diagonal matrix, repeated seam bigrams, the
conditional distributions in both directions, and the marginals. The
diagonal suppression is **independent of the previous word's length
class**, verifying the walk's seam-cancellation prediction.

## Status

**Status**: confirmed (characterization)

## What was measured

Clean corpus (sections 0-9, 2,928 words). Null: 2,000 permutations of
word order — preserves every word-internal statistic and both seam
marginals, breaks only the seam pairing (`experiments/seam_bigram_tests.py`).

| statistic | observed | null | verdict |
|---|---|---|---|
| diagonal (seam doublets) | 23 | 100.7 ± 9.6 | **z = −8.1** — the seam suppression against the honest null |
| off-diagonal chi2 (840 df) | 828 | 810 ± 40 | flat (z = +0.5) |
| pair-distribution IoC (×841) | 1.027 | 0.999 ± 0.014 | +2.0σ, see note |
| max repeated seam bigram | 12 | 10.7 ± 1.0 | flat (z = +1.2) |
| mean nIoC of first-runes given last rune | 1.024 | 0.998 ± 0.014 | +1.9σ, see note |
| mean nIoC of last-runes given first rune | 1.030 | 1.001 ± 0.014 | +2.1σ, see note |
| max conditional-group nIoC (either direction) | 1.21-1.23 | 1.18 ± 0.06 | flat; an English-like leak would show ~1.7 |
| last-rune / first-rune marginals | chi2 31.5 / 23.8 (28 df) | — | uniform |

Note on the three ~2σ rows: they are one signal, not three — the pair
IoC and the two conditional-split means all measure the same slight
clumpiness of the seam matrix, and at p ≈ 0.02-0.03 inside an
eight-statistic battery it is noise-compatible. No group approaches the
~1.7 a keyed or leaking seam would show.

**Length-class independence of the diagonal** (the walk's prediction):
under the walk the boundary factors cancel, so a seam doublet occurs iff
p_last = σ(p_first) — no dependence on the previous word's length. Rates
by (L−1) mod 5: 0.0079 / 0.0100 / 0.0056 / 0.0051 / 0.0136, all within
|z| ≤ 1.24 of the pooled 0.0079. Verified flat.

## Consequences

- The seam carries no exploitable channel beyond the σ-diagonal: no
  conditional structure links a word's last rune to the next word's
  first rune. Word-boundary-keyed mechanisms that would leak here
  (boundary autokey, seam-conditioned keys) get nothing to work with —
  consistent with their standing disproofs.
- The length-independence of the seam doublet rate is a positive,
  pre-derived check of the walk's seam algebra
  (`sigma-power-step.md`: the g^((L−1) mod 5) factor cancels).
- The 23 seam doublets remain the only σ-diagonal data
  (p_last = σ(p_first) at each); this census confirms nothing else about
  σ is visible at the seam.

## Scripts

- `experiments/seam_bigram_tests.py` — reproduces every number above.

## Related

- `sigma-power-step.md` — the seam-cancellation derivation this verifies.
- `doublet-suppression.md`, `stream-cipher-no-repeat.md` — the diagonal.
- `bigram-ioc.md` — the all-adjacency counterpart (off-diagonal uniform).
- `word-boundary-reset-autokey.md`, `word-level-autokey.md` — boundary
  mechanisms with nothing to feed on here.

## Verdict

Confirmed characterization. The seam channel contains the suppressed
diagonal and nothing else; the suppression is length-class-independent
exactly as the walk's seam algebra requires. Negative for new attack
surface, positive as a model check.
