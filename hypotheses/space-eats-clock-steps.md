---
type: hypothesis
---
# Hypothesis: The Space Is Enciphered Too, and Eats Clock Steps

## Claim

Michel's proposal (September 2026). The word separator is enciphered like any other
letter and simply not transmitted, so the clock advances `k` extra steps at every word
boundary. Two runes on opposite sides of a boundary are further apart on the clock than
they look in the transmitted text:

```
clock distance = (transmitted runes between) + k x (boundaries between)
```

## Status

**Status**: not settled, and not settleable by the coincidence route. The test is
well-powered and comes back flat, but a second mechanism — the per-word base change —
predicts exactly the same flatness whatever `k` is, so the negative does not
discriminate.

## The test, and why five classes exhaust every skip in both directions

Within words the period-5 echo is plain: gap 5 reads 0.0492 against chance 0.0345,
z = +3.67, because two positions five apart share an alphabet. If the space eats `k`
steps the same echo should appear across a boundary wherever the clock distance is a
multiple of five.

For pairs spanning a single boundary the clock distance is `gap + k`, so changing `k`
only relabels which residue class of the gap carries the echo. Pooling every cross-word
pair by `gap mod 5` therefore tests all values of `k` at once, and uses every pair
rather than the few at gap exactly 5. That is where the power comes from.

**Negative skips are the same rows.** Michel raised the space running the clock BACK
instead of forward — repeating the previous word's last alphabet. Only `k mod 5` can
matter, because the schedule has period 5, so `k = −1` is `k = 4`, `k = −2` is `k = 3`,
and so on. The five classes cover every skip in both directions. `doublet_phase_test.py`
asserts this rather than assuming it: the phase counts for `k = −1 … −4` come out
byte-identical to those for `k = 4 … 1`.

## Result: flat at every k

Cross-word pairs spanning one boundary, seam excluded: 1,857 / 54,240 = 0.0342, against
chance 0.0345.

| gap mod 5 | implies k | hits / pairs | rate | z vs chance | z vs the other classes |
|---|---|---|---|---|---|
| 0 | 0 or −5 | 338 / 9,887 | 0.0342 | −0.16 | −0.03 |
| 1 | 4 or **−1** | 278 / 8,170 | 0.0340 | −0.23 | −0.11 |
| 2 | 3 or −2 | 429 / 12,204 | 0.0352 | +0.41 | +0.63 |
| 3 | 2 or −3 | 404 / 12,485 | 0.0324 | −1.30 | −1.32 |
| 4 | 1 or −4 | 408 / 11,494 | 0.0355 | +0.60 | +0.84 |

**The power is real, unlike at distance 6.** Each class holds about 10,800 pairs, so an
echo the size of the within-word one would read **z = +8.40**. The largest observed is
+0.84, where chance over five classes gives 1.79. The within-word control in the same
run reads +3.67, so the machinery detects the echo where it exists.

The seam is excluded from the classes because the doublet preventer suppresses it by
design — at gap 1 the rate is 23 / 2,927, z = −7.89 — and it would swamp its own class.

## Why the negative does not settle the claim

The echo needs a shared ALPHABET and a shared BASE. Every model in this directory
changes the base at every word boundary, which is what the flat IoC (0.9999) and the 17
identical words demand — `pure-quagmire-word-restart.md` measures the per-word step as
needing 5,000–10,000 states. That change alone erases cross-word coincidence whatever
the clock does.

So the flat result is what the per-word base change predicts on its own, and the space
question is hidden behind it. The claim survives, untested.

## The sharper test, and what blocks it

A one-zero schedule lets the preventer fail at exactly one clock phase, so **every
surviving doublet** — the 63 inside words and the 23 at the seam — should sit at a
single phase. The phase of a position is the cumulative rune count plus `k` per boundary,
so the concentration would pin `k` without knowing the alphabet, the schedule or the
base. With 86 events against five classes that has ample power.

It cannot be run against this corpus. The preventer advances the clock whenever it
fires, and it fires far more often than it fails, so the clock drifts from the position
count at the skip rate `q`:

| q | drift reaches 5 steps after |
|---|---|
| 0.031 (= 5 × d1w) | 161 runes, 37 words |
| 0.045 (measured on models) | 111 runes, 25 words |

The corpus is 12,956 runes. Beyond the first couple of dozen words the phase computed
from position is unrelated to the real one, so the doublets cannot be binned.

This is a general obstacle, not one specific to this hypothesis: **any test that needs
the absolute clock phase is unavailable while the preventer is in the model**, because
the preventer's own fires are invisible in the ciphertext.

## What to do next

1. **Test `k` inside words instead.** The space only acts at boundaries, so within a
   word the clock is undisturbed by it. Nothing there depends on `k`, which is why this
   route found nothing — but a model FIT can still prefer one `k`, because `k` changes
   the phase each word starts on and therefore which words can carry a seam doublet.
   That is a likelihood comparison over `k`, not a coincidence count.
2. **Or drop the preventer's clock skip.** If doublet suppression works some other way
   that leaves the clock alone, the phase-concentration test above becomes available and
   settles `k` in one measurement. That is a reason to look for a non-skipping
   suppression rule beyond the ones already tried.

## Scripts

- `experiments/space_eats_clock.py` — the residue-class scan, the within-word control,
  the power calculation and the drift calculation that blocks the phase test.

## Related

- `quagmire-odometer.md` — the model this would modify; its per-word step is what hides
  the answer.
- `distance-6-has-no-power.md` — the companion power analysis; that test lacked pairs,
  this one has them and still finds nothing.
- `doublet-dodge-walk.md` — where the clock-skipping preventer comes from.
- `separator-loss-is-selective.md` — the other reason word boundaries matter here.

## Verdict

Not settled. The coincidence test is well-powered, comes back flat at every `k` — and
since only `k mod 5` matters, that is every skip in both directions, the backward space
included — and cannot distinguish the hypothesis from the per-word base change that
would produce the same flatness. Recorded mainly for two things it does establish: the
cross-word channel carries no period-5 signal at any clock convention, and no test
requiring the absolute clock phase is available while a clock-skipping doublet
preventer is in the model.
