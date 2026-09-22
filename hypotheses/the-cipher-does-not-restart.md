---
type: hypothesis
---
# The Cipher Does Not Restart at Any Structural Boundary

## The claim

The base never returns to a common value at a sentence mark, a page break or a section
break. A resynchronisation — the rotor-machine ground setting, reapplied at each
boundary — is excluded.

This closes the most attractive explanation of the sentence-edge anomaly
(`sentences-do-not-end-long.md`): that the mark means something to the **cipher** rather
than only to the scribe.

## Why it was worth testing

**D12 does not already exclude it.** `base_changes_every_block.py` caps unchanged edges
at 15% of the total. Sentence marks are 5.8% of edges and page breaks 1.9%, so a restart
confined to boundaries fits inside that cap and had never been looked for directly.

## The test, which needs no key

If every block after a boundary carries the same base and phase, two such blocks agree at
position k exactly when their plaintexts do, because both cancel:

    c_w[k] = c_w'[k]   iff   base(g^k(p_w[k])) = base(g^k(p_w'[k]))   iff   p_w[k] = p_w'[k]

So position-aligned coincidence over all pairs of boundary-following blocks reads the
plaintext rate under a restart and chance under anything else. Word-initial plaintext is
strongly non-uniform, so the gap is wide.

The null is length-matched — coincidence depends on length through the number of aligned
positions a pair contributes — resampling blocks of exactly the observed lengths from
the whole body, 200 draws.

## Result

| boundary | blocks | observed | matched null | z |
|---|---|---|---|---|
| a sentence mark | 148 | 0.0338 | 0.0348 ± 0.0011 | **−0.96** |
| a page break | 18 | 0.0318 | 0.0344 ± 0.0093 | −0.28 |
| a page or section break | 20 | 0.0311 | 0.0348 ± 0.0081 | −0.45 |
| any boundary at all | 171 | 0.0342 | 0.0349 ± 0.0010 | −0.79 |

## What the test can see, and what it cannot

This is the part that fixes the claim's scope. Planting each kind of reset at the
sentence-mark count:

| planted | observed | z |
|---|---|---|
| base and clock both reset | 0.0914 | **+53** |
| base resets, clock runs on | 0.0507 | **+17** |
| clock resets, base runs on | 0.0333 | **−1.6 — invisible** |
| nothing resets | 0.0354 | +0.5 |

So the null excludes a **base** reset, with or without the clock. It says nothing about a
clock-only reset, and that blindness is **structural, not a sample-size problem**: blocks
carrying different bases coincide at chance whatever their phase. The clock cancels
inside a block (`d-profile-pins-g-to-five-cycles.md`) and the base hides it across one, so a
clock-only reset is invisible to every key-free channel there is. It would need a key to
detect, which puts it out of reach.

The page-break cell carries only 18 blocks, where a planted full reset reaches about +4σ.
**That cell excludes a full reset and nothing weaker.** Only the sentence-mark cell is
strong.

## A tokenization note this turned up

`experiments/sentences_do_not_end_long.py` drops transcription lines carrying no runes.
All 55 `%`, 9 `$` and 15 `&` sit on their own lines, so they were all being discarded.
That happens to produce exactly the **corrected** parse that `page-breaks-cut-blocks.md`
argues for — 2,896 blocks, mean 4.474, rather than the canonical 2,928 with 34 spurious
fragments — so the effect is benign. But it was accidental, and it meant page breaks had
no representation at all.

The parser here makes it deliberate: a standalone marker never cuts a block, and it
flags the next block only where a separator had already closed the previous one. That
leaves **19 clean page starts**, which is what the page-break row rests on.

## How to falsify this

- **A key-dependent restart test.** Every reading here is key-free, which is why the
  clock-only reset escapes. A verifier that carries a candidate key could see it.
- **More page breaks.** Pages 57+ would add a handful of clean page starts; the cell
  needs roughly four times as many to match the sentence-mark cell's power.
- **A restart to something other than base_0.** The test asks whether boundary-following
  blocks share *a* base, not specifically the initial one, so this is already covered —
  but a restart to a base that *varies by boundary* (a per-section ground setting, say)
  would be missed. Splitting the marks by section and testing within each is the check,
  and 148 blocks over 9 sections leaves too few per cell to run it now.

## Status

**Status**: confirmed for a base reset at a sentence mark (z = −0.96 against a +53σ
positive control). Weak for page breaks (18 blocks, +4σ control). Silent on a clock-only
reset, which is unreachable key-free. `experiments/does_the_cipher_restart.py`.

## Related

- `sentences-do-not-end-long.md` — the anomaly this was trying to explain, still open.
- `experiments/base_changes_every_block.py` — D12, the 15% cap that left room for this.
  It has no hypothesis file of its own; the spec row carries it.
- `d-profile-pins-g-to-five-cycles.md` — the lag-k cancellation identity, and why the
  clock is invisible inside a block.
- `page-breaks-cut-blocks.md` — the tokenization this depends on.

## The key does not cycle either, for any period up to eight

`experiments/a_shifted_stop_or_a_switched_key.py`

This file excludes a base **reset** at a mark: blocks following one would share a base and
coincide at the plaintext rate, and they read z = −0.96 against +53 for a planted reset.
That assumes the mark returns the base to a single common value.

A key that **cycles** through N keys, advancing at each mark, is invisible to that test:
with N = 3 only every third span shares a base and pooling dilutes the signal by N.
Grouping the spans by mark index mod N recovers it.

| keys in the cycle | observed | z |
|---|---|---|
| 1 | 0.0337 | −0.89 |
| 2 | 0.0341 | −0.43 |
| 3 | 0.0300 | −2.03 |
| 4 | 0.0357 | +0.36 |
| 5 | 0.0309 | −1.50 |
| 6 | 0.0310 | −1.18 |
| 8 | 0.0320 | −1.04 |

(The observed rates are exact; the z values come from a resampled null and moved by up to
0.3 when the file was edited, since the null's random stream is shared. They are stable
run to run and the range −2.03 to +0.36 is what a seven-cell scan gives by chance.)

Chance is 1/29 = 0.0345. **Nothing at any period.**

The control enciphers English with a real 3-key cycle and reads it back at z = +34.19 for
N = 3 and +22.83 for N = 6, its multiple, against +9.8 to +19.5 at the wrong periods — the
wrong periods stay positive because their groups still contain some same-key pairs, which
is why the true period has to stand out rather than merely be positive.

This closes key switching at the four-dot as a family rather than as a single variant. It
remains blind to a clock-only switch, for the reason given above: blocks carrying
different bases coincide at chance whatever their phase.
