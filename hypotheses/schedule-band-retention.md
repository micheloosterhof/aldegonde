---
type: observation
---
# Observation: The Dodge Sweep's Rate Bands Are Cost-Neutral, and the d6 Band Rejects Seven True Keys in Ten

## Feature

`zero_offset_census.dodge_filter_full` bands three predicted rates — distance 1, 4
and 6 — before any key reaches the scorer, and `quagmire-dodge.md` prices its sweep
with all three applied. Over 2,000 planted keys of exactly that family, the three
bands together keep the true schedule **9.0%** of the time. The d6 band alone keeps
**27.7%**: its upper edge is 0.03454 against chance 0.03448, so it asks a true key to
predict a distance-6 rate at or below chance, and **72%** of true schedules predict
one above it.

The bands also buy nothing. Each one cuts the schedules to score and the probability
of keeping the key by the same factor, so the expected work per true key found is
flat across every combination:

| filter | schedules/alphabet | keys | core-h | keeps a true key | core-h per key found |
|---|---|---|---|---|---|
| no bands | 105,980 | 3.9e9 | 216 | 100.0% | 216 |
| d1 only | 50,246 | 1.8e9 | 102 | 47.5% | 215 |
| d1+d4 | 33,992 | 1.2e9 | 69 | 31.9% | 217 |
| d1+d4+d6 | 10,439 | 3.8e8 | 21 | 9.0% | 235 |

The tightest setting is the one the sweep was specified with. It is the only one that
is worse than doing nothing, and it converts a 216-core-hour certainty into a
21-core-hour lottery ticket at nine to one against.

## Status

**Status**: confirmed (measurement), n = 2,000 planted keys, binomial SE 0.6%.
`experiments/band_retention.py`. The retention numbers are for keys drawn from
`pure_quagmire_restart.schedule` and enciphered by `doublet_phase_test.encipher` onto
a register matched to the LP's word-length sequence, which is the family the sweep
searches for.

## Why the bands lose the key

Two separate defects, and only the second is about d6.

**The pipeline omits its own prediction error.** The bands are a 95% Wilson interval
on the *corpus's observed* rate, widened by `diluted_band` for the clock steps the
dodge inserts. They are then compared against a rate *predicted from register tables*.
Nothing in the interval accounts for the gap between the table's prediction and the
draw the key actually enciphered. Calibrating each band on the planted key's own
ciphertext — the sharpest form of the test, where the corpus and the band agree by
construction — still keeps all three only **53.2%** of the time, against the 95% a
correctly calibrated 95% interval would give. Per band, self-calibrated: d1 93.8%,
d4 74.8%, d6 77.5%. Only d1 is honest, and d1 is the band whose width is not diluted.

**The d6 band is built on 31 coincidences.** `distance-6-has-no-power.md` measures
the within-word d6 deficit at 31/1267, z = −1.95 — just enough power to see once, and
not enough to corroborate, since d11 holds 35 pairs and d16 none. The 95% Wilson
interval on that count is 0.01729 .. 0.03452, and chance is 0.03448: the upper edge
lands on chance to three decimal places. That edge is the raw interval's, not the
dilution's — `diluted_band` widens the lower side (0.01729 → 0.00956) and moves the
upper one by 2e-5. So the band encodes "d6 must be at or below chance" as a hard
constraint purely because a deficit of 31 is large enough to keep chance at the very
top of its interval. That is precisely the claim `distance-6-has-no-power.md` says the
data cannot support, and a true key whose schedule predicts d6 a hair above chance is
discarded for it.

The d1 band, by contrast, is honest: 63/10028 gives 0.00491 .. 0.00803, far below
chance, and it is the one band whose width is not diluted and whose self-calibrated
retention (93.8%) matches its nominal 95%.

## What it changes

The sweep runs with no bands: 3.9e9 keys, 216 core-hours, and the key is in the set by
construction. `experiments/dodge_priority_sweep.py` defaults to `BANDS = frozenset()`
for this reason, with the band set switchable so the measurement stays reproducible.

This is the third search in this project that could not have found what it was looking
for, and the three failures are independent:

- `dju-bei-gate-validity.md` — the gate was a necessary condition only under a reading
  of the repeat that is itself unlikely; it discarded a true key 99.94% of the time.
- `quagmire-dodge.md` — the scorer assumed clock = position, which the dodge violates,
  so a planted key scored below random.
- here — the generator's bands discard a true key 91% of the time.

Coverage, sensitivity and retention are three separate prerequisites. A sweep can
generate a key it cannot score, score a key it never generates, and filter away a key
it both generates and scores. `dodge_priority_sweep.py --selftest` checks all three on
a planted key before any core-hours are spent.

## Scripts

- `experiments/band_retention.py` — the retention measurement, both calibrations, and
  the cost table above.
- `experiments/dodge_priority_sweep.py` — the sweep, with the band set switchable and
  a self-test covering generation, retention and scoring.
- `experiments/zero_offset_census.py` — the counter the generator is checked against.

## Related

- `quagmire-dodge.md` — the hypothesis whose sweep this is.
- `distance-6-has-no-power.md` — why the d6 band has no evidence behind it.
- `dju-bei-gate-validity.md` — the same failure mode, a different filter.
