---
type: observation
---
# Observation: The Distance-6 Deficit Is 31 Coincidences

## What was measured

Michel's question (September 2026): is the distance-6 dip a simple consequence of the
doublet rule, or is there further action at a distance — at 6, at 11? And is there
enough data to tell?

The answer to the last part decides the rest. There is not.

## The 1-mod-5 family

Under a period-5 schedule the distances congruent to 1 mod 5 all carry the same shift
relation, so a designed diagonal at distance 1 acts at 6, 11 and 16 as well. That is the
sharpest form of the question. Within words:

| distance | hits / pairs | z vs chance | z a real deficit would give |
|---|---|---|---|
| 1 | 63 / 10,028 | **−15.48** | −5.48 |
| 6 | 31 / 1,267 | −1.95 | −1.95 |
| 11 | 1 / 35 | −0.19 | −0.32 |
| 16 | 0 / 0 | — | — |

The last column is the power check. At 1,267 pairs a deficit the size of the observed
one reads z = −1.95, so distance 6 has exactly enough data to see the effect once, with
no margin. At 35 pairs distance 11 could not show a real effect at all, and distance 16
has no pairs. Pooling the family without distance 1 gives 32 / 1,302, z = −1.96, which
is distance 6 restated.

So the family cannot be tested past distance 6, and distance 6 sits at its own
detection threshold.

## Within words against across words

| distance | within words | across words |
|---|---|---|
| 1 | 63 / 10,028, z = −15.48 | 23 / 2,927, z = **−7.89** |
| 6 | 31 / 1,267, z = −1.95 | 424 / 11,683, z = +1.07 |
| 11 | 1 / 35, z = −0.19 | 385 / 12,910, z = −2.90 |

The doublet suppression is unmistakable at distance 1 in both, which is the seam and the
within-word rate being the same event. Distance 6 across words sits at chance, as every
model with a per-word step predicts, so whatever distance 6 does is confined to within
words where the alphabet relation survives.

Cross-word distance 11 is the largest departure apart from distance 1, but it is the
maximum of 20 scanned distances, where chance alone gives about 2.45. **Splitting the
corpus cannot judge it**: z scales as the square root of the pair count, so a pooled
−2.90 puts each half at −2.05 whether the cause is a relation or one fluctuation. The
halves read −2.03 and −2.05, which is that arithmetic and not evidence. Recorded as a
negative control on the method.

## What this does to the battery

`fingerprint_battery.compare` scores a cell by where the LP's value falls in the spread
of the MODEL over prose draws. It treats the corpus value as exact. It is not: distance
6 is 31 coincidences, `identical` is 17 word pairs, `returns` is one event.

Re-tested against the combined spread, `sqrt(model_sd² + LP_sd²)`, on the odometer
model:

| cell | z on model spread | z with the LP's error | |
|---|---|---|---|
| d6w | 3.12 | **2.29** | still a miss, marginally |
| d1w | 2.33 | 1.72 | was a miss, lands |
| d3w | −2.99 | −1.88 | was a miss, lands |
| returns | — | −1.00 | LP is 1 ± 1 |
| identical | −0.78 | −0.54 | lands |

`quagmire-odometer.md` recorded `d6w` as failing at p = 0.000. The honest figure is
between 1.65 and 2.29 standard errors depending on the key.

**A method error worth recording.** The first version of this estimated the LP's error
with a moving-block bootstrap for every cell. That is wrong for the repeat counters:
blocks are resampled with replacement, a duplicated block matches itself, and the repeat
statistics explode. It put a spread of 179.6 on `returns`, whose LP value is 1, 176.8 on
`identical` and 119.1 on `long`. Rates now use their binomial error, counts their
Poisson error, and cells with no sound estimate are reported as having none.

## Conclusion

The doublet suppression acts at distance 1, within words and across the word seam, and
both are overwhelming. No action at distance 6 or 11 is established. Distance 6 is a
−1.95 dip with exactly enough power to see itself, distance 11 has no power within
words, and the cross-word distance-11 dip is at the multiple-testing floor with no test
available to settle it.

Any model rejected on `d6w` alone has been rejected on 31 coincidences.

## Scripts

- `experiments/distance6_power.py` — the distance table within and across words, the
  power column, the family pooling and the split-half control.
- `experiments/battery_lp_error.py` — every battery cell re-tested with the LP's own
  sampling error.

## Related

- `quagmire-odometer.md` — the model whose one recorded failure this weakens.
- `quagmire-dodge.md` — records d6 as reachable by tuning, which now matters less.
- `length-clocked-walk.md` — fits d6w as one of its six cells.
