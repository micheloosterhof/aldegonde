---
type: observation
---
# Observation: No Running-Key Depth at Any Lag

## Feature

The difference-stream index of coincidence shows no spike at any lag: the corpus
has no repeating or self-referential key of any period, and no external
language-text running key aligns anywhere.

## Measurement

`experiments/depth_search.py` (clean corpus): difference IoC Diff_d =
C[i]-C[i+d] over ALL lags 2..6520, both Vigenere and Beaufort sense, against a
doublet-suppressed surrogate null (correct 1/n IoC variance law).

| quantity | observed | surrogate null |
|----------|----------|----------------|
| lags at z>4 | 16 (max z 5.52, all nIoC <= 1.02) | 11.9 (max z 5.19) |
| a real depth would show | spike to nIoC ~1.05, localized | — |

## Significance

Wherever a running key realigns, the difference stream reveals a
runeglish-difference at nIoC ~1.05. No lag reaches that; the observed excess is
indistinguishable from the doublet-suppression baseline. This excludes ANY
repeating or self-referential key (the corpus against itself, any section,
forward or reversed, at any offset), and separately the directly-tested external
texts (Parable, master transcription) at all alignments.

## Significance caveat

This does NOT exclude a NON-repeating key at least as long as the text and
statistically uniform (an effective one-time pad); that leaves no depth to find.
See `stream-cipher-no-repeat.md`.

## Consequences

- Excludes `running-key-text.md` and `running-key-math-sequence.md` as repeating
  or self-keys.
- Forces any keystream to be non-repeating (walk state, PRNG, or OTP).

## Scripts

- `experiments/depth_search.py`

## Related

- `running-key-text.md`, `running-key-math-sequence.md` — the hypotheses this
  disproves.
- `no-periodicity.md`, `stream-cipher-no-repeat.md`.

## The scan's reach under a preventer, and why the conclusion still holds (September 2026)

The depth search scans lags 2 to 6520. That reach assumes the keystream advances in
step with position, and `preventer-blinds-absolute-tests.md` shows the author himself
uses a device that breaks the assumption.

The difference stream `C[i] − C[i+d]` is a relative-distance statistic, so a pair
survives only if no interrupt falls between its members — probability `(1−q)^d`:

| q | d=10 | d=29 | d=50 | d=100 | d=500 |
|---|---|---|---|---|---|
| 0.012 | 0.886 | 0.705 | 0.547 | 0.299 | 0.002 |
| 0.024 | 0.784 | 0.494 | 0.297 | 0.088 | 0.000 |
| 0.034 | 0.708 | 0.367 | 0.177 | 0.031 | 0.000 |

Half the pairs survive only out to lag 57, 29 or 20 at those rates. **So under a
preventer this scan does not reach 6520; it reaches roughly 30.**

**The conclusion is unaffected, because a different bound covers the gap.** The three
tests partition the period axis cleanly:

| period | excluded by |
|---|---|
| 2 – 29 | this depth scan, even under a preventer |
| 2 – 949 | the IoC alphabet-count bound, which is phase-independent |
| > 949 | neither — and `unicity-distance.md` shows a key that long is unbreakable with 12,956 runes regardless |

So nothing hides in the gap. A repeating key short enough to matter is excluded by IoC
whatever the interrupt rate, and one long enough to evade IoC is long enough to be an
effective one-time pad — which is exactly the caveat this file already records, now with
the boundary put at a number.

What should change is the citation: the "any lag to 6520" reach belongs to an
uninterrupted cipher, and against a preventer-family model this scan should be quoted
as covering short lags only.
