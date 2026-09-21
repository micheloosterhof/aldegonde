---
type: observation
---
# Observation: DJU-BEI Is the Only Anomalous Repeat at Any Length

## The question the deliberate reading raises

`dju-bei-ends-the-body.md` argues the repeat is deliberate: both occurrences sit where a
scribe would put a refrain — one just after a section title, one as the last words of the
book. A deliberate return means the author had enough control over the key schedule to
force the base back after 1,449 blocks. **An author with that control might have used it
more than once**, leaving shorter returns behind.

So census every window length. A state return produces a repeat that starts at a block
boundary and spans whole blocks, so the aligned column is where an engineered return would
show.

## Result

| length | windows | repeats | expected | | aligned | repeats | expected |
|---|---|---|---|---|---|---|---|
| 3 | 12,954 | 3,009 | 3,461 | | 768 | 17 | 12.15 |
| 4 | 12,953 | 128 | 119.6 | | 629 | **0** | 0.28 |
| 5 | 12,952 | 6 | 4.1 | | 608 | **0** | 0.009 |
| **6** | 12,951 | **1** | 0.1 | | 649 | **1** | **0.0004** |
| 7 | 12,950 | 0 | 0.0 | | 669 | 0 | 0.0000 |
| 8 | 12,949 | 0 | 0.0 | | 644 | 0 | 0.0000 |

**Every length but six matches chance in the aligned column** — 17 against 12.2 at length
three (p ≈ 0.11, unremarkable), zero against 0.28 at four, zero against 0.009 at five. At
length six there is one against **0.0004**.

## What it means for both readings

**DJU-BEI stands alone.** There is no family of shorter engineered returns, and no partial
trail. Both readings inherit the consequence:

- **Chance** must produce exactly one 1-in-2,700 event and nothing else out of place.
- **Design** must have had the capability and used it exactly once — which fits a refrain
  bracketing the book, and fits nothing more elaborate.

Neither reading is embarrassed, but the space of designs narrows: an author who wove
returns through the text would have left more than one, and did not.

## The background is worth noting separately

The unaligned column is the language-and-chance floor. Length-3 repeats run **below**
chance — 3,009 against 3,461 — which is the corpus's own repeat suppression showing
through at trigram scale, the same mechanism that holds doublets to 0.0063. Lengths four
and five sit on the expectation.

## Status

**Status**: confirmed (census over the whole body, lengths 3 to 8).
`experiments/repeat_census_by_length.py`.

## Related

- `dju-bei-is-more-surprising-than-recorded.md` — the 1-in-2,700.
- `dju-bei-ends-the-body.md` — the positional case for deliberateness.
- `doublet-suppression.md` — the suppression visible in the length-3 deficit.
