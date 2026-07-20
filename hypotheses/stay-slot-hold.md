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

**Status**: plausible (strengthens the model by removing fitted parameters;
reproduces the profile shape without tuning; exact magnitudes approximate)

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

- **The number matches, parameter-free.** Real runeglish plaintext (128k words,
  prose) has within-word doublet rate 0.0346, so `(1/5)·0.0346 = 0.0069` — LP
  observed 0.0063 (within ~10%), with no tuned diagonal.
- **Boundary-blindness is derived, not tuned.** Plaintext doublet rate is nearly
  the same within words (0.0346) and across word boundaries (0.0327) — both
  ~chance — so `plaintext/5` is nearly equal at both, giving within ≈ seam for
  free. The "tuned coincidence" flagged in the model audit dissolves.
- **The g4 powers behave as required.** g4¹ minimized (IoC 0.04); g4²/g4³
  uncontrolled (~chance); g4⁴ = identity (the echo). The d1-d5 staircase falls
  out of these plus the hold.
- **Simulation, no rate fitting.** Stay-slot with the advance *minimized* (not
  fit): d1w 0.0080, d1seam 0.0127, d2/d3/d4 ~chance, d5 echo — the right shape.
- **Bonus.** The stay-slot reproduces the d1-delta residual (χ²=39.3 vs LP 41.4)
  that the order-5-g model did not naturally hit.

## Evidence against / open

- **Magnitudes run slightly high.** Sim d1w ~0.008 vs LP 0.0063; sim seam
  ~0.013 vs LP 0.0079. The pure-hold floor is `(1/5)·0.0346 = 0.0069`, and LP
  within (0.0063) is marginally *below* it — since the advance can only add,
  matching 0.0063 needs the real LP plaintext doublet rate a touch below chance
  (real English doublets are ~2-3%, below chance; the proxy came out at chance,
  possibly a digraph-merge artifact) or the hold slightly off a clean 1/5.
- **The seam is only partly inherent here.** The within-word profile is
  cleanly hold-driven, but in the simulated walk the *seam* still passes through
  the per-word base step. LP seam (0.0079) is close to `(1/5)·plaintext-seam
  (0.0065)` but a little higher, suggesting the seam is *mostly* a hold-exposure
  with a small extra contribution — not fully pinned.
- **d2/d3/d4 exact values depend on the arbitrary powers** `g4²`,`g4³` of the
  specific advance; they land near chance but vary run to run.
- **Not distinguished from order-5-g by the ciphertext.** "advance-4-hold-1
  (g4⁴=id)" and "advance-5 (g⁵=id)" both give the d5 echo and pass the battery;
  the hold version is *preferred* only because it makes the doublet inherent.

## Predictions

- The within-word doublet rate should track (real LP plaintext doublet rate)/5;
  a decryption would let this be checked exactly.
- The d1-d5 profile shape should be reproduced by any correct model with only
  the adjacent step controlled — no separate tuning at d2/d3/d4.

## Scripts

- `experiments/stay_slot_cipher.py` — V2 STAY-SLOT (order-4 advance minimized,
  1-in-5 hold) with the full battery; V1 is the order-5-g counterpart.

## Related

- `length-clocked-walk.md` — the overall model; this note replaces its
  "tuned g-diagonal" account of the doublet with an inherent hold mechanism.
- `d5-partial-alphabet-leak.md`, `within-word-d5-coincidence.md` — the d5 echo
  the hold also produces.
- `explicit-doublet-avoidance.md`, `doublet-spacing-poisson.md` — earlier
  doublet notes; this is the "inherent, not bolted-on" resolution.

## Verdict

The doublet suppression and the whole within-word d1-d5 profile are inherent:
they come from one minimized advance permutation `g4` + the period-5 hold + the
plaintext's own coincidence structure, not from tuned diagonals. This unifies
the doublet suppression with the d5 echo (both are the hold) and derives the
boundary-blindness from the language, directly fixing the "tuned diagonal" weak
point of the model. The mechanism is right; the exact magnitudes are
approximate and want a real-LP-plaintext doublet rate we do not have, and the
seam is only partly pinned. The hold and order-5-g formulations are not
distinguished by the ciphertext — the hold is preferred for having zero fitted
rates.
