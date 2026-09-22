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

**Status**: unresolved, and **disfavoured by the doublet-gap signature on a narrower
basis than first published** (`experiments/doublet_gaps_conditioned.py`, September 2026).
The original 80:1 is **withdrawn** — it came from a pooled scoring that conditions on
nothing. Bucketed by gap size with the key phase marginalised, the within-block doublets
give log LR **−0.91**, which if anything favours the odometer, and the seam doublets give
**+3.41, about 30:1** against it. The verdict rests on the seam doublets alone.

This is not independent of the verdict on `quagmire-dodge.md` — it is the same evidence
reaching the same mechanism in both. What makes it serious is that neither model can
drop the zero offset: without it the preventer never fails and the corpus's doublets
could not exist at all.

Otherwise still the best-scoring model in this directory on the fitted-to-free ledger.
Untuned it lands 17 of 19 free cells.

The `d6w` failure recorded below is **much weaker than it was first written**. That
verdict came from `fingerprint_battery`, which scores a cell by where the LP falls in
the MODEL's spread and treats the corpus value as exact. The LP's within-word distance-6
rate is 31 coincidences in 1,267 pairs. Counting its error too, the gap is z = 1.65 to
2.29 rather than p = 0.000. See `distance-6-has-no-power.md`.

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

This is weaker than proof, for two reasons. The search is a hill-climb of 900 steps
with a crude neighbourhood, so it bounds what that search found rather than what the
family can do. And the target it was aiming at is itself uncertain: the corpus's 0.0245
carries a binomial error of +-0.0043, so the model's 0.0350 is between 1.65 and 2.29
standard errors away, not the p = 0.000 the battery printed.

The two runs do trade off against each other, which is what a real constraint between
the diagonals would look like, and `sigma_algebraic_floor.py` records the same kind of
floor for arithmetic families. But the cell being chased may not be a real relation at
all.

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
3. ~~Inherited: `walk_score_kernel` cannot score any model with the doublet
   preventer.~~ `experiments/dodge_aware_scorer.py` now can, separating a planted key
   by z = 12 to 20, and `dodge_score_kernel.c` runs it at 5,000 keys/s/core. This model
   is searchable for about 20 core-hours.

## What the sweep has to enumerate

The scorer leaves an unknown bijection on the ciphertext, which is what makes it
base₀-free. A natural hope is that this absorbs the odometer's dial STARTS, so the
sweep would only enumerate (alphabet, schedule). It does not.

| scored with | score |
|---|---|
| the true key | −3.078 |
| the true alphabet and schedule, 40 wrong dial starts | mean −3.572, best −3.532 |
| 40 fully wrong keys | mean −3.582, best −3.527 |

None of the 40 wrong-dial scores clears the wrong-key ceiling. A wrong dial start makes
the correct alphabet and schedule look exactly like noise.

**But only the INNER dial.** That first measurement drew random `(a₀, b₀)` PAIRS and
concluded about both, which was a scope error. Separating them:

| varied | score spread |
|---|---|
| the outer dial `b₀`, at any fixed inner dial | **0.000000** |
| the inner dial `a₀` | 0.0930 — true 1.0785, next best 0.6248 |

The outer dial shifts every ciphertext rune by the same amount, and a uniform shift is
itself a bijection, so the free assignment absorbs it exactly. It is not a key parameter
at all as far as the scorer is concerned.

The inner dial is. Changing `a₀` adds a constant to every running sum `S_k`, which
leaves the OFFSETS unchanged, so it is a different key with the same schedule and the
schedule enumeration does not cover it.

So the sweep carries a factor of 29, not 841.

Priority vocabulary: 1.3×10⁷ (alphabet, schedule) pairs × 29 = 3.8×10⁸ keys. The
compiled kernel does 5,000 keys/s/core, so that is **21 core-hours**, or 13 with the
two-stage 60% prefilter.

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
that was thought to require a general permutation.

The one cell it does not reach is `d6w`, and the case against it has since weakened
twice over. The hill-climb could not bring it down without breaking d2w and d5x, which
suggests a constraint between the diagonals. But the corpus's own distance-6 rate is 31
coincidences with an error bar of +-0.0043, the gap is 1.65 to 2.29 standard errors
rather than p = 0.000, and the rest of the 1-mod-5 family has no power to corroborate
it: distance 11 holds 35 within-word pairs and distance 16 holds none.

So the model has no established failure other than the DJU-BEI repeat, and chasing
`d6w` further means chasing a relation that may not exist.
