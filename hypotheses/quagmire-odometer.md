---
type: hypothesis
---
# Hypothesis: A Quagmire on an Odometer, with No General Permutation

## Claim

The cipher `pure-quagmire-word-restart.md` points at, once the fixed restart is removed
from Michel's proposal. Every operation is a shift; there is no general permutation in
the key.

```
c_j = ( K[ (pos_K(p_j) + a_w + S[clock mod 5]) mod 29 ] + b_w ) mod 29
```

`K` is one keyed alphabet, `S` the running sums of a five-step schedule holding exactly
one zero offset, and the doublet preventer advances the clock on a repeat. The clock
runs **on** through the word break. `a_w` shifts inside `K` and `b_w` outside it; they
do not commute, so the per-word step ranges over 29 × 29 = 841 permutations. They are
driven as an odometer — `a` every word, `b` only when `a` wraps.

## Status

**Status**: unresolved, and the best-scoring model in this directory on the
fitted-to-free ledger. Untuned it lands 17 of 19 free cells. Its systematic failure is
`d6w`, which this model could not reach even with the search aimed at it.

## Why each piece is forced

- **The carry.** Two dials each advancing at a fixed rate stay on a line and deliver 29
  states between them, not 841. Measured: both dials advancing every word give 125
  identical ciphertext words; the carry gives 19, against the corpus's 17. All 841
  states are visited in 2,928 words.
- **The running clock.** A fixed restart puts every word boundary on one clock phase, so
  the preventer fails at all of them or none. Over 12 draws the seam-to-doublet ratio
  came out 0.0 six times and 7.4 to 54.0 six times; the corpus reads 1.25. See
  `pure-quagmire-word-restart.md`.
- **The single zero offset.** The only way the preventer can fail, which fixes the
  doublet rate at (1/5) × a diagonal. See `quagmire-dodge.md`.

## Evidence for: 17 of 19 free cells, nothing fitted

`K`, the schedule and both dial starts drawn at random, scored on 40 draws of a register
carrying the LP's own word lengths:

| cell | LP | model | tail |
|---|---|---|---|
| seam | 0.0079 | 0.0078 | 0.967 |
| d1w | 0.0063 | 0.0071 | 0.900 |
| ioc | 0.9999 | 0.9999 | 1.000 |
| identical | 17 | 13.6 | 0.450 |
| d2w, d3w, d4w, d5w, d5x | — | — | 0.40–1.00 |
| entropy, triplets, bigram_chi2, kappa, doublet pos/gap, long, clock | — | — | all land |
| **d6w** | **0.0245** | **0.0387** | **0.000** |
| **returns** | **1** | **0.025** | **0.050** |

The seam is the cell that disproved the restart, and the running clock reproduces it
untuned at 0.0079 against 0.0078.

For comparison, `length-clocked-walk.md` fits six cells and leaves 13 free with one
miss; `quagmire-dodge.md` fits five and leaves 14. This fits **none** and leaves 19.

## Evidence against: d6w does not come down

Fitting the profile by hill-climbing `K` and the schedule, then re-scoring on 40 fresh
register draws:

| fitted | d6w reached | other outcome |
|---|---|---|
| d1w, d6w | 0.0323 (from 0.0387) | d2w and d5x pushed out to p = 0.050 |
| d1w, d2w, d3w, d5x, d6w | 0.0350 | d1w, d2w, d3w, d5x all land; **d6w misses at p = 0.000 while being fitted** |

So `d6w` moves only when the other diagonals give way, and with them held it goes back
where it started. The corpus needs 0.0245 and the model sits at 0.0350.

This is weaker than proof. The search is a hill-climb of 900 steps with a crude
neighbourhood, so it bounds what that search found rather than what the family can do.
But the two runs trade off against each other, which is what a real constraint between
the diagonals would look like, and `sigma_algebraic_floor.py` records the same kind of
floor for arithmetic families.

`quagmire-dodge.md` reports d6 as reachable at 0.0083, but that model has a general
permutation σ in the per-word step. The difference between the two is the thing this
hypothesis removes, so the discrepancy is evidence that the shift-only step is what
cannot reach d6.

## A reporting bug worth recording

The first full-profile run printed "misses: returns" while `d6w` sat at p = 0.000,
because the miss flag was only applied to FREE cells. A fitted cell that misses is the
more serious result — the search could not reach the corpus even while aiming at it —
and it was invisible. Fixed; both are flagged now.

## What to do next

1. **Settle d6w properly.** Replace the hill-climb with the analytic treatment: under a
   period-5 schedule 6 ≡ 1 mod 5, so d6 is a shift diagonal of the distance-6 plaintext
   table and its reachable range can be computed rather than searched. That decides
   whether the shift-only step is genuinely floored.
2. **If it is floored, the per-word step needs more than two shift dials.** The state
   budget in `pure-quagmire-word-restart.md` is met by 841, but d6 may need structure
   that shifts cannot supply, which would restore part of σ.
3. Inherited: `walk_score_kernel` cannot score any model with the doublet preventer, so
   none of this family can be searched for yet. See `quagmire-dodge.md`.

## Scripts

- `experiments/quagmire_odometer.py` — the cipher, the carry-versus-lockstep control,
  the fixed-restart control, the untuned battery score, the matched-register re-score
  and the profile fit.
- `experiments/pure_quagmire_restart.py` — where the restart was disproved and the
  state budget measured.

## Related

- `pure-quagmire-word-restart.md` — Michel's proposal, whose restart this drops and
  whose state budget this meets.
- `quagmire-dodge.md` — the same preventer with a general permutation per word; reaches
  d6 where this does not.
- `length-clocked-walk.md` — the incumbent, which fits six cells to this one's none.

## Verdict

Unresolved. On the fitted-to-free ledger it is the strongest model here: 17 of 19 cells
land with nothing tuned, including the seam that killed the restart and the flat IoC
that was thought to require a general permutation. Its failure is `d6w`, which did not
come down under a search aimed at it and which the σ-bearing sibling does reach. Whether
that is a floor of the shift-only step or a weak hill-climb is the next thing to settle,
and it is an algebra question rather than a search.
