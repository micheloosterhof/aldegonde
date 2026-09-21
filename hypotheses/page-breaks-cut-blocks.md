---
type: observation
---
# A Page Break Cuts a Block in the Thirty-Four Places Where No Separator Was Written

## Status

**Status**: confirmed, and it is a defect in the corpus tokenization rather than a
property of the cipher. The corrected parse is available but not the default; see
*What to do about it*.

## Claim

`c3301.WORD_BOUNDARY` contains `%`, the page break, so `lp_corpus.load_clean` ends a
block at every page boundary. That is right where the scribe wrote a separator before
the page ran out and wrong where he did not.

**In 34 of the 55 page breaks a rune stands immediately before the `%`.** There a block
that continues onto the next page is counted as two, which puts 34 spurious fragments
into the canonical 2,928.

## How the two cases separate

Split the page breaks by whether a separator precedes them and look at the first block
of the next page. A cut leaves a fragment; a genuine boundary leaves an ordinary block.

| first block of the new page | n | mean | 1 rune | 2 runes |
|---|---|---|---|---|
| **after a break with a rune before it** | 32 | **2.594** | **0.281** | 0.375 |
| after a break with a separator before it | 17 | 4.000 | 0.059 | 0.294 |
| every block | 2,928 | 4.425 | 0.034 | 0.159 |

After a break with a rune before it, the first block is a single rune **eight times as
often** as a block should be. After a break with a separator before it, the first block
is ordinary to three decimals in the mean. Nothing about page starts is intrinsically
short — only the ones that follow an unterminated block.

## What it changes

| parse | blocks | mean | fraction at 2 | seam | d1 within | z vs the author |
|---|---|---|---|---|---|---|
| as recorded everywhere | 2,928 | 4.425 | 0.1588 | 0.0079 | 0.0063 | −4.81 |
| joined at page breaks | 2,896 | 4.474 | **0.1547** | 0.0079 | 0.0063 | **−5.05** |

About one percent on every block-level number. `seam` and `d1w` do not move at four
decimals: the 34 false boundaries are a 1.2% contamination of 2,927 seam pairs, and the
pairs they add back within blocks are too few to shift the doublet rate.

**The hole at length 2 gets deeper, not shallower.** So none of
`block-lengths-have-a-hole-at-two.md` is at risk; its numbers are the conservative ones.

## What to do about it

`load_clean(join_pages=True)` gives the corrected tokenization. **The default is left
unchanged**, because switching it re-bases every block-level number recorded in this
directory — 2,928 blocks appears in dozens of files — and that is a decision to take
deliberately rather than as a side effect. The recommendation is to switch it and re-run
the affected files in one pass.

What would need re-running: anything quoting a block count, a block-length statistic, or
a position index into the block sequence. The DJU-BEI return is identified by word
identity rather than position, so it survives renumbering, but its recorded indices
(1477/1478 and 2926/2927) would shift.

## Falsification

- If the 34 breaks are genuine boundaries with the separator simply lost at the page
  edge, then the fragments after them are real blocks and should look like ordinary
  blocks. They do not: 28% of one rune against 3.4%.
- If page starts were intrinsically short for some scribal reason — a decorated initial,
  say — the effect would appear after the 21 clean breaks too. It does not.
- The 34-against-21 split is from the transcription. If a page's final separator is
  present in the scan but missing from the transcription, the count moves and the
  correction should be applied to fewer breaks.

## Scripts

- `experiments/page_breaks_cut_blocks.py`
- `experiments/lp_corpus.py` — `load_clean(join_pages=...)`

## Related

- `block-lengths-have-a-hole-at-two.md` — the result this touches, which the correction
  strengthens.
- `separators-are-the-cipher-unit.md` — if blocks are the cipher's units, a cut block is
  a cut unit, and the 34 are worth excluding from any per-block key statistic.
