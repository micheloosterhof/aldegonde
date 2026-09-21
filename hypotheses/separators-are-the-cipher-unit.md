---
type: observation
---
# Observation: The d5 Echo Is Anchored to the Visible Separators, So They Are the Cipher's Units

## The awkward possibility this closes

`separators-are-not-word-boundaries.md` finds the body's block lengths carry a tenth of
the serial structure language has, depend on nothing measurable, and cannot be produced
from English words by merging, nulls or padding. That raises a question the file does not
answer: if the separators do not delimit words, are they cipher structure at all, or just
marks the analysis has been over-reading?

They are cipher structure. The d5 echo — positions five apart inside a block coinciding
above chance, which is the whole evidence for a letter step of order 5 — is anchored to
exactly these positions.

## The test

Slide **every** boundary by the same number of runes, keeping the length sequence
unchanged, so the block structure is identical in shape and only its phase moves. Then
re-measure the within-block coincidence at lag 5.

| shift | hits / pairs | × chance | z vs chance |
|---|---|---|---|
| **0 (the real separators)** | **102 / 2,073** | **1.427** | **+3.67** |
| 1 | 98 / 2,073 | 1.371 | +3.19 |
| 2 | 89 / 2,073 | 1.245 | +2.11 |
| 3 | 78 / 2,073 | 1.091 | +0.78 |
| 4 | 60 / 2,073 | 0.839 | −1.38 |
| 5–15 | — | 0.81 to 1.15 | — |

Shifts 4 and beyond: mean **0.998**, sd 0.103 over twelve offsets. The real separators
sit **+4.17σ** above that empirical null.

**How to read the small shifts.** Moving every boundary by one rune leaves most *pairs*
inside the block they were already in, so shifts 1–3 are not independent draws — the
smooth decay is their pair sets decorrelating from shift 0's, not a signal. Only shifts
4+ are a null, and that is the comparison quoted.

## What it settles

The scribe's separators are where the cipher's alphabet phase resets. That is a stronger
statement than "the key state is word-anchored", which was measured by comparing within
to across boundaries (`rotor_word_scope.py`, z = +3.22 against a boundary-blind null):
this shows the effect is specific to *these* boundary positions and not to boundaries of
that shape anywhere.

So the two findings sit together without contradiction:

- the separators **are** the cipher's units — the phase is anchored to them;
- their **lengths** carry no language order and depend on nothing measurable.

Which is to say the author's segmentation is real and deliberate, and is not the
plaintext's word segmentation. That is the block reading, now with the first direct
evidence for the first half of it rather than only the second.

## The same null, applied to every lag, separates two things the project had conflated

The boundary shift is a null for any within-block statistic, not just lag 5. Running it
across lags 1 to 8 isolates what is *anchored to the separators* from what is merely true
of the text:

| lag | × chance | shifted null | z |
|---|---|---|---|
| 1 | 0.182 | 0.193 ± 0.011 | −1.02 |
| 2 | 1.007 | 0.967 ± 0.037 | +1.07 |
| 3 | 1.074 | 0.994 ± 0.072 | +1.10 |
| **4** | 1.188 | 1.032 ± 0.071 | **+2.21** |
| **5** | 1.427 | 1.042 ± 0.100 | **+3.83** |
| **6** | 0.710 | 0.955 ± 0.104 | **−2.36** |
| 7 | 1.220 | 0.937 ± 0.199 | +1.43 |
| 8 | 0.777 | 1.008 ± 0.253 | −0.91 |

Adjacent lags share runes, so the z values are not independent. The permutation test that
handles this treats each shifted offset as a pseudo-replicate and recomputes the same
concentration statistic:

| | observed | shifted median | shifted max | p |
|---|---|---|---|---|
| Σz² over lags 4, 5, 6 | **25.10** | 2.53 | 11.13 | **0.037** |
| Σz² over lags 1, 2, 3, 7, 8 | 6.27 | 5.30 | 16.74 | 0.444 |

No offset reaches the observed concentration, and the observed value is 2.3× the largest
of 26 nulls — so p ≤ 0.037 is a bound set by the number of offsets, not an estimate.

**The structure sits exactly where a letter step of order 5 puts it.** Lag 5 repeats the
alphabet; lags 4 and 6 sit on g's two diagonals, and they move in opposite directions,
which is what a tuned diagonal predicts and what `d4-d6` has recorded as one g's
signature. Lags 2, 3, 7 and 8 carry nothing anchored.

**And lag 1 is not anchored at all.** The shifted null reproduces the doublet deficit
almost exactly — 0.193 against the observed 0.182, z = −1.02. Sliding every block
boundary does not change the doublet rate. So the doublet suppression is a property of
the **emitted stream**, not of the block's alphabet schedule, and any model that derives
it from the per-block schedule is wrong. `doublet-deficit-is-global` asserted this from
the within/across split; this is the sharper test, holding the block shape fixed.

## Scope

- The echo itself is a ~3.7σ effect and this file inherits that; it shows the effect is
  *located* at the separators, not that it is larger than previously measured.
- Only lag 5 is tested here, because it is the only lag with a key-free reading.
- The length sequence is held fixed, so this varies phase, not segmentation shape. A
  differently-shaped segmentation is not covered.

## Status

**Status**: confirmed (measurement), 102/2,073 pairs at shift 0 against an empirical null
of 0.998 ± 0.103 from twelve decorrelated offsets. `experiments/boundary_phase_shift.py`.

## Related

- `separators-are-not-word-boundaries.md` — the other half of the picture.
- `within-word-d5-coincidence.md`, `d5-partial-alphabet-leak.md` — the echo itself.
- `rotor-machine-compact-state.md` — the boundary-blind null this sharpens.
