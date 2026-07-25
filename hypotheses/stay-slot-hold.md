---
type: hypothesis
---
# The Doublet Suppression is Inherent: the 1-in-5 Hold, not a Tuned Diagonal

## Claim

The within-word doublet suppression (0.0063) and the entire within-word d1-d5
coincidence profile are **not tuned parameters** — they fall out of a single
mechanism that is the *same structure* producing the d5 echo. Instead of an
order-5 permutation `g` advancing on every letter (whose diagonal must be tuned
to 0.0063), the alphabet advances by a **rich order-4 permutation `g4` on 4 of
every 5 letters and HOLDS once per 5** (net advance over 5 = `g4⁴ = id`, which
gives the d5 echo). On the hold step the two adjacent runes share the alphabet,
so a ciphertext doublet occurs **exactly when the plaintext has a doublet**.
Therefore

```
within-word doublet rate ≈ (1/5)·(plaintext doublet rate)  +  (4/5)·(advance diagonal)
```

The first term is set by the **language**, not fitted. The advance step `g4` is
only *minimized* (a "make it doublet-avoiding" criterion, not a fit to a
value). So the doublet rate is **inherent**, and the whole staircase (d1
suppressed, d2/d3 ~chance, d4 slightly up, d5 echo) comes from *one* minimized
permutation plus the period-5 hold.

This replaces the two tuned diagonals (`g`-diagonal for within, `σ`-diagonal
for the seam) that the order-5-g model needed. See `length-clocked-walk.md`.

## Status

**Status**: disproved (doublet position-profile test, July 2026 — the
doublets are not plaintext double letters; see Evidence against)

## Mechanism

The advance counter `e` increments on 4 of every 5 positions and holds once
(at a per-word keyed slot `r_w`). Alphabet at position `j` = `base_w ∘ g4^(e_j)`.
Two positions `d` apart differ by `g4^(d − holds-in-window)`:

- **d1**: `g4¹` (minimized) most steps, or same alphabet on the hold (plaintext
  doublet) → **suppressed**.
- **d2 / d3**: `g4²` / `g4³` (mixed with an occasional hold). These powers are
  **not** minimized — only `g4` is — so they sit at **~chance**.
- **d4**: in a 4-window with **no hold** (1/5 of the time) the net step is
  `g4⁴ = id`, so those pairs get a **partial echo** (plaintext d4 coincidence
  leaks); the rest are `g4³ ~ chance`. Result: slightly *above* chance.
- **d5**: a 5-window **always** contains exactly one hold → net `g4⁴ = id` →
  same alphabet → **full echo**.

So the rising profile is not three separate facts; it is the increasing
"return-to-identity" contribution as `d` approaches the period, with only the
adjacent step controlled.

## Evidence for

- **The number matches, parameter-free.** The real runeglish bigram corpus
  (mortlach, 6.7e9 bigrams) has a plaintext doublet rate of **0.0323** (its
  diagonal / total), so `(1/5)·0.0323 = 0.0065` — LP observed **0.0063**,
  within 3%, with no tuned diagonal. (An earlier prose proxy gave 0.0346 →
  0.0069; the corpus figure is tighter.) `experiments/advance_doublet_floor.py`.
