---
type: observation
---
# Observation: The Interrupter Is An Exact Plaintext Rule, And The Body Does Not Use It

## The rule

`interrupter-is-a-scribal-mark` states the puzzle from the ciphertext side: on page 1
only 6 of 14 ciphertext rune-F actually interrupt, so the trigger cannot be read off the
rune, and skip positions have to be searched. Stated that way it looks like a scribal
decision with no rule behind it.

From the plaintext side there are no exceptions at all. Across every interrupted page in
the testbed — chunks 1, 2, 12, 13 and 71, spanning two different ciphers — the set of
interrupt positions **equals** the set of positions where the plaintext rune is F:

| chunk | cipher | plaintext F | interrupts | equal |
|---|---|---|---|---|
| 1 | interrupted vigenere | 6 | 6 | yes |
| 2 | interrupted vigenere | 3 | 3 | yes |
| 12 | interrupted vigenere | 2 | 2 | yes |
| 13 | interrupted vigenere | 0 | 0 | yes |
| 71 | prime running key | 1 | 1 | yes |

> **Every plaintext F is passed through literally, and nothing else is.**

Chunk 13 is the useful one: zero plaintext F, zero interrupts. The rule is not "some F's
are special", it is "F is not enciphered".

The ciphertext-side confusion dissolves. A ciphertext ᚠ arises two ways — a literal
plaintext F, or any plaintext letter that the key happens to send to F — and only the
first kind interrupts. On page 1 that is 6 of 14, which is exactly the mix the rune
frequency predicts.

## Why this matters: a bound becomes a point prediction

The interrupt rate is therefore not a free parameter. It is the plaintext's own F
frequency, and `lp-plaintext-register.md` measures that on the author's own words:
**0.0158 ± 0.0028** over 1,963 runes. The solved pages' own interrupt rate, 12/919 =
0.0131, agrees.

F is common in this register because the runeglish convention writes C as F —
`FIRFUMFERENFE` for CIRCUMFERENCE is the author's own spelling.

`passthrough_interrupter_bound.py` already bounded any rune-emitting interrupter in the
body from the flat unigrams. With the rate now known rather than bounded, the same
algebra gives a prediction instead:

| | rune-F rate in the body |
|---|---|
| predicted, q + (1−q)/29 | 0.0497 |
| **observed** | **0.0354 ± 0.0016** |
| | **z = −4.43** |

In counts: the rule predicts **205 interrupts** in the body; the unigram bound allows at
most **47**.

**The body does not use the author's own interrupter.** Either its plaintext has far
fewer F's than the front matter — implausible, same author, same spelling convention —
or the device is absent.

## The consequence is methodological, and it loosens things

`preventer-blinds-absolute-tests.md` prices what an interrupter costs every
alignment-based test: a distance-d pair survives with probability (1−q)^d, so the usable
reach is about 1/q. Every scan in this directory has been quoted at q ≈ 0.0175, giving an
expected clean run of **57 runes**.

That figure is now an upper bound on the damage, not an estimate of it:

| q | expected run before the first interrupt |
|---|---|
| 0.0158 (the author's own rate) | 63 runes |
| 0.0037 (the body's 95% ceiling) | **273 runes** |

So against a rune-emitting interrupter, alignment tests in the body reach roughly **four
times further** than they have been credited with. `running-key-math-sequence.md`'s
57-rune prefix was conservative by that factor, and prefix-scored searches should be
re-run longer.

## Scope

This covers interrupters that **emit** a rune, which is the only kind that shows in the
unigram table and the only kind the author is known to use. A clock perturbation that
skips a key step while still enciphering the rune — the `quagmire-dodge.md` and
`interrupted-walk.md` families — leaves no unigram trace, is untouched here, and would
blind alignment tests exactly as before.

So the honest reading is conditional: **if** the body's clock is perturbed at all, it is
not perturbed by the author's own device.

## Status

**Status**: confirmed (exact on 12 of 12 interrupts across 5 pages and 2 cipher
families; the body's refutation is z = −4.43). `experiments/interrupter_rule.py`.

## Related

- `interrupter-is-a-scribal-mark` (memory) — the ciphertext-side framing this replaces.
- `passthrough_interrupter_bound.py` / `solved-page-testbed.md` — the bound this sharpens.
- `preventer-blinds-absolute-tests.md` — the reach calculation this loosens.
