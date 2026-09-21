---
type: observation
---
# Observation: The Repeat's Second Occurrence Is the Final Six Runes of the Body

## The test that cannot be run

Four results now condition on the DJU-BEI repeat being a genuine state return:
`dju-bei-needs-a-product-step.md`, `sigma-is-even.md`,
`dju-bei-favours-the-continuous-clock.md`, and through them the A₂₉ reading of the base
family. That is a lot of weight on one observation, so the direct test matters.

The direct test is to look at what *follows*. If the state genuinely recurred, the two
continuations run with the same base and the same phase, so their runes coincide at the
**plaintext** rate — 1.79× chance — for as long as the block lengths keep the clocks
aligned. A coincidence predicts chance.

**There is nothing to look at.** The second occurrence is at rune offset 12,950 of 12,956:
the final six runes, blocks 2,926 and 2,927 of 2,928, ending master chunk 70 — the last
body chunk before the solved AN END page.

*Checked, September 2026.* "Nothing follows" is not quite right and the conclusion is
unchanged. `data/page0-56.txt` is a strict prefix of `data/page0-58.txt`, which carries
180 more runes: 85 on the AN END page, split into two runic segments of 45 and 40 either
side of the hex signature, and 95 in the plaintext Parable. So material does follow — but
the 85 runes are enciphered with a **prime running key**, a different and already-solved
system (`solved_page_triples.json`, page 71: "AN END. WITHIN THE DEEP WEB THERE EXISTS A
PAGE THAT HASHES TO…"), and the 95 are not enciphered at all. Nothing enciphered with the
body's own cipher follows the return, so the continuation test remains impossible for the
reason this file gives, with a sharper statement of why.

| | |
|---|---|
| first occurrence | rune 6,555, block 1,477 |
| second occurrence | rune 12,950, block 2,926 |
| runes after it | **0** |

So the sharpest available check on the return hypothesis is unavailable, and the four
downstream results stay conditional on something that cannot be verified from this corpus.

## But the position is itself evidence

Given that a repeat exists, its second occurrence landing in the final six runes has
probability 6/12,951 ≈ **1 in 2,158**.

That is a second improbability on top of the 1-in-2,700 for the repeat existing at all
(`dju-bei-is-more-surprising-than-recorded.md`), and it cuts against the chance reading:
**a coincidence now has to explain the position as well.** A deliberate reading — a closing
refrain, a colophon, a signature at the end of the enciphered text — explains it for free.

The two figures should not simply be multiplied. The position was noticed *after* the
repeat, so it is a post-hoc observation and carries less weight than a pre-registered one.
But it is not nothing, and it points the same way.

## A reading this suggests

The book's last phrase repeats a phrase from near its middle (block 1,477 of 2,928 — close
to the midpoint, though not exactly). That is a literary device before it is a
cryptographic one. Under that reading the repeat is a **plaintext** repeat, and the
remarkable part is not that the phrase recurs but that it **enciphers identically** — which
still requires the key state to coincide, and so still implies the return.

In other words the deliberate reading does not remove the need for a state return; it
supplies a motive for one.

## The first occurrence is marked too

If the repeat is deliberate, the first occurrence should also sit somewhere the book marks.
It does (`experiments/dju_bei_structural_position.py`):

| | position |
|---|---|
| **first** | chunk 42, page 27 — which **opens a section** and **carries a rubricated title** of 19 runes in 3 words. The repeat begins **9 runes after the title ends**, at chunk offset 28 of 234. |
| **second** | chunk 70, page 55 — offset 70 of 76, **zero runes left**, the last two blocks of the body. |

How surprising a randomly placed 2-block unit would find each:

| | probability |
|---|---|
| landing in the final six runes | 0.00046 (1 in 2,158) |
| landing in the first five blocks of one of the 15 rubricated-title pages | 0.026 (1 in 39) |

**Both occurrences sit where a scribe would put a refrain** — one just after a section
title, one as the last words of the enciphered book. That is what a deliberate repeat
looks like and not what a coincidence looks like.

The caution is the same as above and applies twice over: both positions were noticed
*after* the repeat, neither was predicted, and the two probabilities should not be
multiplied into a single figure.

## Status

**Status**: confirmed (position, exact). The consequence — that the continuation test is
unavailable — is structural. `experiments/dju_bei_position.py`.

## Related

- `dju-bei-is-more-surprising-than-recorded.md` — the 1-in-2,700 for the repeat itself.
- `dju-bei-needs-a-product-step.md`, `sigma-is-even.md`,
  `dju-bei-favours-the-continuous-clock.md` — the results that stay conditional.
- `repeated-phrase-dju-bei.md` — the original record of the repeat.
