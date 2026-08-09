---
type: observation
---
# Characterization: The Seam Channel is Clean (Suppressed Diagonal Only)

## Claim

The 2,927 word seams — the bigram (last rune of word w, first rune of
word w+1) — carry **no structure at all**. The off-diagonal matrix,
repeated seam bigrams, the conditional distributions in both directions
and the marginals are all flat.

**Corrected, August 2026** (`experiments/negative_control_battery.py`).
This file previously claimed the seam carried "exactly one structure: the
suppressed diagonal (the 23 cross-word doublets, z = −8.1 against random
word pairing)". That z measures the **global** doublet suppression showing
through at the seam, not a seam property. The null used — permuting word
order — reassembles words freely and so destroys the doublet suppression
along with the seam pairing, sending the expectation to the unsuppressed
100.7.

Against a surrogate that **preserves** the observed doublet rate and every
boundary, the seam diagonal is 23 observed against 19.7 ± 4.6, **z = +0.72**.
There is nothing there.

This also resolves a contradiction between two files. `word-level-autokey.md`
already carried the correction that the suppression is boundary-blind — the
within-word rate 0.0063 and the seam rate 0.0079 are statistically one rate
(z = 0.87, pooled 0.0066) — while this file still headlined the seam
diagonal as a finding. The boundary-blind reading is the right one.

The diagonal suppression remains **independent of the previous word's length
class**, which still verifies the walk's seam-cancellation prediction; that
part is unaffected.

## Status

**Status**: confirmed (characterization)

## What was measured

Clean corpus (sections 0-9, 2,928 words). Null: 2,000 permutations of
word order — preserves every word-internal statistic and both seam
marginals, breaks only the seam pairing (`experiments/seam_bigram_tests.py`).

| statistic | observed | null | verdict |
|---|---|---|---|
| diagonal (seam doublets), word-order null | 23 | 100.7 ± 9.6 | ~~z = −8.1~~ — this null destroys the doublet suppression; see the correction above |
| diagonal (seam doublets), doublet-preserving null | 23 | 19.7 ± 4.6 | **z = +0.72** — nothing; the seam is as suppressed as everywhere else, no more |
| off-diagonal chi2 (840 df) | 828 | 810 ± 40 | flat (z = +0.5) |
| pair-distribution IoC (×841) | 1.027 | 0.999 ± 0.014 | +2.0σ, see note |
| max repeated seam bigram | 12 | 10.7 ± 1.0 | flat (z = +1.2) |
| mean nIoC of first-runes given last rune | 1.024 | 0.998 ± 0.014 | +1.9σ, see note |
| mean nIoC of last-runes given first rune | 1.030 | 1.001 ± 0.014 | +2.1σ, see note |
| max conditional-group nIoC (either direction) | 1.21-1.23 | 1.18 ± 0.06 | flat; an English-like leak would show ~1.7 |
| last-rune / first-rune marginals | chi2 31.5 / 23.8 (28 df) | — | uniform |

**The three ~2σ rows are an artifact, not a lean** (review
decomposition, section F/G of the script): the word-order permutation
null does not preserve the seam doublet suppression, so the observed
matrix packs the same 2,927 seams into effectively 812 cells instead of
841 — a mechanical +3.6% ceiling on any density statistic (observed
+2.8%), and each conditional group avoids one value (29/28 ≈ 1.036).
Isolating the components confirms it: off-diagonal-only pair IoC is at
its own baseline (obs 1.042 vs null 1.036 ± 0.014, z = +0.43), and the
deeper cross-seam conditionals are flat (first-rune given
second-to-last: z = +0.12; second rune given last: z = +0.30). This is
the FOURTH instance of the doublet-suppression trap (after bigram IoC,
trigram repeats, and isomorphs — see README): any density statistic on
this corpus must use a suppression-aware null. No group approaches the
~1.7 a keyed or leaking seam would show.

**Reach into the next word** (last rune of word w vs rune r of word
w+1). Walk prediction: a match at reach r requires
p_last = σ(g^(r−1)(p_r)) — a fixed permutation diagonal per reach, with
σ tuned rare only at r = 1 — so reaches 2-6 should sit at chance with no
conditional structure. Measured (word-permutation null):

| r | pairs | matches | rate | z | conditional split z |
|---|---|---|---|---|---|
| 1 | 2927 | 23 | 0.0079 | **−8.1** | (+1.9, the cell-packing artifact) |
| 2 | 2828 | 90 | 0.0318 | −0.7 | +0.4 |
| 3 | 2363 | 72 | 0.0305 | −1.0 | +0.4 |
| 4 | 1637 | 59 | 0.0360 | +0.4 | +0.3 |
| 5 | 1123 | 35 | 0.0312 | −0.6 | −0.5 |
| 6 | 805 | 26 | 0.0323 | −0.3 | −0.5 |

Chance at every reach past the seam, exactly as the cancellation
predicts; the suppression is confined to r = 1.

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
diagonal and nothing else — the apparent ~2σ density lean decomposes
entirely into the diagonal-deficit cell-packing artifact, and the
conditional structure is flat at depth 1 and depth 2 in both directions.
The suppression is length-class-independent exactly as the walk's seam
algebra requires. Negative for new attack surface, positive as a model
check.
