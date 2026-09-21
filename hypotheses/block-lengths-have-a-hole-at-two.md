---
type: observation
---
# The Block Lengths Have a Hole at Two, and It Is Not the Same Effect as the Missing Order

## Status

**Status**: confirmed. It refines row E1 of `what-any-solution-must-satisfy.md`, which
says the block lengths have "the marginal of running text" and carry no language order,
by showing the marginal is *not* the author's and by separating the two anomalies.

## Claim

The body's block-length marginal has only ever been compared to prose by eye. Compared
properly against the author's own plaintext it fails, and the failure is one length:

| length | LP plaintext | prose | body |
|---|---|---|---|
| 1 | 0.0329 | 0.0246 | 0.0338 |
| **2** | **0.2387** | **0.2841** | **0.1588** |
| 3 | 0.2449 | 0.1962 | 0.2480 |
| 4 | 0.1605 | 0.1440 | 0.1755 |
| mean | 4.04 | 4.23 | 4.42 |

**The body has a third fewer 2-rune blocks than the author has 2-letter words**, while
length 1 matches to three decimals and length 3 is slightly above.

## The register objection, priced

The eleven solved pages are front matter and the body is not, so a register difference
is the first thing to rule out. Two ways, both in
`experiments/block_length_shape.py`.

**The between-page spread.** The 2-rune fraction varies from 0.111 to 0.367 across the
eleven solved pages, giving a standard error on the mean of 0.0247. That is the right
denominator, because it prices exactly the difference between one page's register and
another's.

    LP plaintext 0.239,  body 0.159,  z = -3.24

**A one-parameter register tilt.** Reweight either reference by `exp(λ · length)` — a
shift toward longer or shorter words — and fit λ to the body:

| reference | best λ | χ² on 10 df | residual at length 2 |
|---|---|---|---|
| LP plaintext | +0.075 | 72.7 | **−5.2** |
| prose | +0.023 | 266.5 | **−11.5** |

Neither fits, and in both the largest residual is at length 2 with lengths 1 and 3 on
the other side. **A register cannot be wordier at one length only.**

## What closes the hole

Absorbing units into their neighbour, one parameter, fitted:

| absorbed length | best rate | χ² | residual at length 2 |
|---|---|---|---|
| 1 | 0.15 | 161.7 | −8.8 |
| **2** | **0.35** | **27.7** | **0.0** |
| 3 | 0.05 | 150.3 | −8.8 |

Only length 2. Absorbing about a third of the 2-rune units reproduces the marginal
better than any register shift does.

## But it is not the same effect as the missing order

Merging removes exactly the transitions that carry the serial signal — a short function
word followed by a longer content word — so it should move both statistics at once. If
one rate satisfies both, the body is the author's words with the short ones absorbed.

| q | marginal χ² | fraction at length 2 | excess G² per pair |
|---|---|---|---|
| 0.00 | 198.5 | 0.2420 | 0.0393 ± 0.0009 |
| 0.30 | 46.4 | 0.1723 | 0.0217 ± 0.0091 |
| **0.35** | **38.6** | 0.1620 | **0.0233 ± 0.0058** |
| 0.50 | 58.0 | 0.1277 | 0.0161 ± 0.0079 |
| 1.00 | 41,650 | 0.0017 | 0.0096 ± 0.0011 |
| **body** | — | **0.1588** | **0.0040 ± 0.0025** |

**The two fits disagree.** At the rate the marginal picks, the sequence still carries
0.023 of excess against the body's 0.004 — a difference of 0.019 ± 0.006, about three
sigma. Driving q to 1.0 brings the sequence to 0.0096, still two sigma high, and
destroys the marginal entirely.

So absorption accounts for the hole at length 2 and not for the missing serial order.
**They are two effects, not one.**

This also corrects the standing shorthand that merging is "refuted by the length
sequence". It is not refuted — it removes three quarters of the serial excess, which is
far more than anything else tried. It is insufficient.

## The hole is a process, not a register

Content varies between sections of a 58-page book. A scribal or cipher rule does not.
Splitting the body into its nine sections of 40 blocks or more:

| section | blocks | fraction at length 2 |
|---|---|---|
| 0 | 160 | 0.181 |
| 1 | 259 | 0.135 |
| 2 | 385 | 0.145 |
| 4 | 439 | 0.178 |
| 5 | 227 | 0.150 |
| 6 | 352 | 0.170 |
| 7 | 357 | 0.157 |
| 8 | 680 | 0.156 |
| 9 | 67 | 0.164 |

