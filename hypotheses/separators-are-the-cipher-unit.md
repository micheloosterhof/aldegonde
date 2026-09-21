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
