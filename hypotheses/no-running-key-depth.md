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