- **A doublet-free advance provably exists — so the doublets can't come from it.**
  Minimizing the advance diagonal (an assignment problem over permutations) hits
  **0.0013** unconstrained, and **~0.0023** even when constrained to the
  model's cycle types (five 5-cycles for order-5, seven 4-cycles for order-4).
  All far below observed 0.0063, so the advance can carry ~zero doublets and the
  hold is left as the source. Two constructions give the doublet-free advance:
  routing the diagonal through rare bigrams (floors at 0.0013 because this
  corpus has no truly-forbidden bigrams), or a size-mismatched disk (in/out
  rings that can't collide) for a *structural* exact zero.
- **Boundary-blindness is derived, not tuned.** On the prose proxy (the only
  baseline here with a word-boundary split; the tighter mortlach figure above
  has no seam decomposition), the plaintext doublet rate is nearly the same
  within words (0.0346) and across word boundaries (0.0327) — both
  ~chance — so `plaintext/5` is nearly equal at both, giving within ≈ seam for
  free. The "tuned coincidence" flagged in the model audit dissolves.
- **The g4 powers behave as required.** g4¹ minimized (IoC 0.04); g4²/g4³
  uncontrolled (~chance); g4⁴ = identity (the echo). The d1-d5 staircase falls
  out of these plus the hold.
- **Simulation, no rate fitting.** Stay-slot with the advance *minimized* (not
  fit): d1w 0.0080, d1seam 0.0127, d2/d3/d4 ~chance, d5 echo — the right shape.
- **Bonus.** The stay-slot reproduces the d1-delta residual (χ²=39.3 vs LP 41.4)
  that the order-5-g model did not naturally hit.

## Doublet placement: no fixed hold, hold must be keyed

If the hold sat at a fixed word position, within-word doublets (which can only
appear on a hold step) would pile up at that word-phase. They don't:
`experiments/doublet_placement.py` finds the doublet RATE flat on every periodic
axis — position-in-word mod 5 (p=0.63), distance-from-word-end mod 5 (p=0.98),
absolute position mod 5 (p=0.42), word index mod 5 (p=0.27) — and flat by word
length. Doublet gap-mod-5 is flat too, and the min-gap-6 (no two doublets within
5) is **not** significant: random placement on the eligible positions gives 0
close gaps 22% of the time (word structure + 63 events), so it is not a repulsion
mechanism.

Consequences: a **fixed hold slot is refuted**; if the model is stay-slot the
hold is **keyed** (moves per word by a keystream), which is exactly what
reversibility requires. But placement does **not** discriminate g4-hold from
order-5-g: a keyed hold and a position-independent g-diagonal both give
featureless placement, and 63 doublets carry no handle. Placement is exhausted.

## Evidence against / open

- **THE KILL — the doublet position profile (July 2026,
  `experiments/doublet_position_profile.py`).** On the hold step a
  ciphertext doublet occurs exactly when the plaintext doubles, so the
  within-word doublets must inherit the plaintext double-letter
  position-in-word profile — and that profile is extreme: double letters
  almost never open a word (prose runeglish: start share 0.3%, rate 0.04%;
  the author's own solved register: 0 of 503 start adjacencies). A keyed
  hold does not rescue this — uniform thinning preserves the profile. The
  (This tests the PURE-hold reading, in which essentially all doublets
  are hold-derived — which is what the parameter-free rate match
  requires. A hold-plus-tuned-advance hybrid would predict an
  intermediate profile and is not excluded here, but it forfeits that
  rate match, the hypothesis's whole motivation.)
  LP doublets instead sit flat on the adjacency baseline: start 11 /
  middle 33 / end 18 / whole-word 1, G = 3.6 (p = 0.30) against flat,
  G = 83 (p < 1e-17) against the prose double profile, G = inf against
  the solved register (11 events in its zero-probability start cell). The
  hold cannot be the doublet source. Note the irony: the parameter-free
  rate match (0.0323/5 = 0.0065 vs 0.0063) was this file's headline — the
  rate matches but the events are the wrong ones.
- **Magnitudes run slightly high in simulation.** Sim d1w ~0.008 vs LP 0.0063;
  sim seam ~0.013 vs LP 0.0079. The pure-hold floor from the real bigram corpus
  is `(1/5)·0.0323 = 0.0065`, and LP within (0.0063) sits just *below* it —
  a near-exact match (the earlier 0.0346 proxy overstated the gap). Since the
  advance can only add on top of the hold, hitting 0.0063 needs the LP
  plaintext's own doublet rate at/just-below 0.0323 (plausible) or the hold a
  hair off a clean 1/5. The simulation's overshoot is from a non-minimized
  advance in that run, not the floor.
- **The seam is only partly inherent here.** The within-word profile is
  cleanly hold-driven, but in the simulated walk the *seam* still passes through
  the per-word base step. LP seam (0.0079) is close to `(1/5)·plaintext-seam
  (0.0065)` but a little higher, suggesting the seam is *mostly* a hold-exposure
  with a small extra contribution — not fully pinned.
- **d2/d3/d4 exact values depend on the arbitrary powers** `g4²`,`g4³` of the
  specific advance; they land near chance but vary run to run.
- **Not distinguished from order-5-g by the doublet rate.** "advance-4-hold-1
  (g4⁴=id)" and "advance-5 (g⁵=id)" both give the d5 echo and pass the battery.
  A tested-and-**retracted** discriminator: the order-5 grid diagonal at first
  appeared floored at ~0.02 (would have refuted the pure grid, since its diagonal
  IS the whole doublet rate with no hold), but that was a pure-descent local
  minimum — proper annealing drives the five-5-cycle diagonal to **0.0023**, so
  the grid can hit 0.0063 too. The hold version is *preferred* only on parsimony:
  it predicts 0.0063 for free (= plaintext-doublet/5), whereas the pure grid must
  *select* a diagonal at 0.0063 out of its achievable [0.0023, 0.15] range.

## Predictions

- The within-word doublet rate should track (real LP plaintext doublet rate)/5;
  a decryption would let this be checked exactly.
- The d1-d5 profile shape should be reproduced by any correct model with only
  the adjacent step controlled — no separate tuning at d2/d3/d4.

## Scripts

- `experiments/stay_slot_cipher.py` — V2 STAY-SLOT (order-4 advance minimized,
  1-in-5 hold) with the full battery; V1 is the order-5-g counterpart.
- `experiments/advance_doublet_floor.py` — the assignment-problem floor for the
  advance diagonal (0.0013 unconstrained, ~0.0023 by cycle type) and the
  parameter-free hold prediction 0.0323/5 = 0.0065 vs LP 0.0063.

## Related

- `length-clocked-walk.md` — the overall model; this note replaces its
  "tuned g-diagonal" account of the doublet with an inherent hold mechanism.
- `d5-partial-alphabet-leak.md`, `within-word-d5-coincidence.md` — the d5 echo
  the hold also produces.
- `explicit-doublet-avoidance.md`, `doublet-spacing-poisson.md` — earlier
  doublet notes; this is the "inherent, not bolted-on" resolution.

## Verdict

Disproved. The hold formulation's defining consequence — within-word
doublets ARE plaintext double letters — fails the position-profile test:
plaintext doubles are start-forbidden and end-heavy in every measured
register, while the LP doublets are positionally flat (11 word-initial
events where the register predicts ~0). The parameter-free rate match
(plaintext/5 ≈ 0.0065 vs 0.0063) was a genuine coincidence of magnitudes,
not of mechanisms. What survives in the walk family is the formulation
this file tried to replace: a TUNED rare-diagonal order-5 `g`
(`length-clocked-walk.md`), whose exposed bigram class {(g(y), y)} is not
doubles and must now satisfy a new constraint — its positional profile in
plaintext must be approximately baseline-flat, since that is what the
doublets show. The profile test thereby also becomes a key-space filter
on candidate `g` diagonals. (Output-avoidance / key-event readings of the
doublets predict the flat profile natively.)