pooled 0.1589 over 2,926 blocks, **homogeneity χ² = 3.9 on 8 df**. The observed spread
across sections is 0.0152 against a binomial expectation of 0.0248, so the sections are
if anything more alike than independent sampling requires.

**No section reaches the author's 0.239; the highest is 0.181.** Whatever removes the
2-rune blocks applies evenly to the whole body.

That is the argument against a register explanation, and it is stronger than the
between-page one: a register that happened to be uniformly article-poor across nine
sections of unrelated content would be a coincidence, whereas a rule applied by the
scribe or the cipher is uniform by definition.

## And it is not a spelling convention

Seven of the 29 runes stand for two English letters, and THE — the commonest 2-rune
word — is ᚦ + ᛖ. If the body spelled it ᛏ + ᚻ + ᛖ, mass would move from length 2 to
length 3, which is the shape of the deficit exactly.

| convention | χ² | length-2 residual |
|---|---|---|
| as transcribed | 162.7 | −8.8 |
| **TH as two runes** | **79.4** | **−3.8** |
| TH, EA, NG as two runes | 89.8 | −3.8 |

**Splitting TH halves the misfit**, so the hypothesis is worth the number. But the
author's own practice settles it:

    TH  74 as one rune,  0 as two
    NG  24 as one rune,  0 as two
    IA  14 as one rune,  0 as two
    EA  11 as one rune,  0 as two
    AE   2 as one rune,  0 as two

**125 digraph tokens in the solved plaintext, not one written apart.** A convention
change in the body is not impossible, but there is no instance of it anywhere in the
book and it would still leave a −3.8 residual.

## Consequences

- Row E1 should read that the lengths have the marginal of running text *with a hole at
  length 2*, not the marginal of the author's running text.
- Any mechanism proposed for the block lengths now has two numbers to hit, not one: a
  34% deficit at length 2, and a serial excess of 0.004 against a plaintext 0.039.
- The eleven mechanisms measured against E1 were all tested against the serial statistic
  alone. The marginal is a second, independent handle, and it is the sharper of the two
  because it needs no surrogate — it is a distribution comparison.
- Because the hole is uniform across the body and the author's spelling is consistent,
  the two ordinary explanations — different content, different orthography — are both
  out. What remains is a rule applied uniformly to the body and not to the front matter.

## What the d5 leak cannot settle

`period5-is-confirmed.md` makes d5 the one key-free channel: within a block the base is
fixed and `g^5` is the identity, so lag-5 coincidence reads the plaintext directly. That
looked like a way to decide whether the blocks are words or arbitrary cuts of a rune
stream — if they are words, the body's d5 should match the author's within-word rate; if
cuts, his continuous rate.

Measured on the solved plaintext:

| segmentation | lag-5 rate | pairs |
|---|---|---|
| within the author's words | 0.0575 ± 0.0144 | 261 |
| continuous, boundaries ignored | 0.0624 ± 0.0055 | 1,908 |
| re-cut into the body's block lengths | 0.0633 ± 0.0127 | 200 recuts |
| **body, within blocks** | **0.0492 ± 0.0048** | 2,073 |

**The three predictions differ by 0.006 and the body's own error is 0.005, so the test
has no power.** The body sits below all three at z = −0.54, −1.80 and −1.04. The reason
is structural: at lag 5 English has almost no positional structure left, so crossing a
word boundary barely changes the rate. Lags 10 and 15 would leak too, `g` having order
5, but blocks of eleven runes or more are 1.5% of the body and supply too few pairs.

So d5 cannot decide the segmentation question, and this is worth recording so it is not
attempted again.

## Falsification

- The 486-word plaintext sample is the weak point. If the 2-rune fraction is a property
  of front matter, any newly solved body page must show 0.159 and not 0.239. That is a
  direct prediction on the next page solved.
- If the body's plaintext spells TH apart, a solved body page will show it. The front
  matter's 125-for-125 consistency predicts it will not.
- If the deficit is a transcription effect — 2-rune blocks lost to unrecorded separators
  — then the pages with the most separators should show the largest deficit. The body is
  uniform (`section-homogeneity.md`), so this predicts no page-to-page gradient.
- If absorption is right after all, some absorption rule that is not uniform over 2-rune
  units must hit both numbers. The uniform one demonstrably cannot.

## Scripts

- `experiments/block_length_shape.py`

## Related

- `separators-are-not-word-boundaries.md` — row E1's source, which measures the order
  and not the marginal.
- `separators-are-the-cipher-unit.md`, `blocks-are-still-words.md` — the two readings
  this bears on; it favours neither cleanly, which is the point.
- `lp_plaintext_register.py` — the author's own register, without which this comparison
  reads against prose and misses by more.
