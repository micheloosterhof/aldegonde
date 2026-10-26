---
type: observation
---
# Observation: The Alphabet Set Does Not Persist Across Blocks — Not for Two, Not for Three, Not on a Trigger

## Question

Michel's question (October 2026): what if the five alphabets are not re-keyed at every
block but serve two or three consecutive blocks, or persist until some trigger switches
the series? The model on record assumes one set per block; this asks the ciphertext.

## The test

If blocks w and w+D share one alphabet set, they are enciphered identically position by
position under a clock that restarts at each block, so they coincide at matched positions
at the plaintext's word-aligned rate, 0.0794, instead of chance 0.0345. Runs of fixed
length k put blocks at distance D < k together with probability (k − D)/k; a switch fired
with probability q per block gives (1 − q)^D. The record's word-aligned test pooled all
13.5M block pairs (`lag5-digraph-is-inside-the-word.md`), which would dilute a short run a
thousandfold, so this reads the rate distance by distance.

`experiments/alphabet_sharing_by_word_distance.py`

## Result

Left-aligned (shared first position), about 9,000 matched positions per distance:

| D | rate | z vs chance | k = 2 predicts | k = 3 predicts |
|---|---|---|---|---|
| 1 | 0.0373 | +1.49 | 0.0569 | 0.0644 |
| 2 | 0.0344 | −0.06 | 0.0345 | 0.0495 |
| 3 | 0.0315 | −1.55 | 0.0345 | 0.0345 |
| 4–12 | 0.0339–0.0371 | −0.3 to +1.4 | chance | chance |
| 15 | 0.0406 | +3.14 | chance | chance |
| 20, 30, 50 | 0.0356, 0.0350, 0.0317 | +0.6, +0.2, −1.4 | chance | chance |

Adjacent blocks sit 8σ below the two-block prediction and further below three. The D = 1
reading of +1.49 is the same number `sigma-moves-almost-every-rune.md` records as 1.0685
(z = +1.48) and attributes to the step's fixed points. D = 15 at +3.14 is one cell of 32
scanned (two alignments × 16 distances) and clears nothing after correction. Right-aligned
(shared last position) is flat everywhere, D = 1 at −1.02.

Under a continuous clock the sharing would show instead as lag-k coincidence across exactly
one boundary: lag 5 reads 240 of 7,306 = 0.0328 (z −0.76), where two-block runs predict
0.047 (−5.7σ); lags 2–7 all sit within 1.4σ of chance; lag 1 is the doublet seam.

**A trigger model is bounded, not just a fixed k.** The D = 1 excess over chance is
0.0028 ± 0.0019, so the probability that a block keeps its predecessor's set is at most
(0.0028 + 2 × 0.0019) / 0.0449 ≈ 0.15 at two sigma. Whatever the switching rule, it fires at
at least 85% of boundaries, and the data are consistent with it firing at every one.

## Conclusion

The alphabet set changes at every block, or at nearly every block: no fixed run length
of two or more survives, and any trigger must switch at ≥ 85% of boundaries. The word
boundary is a hard cut of the alphabet, as `length-clocked-walk.md` states; this is the
measurement that supports it at short block distances, where the pooled test could not.

## Scripts

- `experiments/alphabet_sharing_by_word_distance.py`

## Related

- `sigma-moves-almost-every-rune.md` — the same D = 1 cell read as σ's fixed points.
- `lag5-digraph-is-inside-the-word.md` — the pooled word-aligned test this sharpens.
- `rotor-machine-compact-state.md`, `lengths-do-not-steer-the-key.md`,
  `dot-counts-do-not-drive-the-key.md` — public triggers tested by bucket coincidence.

## What the record says about how the per-block sets relate (October 2026)

The question behind the test above — one set per block, or related sets — has a model
answer and a measured one. The model assumes a relation (`base_{w+1} = base_w ∘ g^a ∘ σ`,
one σ conjugated by a g-power set by the block length), because a finite key needs one.
The measurements say the relation, whatever it is, is indistinguishable from fresh:

| question | result | file |
|---|---|---|
| any two blocks sharing an alphabet set at a detectable rate? | no: 13.5M block pairs at matched positions coincide at 0.0344, chance 0.0345 | `lag5-digraph-is-inside-the-word.md` |
| consecutive blocks sharing? | no: this file, adjacent 0.0373 against 0.0569 for two-block runs | — |
| how many effective alphabets? | ≥ 949 from the flat IoC; ≥ ~300 bases from the no-reuse depth | `flat-ioc.md`, `two-rune-depth-no-base-reuse.md` |
| the step a power of g (five alphabets in all)? | no: within-class IoC 0.999 where 1.6 is required | `key-local-channel-is-empty.md` §6 |
| the re-basing a shift or affine map? | no: χ² 89.7 against 620–1,252 for planted affine | `base-is-not-affine.md` |
| the group the bases live in? | A₂₉ or S₂₉ | `base-family-is-the-symmetric-group.md` |
| the same relation in every block? | disfavoured at e¹⁰ (C9) | `within-word-relation-is-position-flat.md` |
| any positive sign of relatedness? | one candidate base return, DJU-BEI (chance 0.00037) | `dju-bei-*.md` |

Every small family is excluded, and the surviving one — related by a generic permutation
step — is observationally identical to new. The reason is structural: a cross-block pair
exposes `g^{-j} · S · g^{j'}` with S a long product, a generic permutation's diagonal is
about one fixed point in 29, so cross-block equality sits at 1/29 whether or not the
blocks are related (`key-construction-is-unmeasurable.md`). Relatedness is reachable only
key-globally: a crib propagated through base₀, or a structured enumeration of (g, σ).
