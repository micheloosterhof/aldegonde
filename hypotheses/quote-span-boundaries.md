---
type: observation
---
# Quoted Spans Align to the '.' Marks (the Marks Are Not Inert)

## Status

**Status**: confirmed (characterization) for the alignment itself
(p = 1.5e-7, layout-robust). What the '.' marks therefore *are* remains open —
this result rules out one answer, not in another.

## Claim

The seven quoted spans recovered from the page scans
(`contraction-cribs.md`) do not sit at arbitrary word boundaries. They align
to the '.' marks from both directions:

- **8 of 14 span edges land on a '.' mark**, against 0.7 expected if quotes
  picked word boundaries uniformly — p = 1.5e-7.
- **'.' marks are depleted strictly inside spans**: 1 observed across 79
  internal boundaries against 4.2 expected — p = 0.071.

Quoted speech starts and stops at '.' marks and avoids crossing them. **The
'.' marks therefore carry structure that plaintext respects.** They are not
a second, interchangeable word separator.

This does **not** make them English sentence ends: the sentence-final
word-length signature is still absent
(`word-length-keystream-and-boundaries.md`, z = -1.21), and the marks that
carry quote edges show no more of it than the rest (4.14 vs 4.23, n = 7 —
underpowered, reported only so it is not mistaken for support).

## Evidence

The seven spans (`experiments/quote_span_analysis.py`):

| # | words | runes | '.' inside | opens on | closes on |
|---|---|---|---|---|---|
| 1 | 4 | 18 | 0 | . | - |
| 2 | 5 | 19 | 0 | - | . |
| 3 | 2 | 12 | 0 | . | - |
| 4 | 14 | 58 | 0 | - | . |
| 5 | 13 | 68 | 0 | . | . |
| 6 | 34 | 160 | 1 | . | - |
| 7 | 14 | 70 | 0 | . | - |

Span lengths: 2, 4, 5, 13, 14, 14, 34 words (median 13). That is an
unremarkable spread for English quoted speech — short quoted phrases and
longer utterances — and it is *not* evidence for anything on its own; seven
spans cannot discriminate a length distribution. It is reported because a
wildly wrong spread (all spans 200 words, or all exactly equal) would have
argued against the reading, and it does not.

Opens favour '.' more than closes (5 of 7 versus 3 of 7), which is the
English pattern: a quotation reliably opens after a full stop but often
closes before a comma or a speech tag that no mark here records.

Span 6 opens on page 42 and closes on page 43. The structure crosses a page
boundary, so it is not per-page decoration.

### The layout confound is controlled

'.' marks cluster at line ends (19.9% versus 3.7% for '-'), so co-location
by typography had to be excluded. Only **2 of 14** quote marks sit at a line
end, so the adjacency is not inherited from that clustering.

More robustly, without modelling any particular layout effect: '.' would have
to make up **33% of boundaries at quote-eligible positions — 6.1x the corpus
rate** — before 8 of 14 stopped being surprising at p = 0.05. The strongest
layout coupling anywhere on record in this corpus is 3.7x.

## What this does not show

- It does not identify the unit. A clause, verse, breath group or utterance
  boundary would all attract quote edges while failing the sentence-final
  word-length test. The result narrows the question rather than settling it.
- It does not resurrect the sentence-position reading of the four
  apostrophes. That needed '.' to be an English *sentence* end specifically,
  and this result does not supply that.
- It cannot exclude an elaborate decorative layer in which quotes were placed
  next to '.' marks deliberately. That forger must also make the quotes nest
  perfectly across 47 pages (`contraction-cribs.md`, p = 1.2e-4).
- The depletion result is p = 0.071 — a hint, not a finding. Only the edge
  alignment is strong.

## Consequences

`word-length-keystream-and-boundaries.md` concludes the '.' marks "do not mark
English sentence ends" and raises that the visible segmentation may be
cosmetic — "exactly what a cosmetic segmentation designed to look like
language would preserve". That conclusion stands as stated, but the cosmetic
reading is now harder: a cosmetic mark would have no reason to organise
quoted speech. Both facts have to hold together — the marks delimit something
the plaintext respects, and that something is not an English sentence.

The mixture proposal in that file (a minority of genuine sentence ends plus a
majority of filler) predicts that quote-adjacent marks are the genuine ones.
The word-length probe above does not support that, at n = 7.

## Scripts

- `experiments/quote_span_analysis.py` — span lengths, edge alignment,
  internal depletion, layout control, mixture probe.

## Related

- `contraction-cribs.md` — where the marks come from and how they were placed.
- `word-length-keystream-and-boundaries.md` — the '.'-mark result this
  qualifies.

## Verdict

The '.' marks are not semantically inert, and reading them as merely a second
word separator does not survive this test. They delimit units that quoted
speech opens on, closes on, and avoids crossing. What those units are is the
open question, and it is now sharper than before: something the plaintext
respects, that is not an English sentence.
