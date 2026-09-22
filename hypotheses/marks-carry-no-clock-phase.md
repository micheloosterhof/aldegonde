---
type: observation
---
# The Marks Carry No Clock Phase, and the Test Could Not Have Found One

## Status

**Status**: closed channel, with the reason measured. `experiments/marks_and_the_clock_phase.py`.

## What was worth asking

If the four-dot marks sat where the cipher's clock stood at a particular phase, that
would tie the scribe's punctuation to the mechanism — the first such link, and every
other convention at the page-15 break has turned out to be scribal
(`one-production-break-at-page-fifteen.md`, and
`experiments/the_interrupter_tracks_the_cipher.py`).

The cumulative rune count at each mark is the obvious probe: the clock advances one per
rune, so the count mod 5 should be the phase.

## The measurement

| set | counts mod 5 |
|---|---|
| every block-closing boundary | [562, 563, 589, 593, 588] |
| closed by a four-dot | [19, 26, 22, 35, 34] |

Against a null placing 136 marks at random block-closing boundaries — which carries the
block-length distribution, and so the residue structure cumulative sums inherit —
**χ² = 6.55, P = 0.15**. Thirteen-dot reads P = 0.98 on 25 marks.

## Why the null result is uninformative

The dodge advances the clock an extra step at about 3.4% of positions, so across 12,956
runes the clock runs some 440 steps ahead of the rune count and the two decorrelate
within a page. Planting the effect:

| marks placed | χ² over 30 runs | P < 0.05 |
|---|---|---|
| at the generator's **true** clock phase 0 | 5.36 ± 4.12 | **6/30** |
| at random block ends | 4.34 ± 3.74 | 3/30 |

Twenty percent detection against a ten percent false-positive rate. **The channel is
closed, not the question answered.** It fails for the same reason the doublet-position
test did: anything measured against absolute rune position is measuring a quantity the
clock has already drifted away from.

## Two wrong nulls caught on the way

Both would have been reportable:

- **Uniform mod 5** gives P = 0.062, with modulus 5 the only one of seven showing
  anything (the rest run 0.36 to 0.99) — and modulus 5 is pre-specified, since 5 is the
  cipher's period, so it would have read as a real hint. But block lengths are not
  uniform mod 5 and cumulative sums inherit that, so the flat null is wrong.
- **A boundary set including separators that close no block** repeats the same cumulative
  count and doubles one residue: [566, 567, 595, 597, **1118**] over 3,443 "boundaries"
  for 2,896 blocks. Against that null the marks read P = 0.0485. Requiring runes since
  the last boundary gives 2,895 and a flat profile.

## What would reopen it

A key-dependent test. The clock is recoverable only alongside a candidate key, so a
verifier carrying one could place each mark on the true clock rather than on the rune
count. Nothing key-free can do it.

## Related

- `doublet_gaps_conditioned.py` — the same drift closing a different channel.
- `the-thirteen-dot-closes-a-section.md` — what the marks are instead.
