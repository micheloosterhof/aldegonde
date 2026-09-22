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
| 1 | 0.0401 | 0.0246 | 0.0338 |
| **2** | **0.2420** | **0.2841** | **0.1588** |
| 3 | 0.2393 | 0.1962 | 0.2480 |
| 4 | 0.1770 | 0.1440 | 0.1755 |
| mean | 3.98 | 4.23 | 4.42 |

**The body has a third fewer 2-rune blocks than the author has 2-letter words.** A
two-sample chi2 over all twelve cells is 39.5 on 11 df, and the standardised residual at
length 2 is -2.1 while no other cell exceeds 1.1 -- the misfit is one length.

The plaintext sample is **723 words from all sixteen solved pages**, not the 486 that
`lp_plaintext_register.corpus()` returns. That function drops the Vigenere and
running-key pages because their interrupts break the rune-to-rune position map, which is
right for runes and wrong for lengths: an interrupt is a rune the key skips, not a rune
inserted or removed, so those pages' word lengths are their plaintext's exactly. Using
them lifts the sample by 49%, and every length statistic here is measured on it.

## The register objection, priced

The eleven solved pages are front matter and the body is not, so a register difference
is the first thing to rule out. Two ways, both in
`experiments/block_length_shape.py`.

**The between-page spread.** The 2-rune fraction varies from 0.111 to 0.367 across the
sixteen solved pages, giving a standard error on the mean of 0.0192, and only 3 of the
16 pages fall below the body's 0.159. That is the right
denominator, because it prices exactly the difference between one page's register and
another's.

    LP plaintext 0.242,  body 0.159,  z = -4.33   (binomial z = -4.81)

**A one-parameter register tilt.** Reweight either reference by `exp(λ · length)` — a
shift toward longer or shorter words — and fit λ to the body:

| reference | best λ | χ² on 10 df | residual at length 2 |
|---|---|---|---|
| LP plaintext | +0.084 | 84.0 | **−5.1** |
| prose | +0.023 | 266.5 | **−11.5** |

Neither fits, and in both the largest residual is at length 2 with lengths 1 and 3 on
the other side. **A register cannot be wordier at one length only.**

## What closes the hole

Absorbing units into their neighbour, one parameter, fitted:

| absorbed length | best rate | χ² | residual at length 2 |
|---|---|---|---|
| 1 | 0.30 | 188.0 | −9.2 |
| **2** | **0.35** | **42.9** | **−0.2** |
| 3 | 0.10 | 181.0 | −9.2 |

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
**They are two effects, not one.** *(Withdrawn — see the retraction below. Both numbers
in this section carry the wrong error.)*

This also corrects the standing shorthand that merging is "refuted by the length
sequence". It is not refuted — it removes three quarters of the serial excess, which is
far more than anything else tried. It is insufficient.

## No English register reaches the body's rate

The standing objection is that the body is 58 pages of unknown content while the solved
pages are front matter, so the two could simply be different kinds of writing. That is
testable, because the 2-rune class in runeglish is exactly the top function words — THE
is one rune plus E — and its frequency is what varies between registers.

`experiments/register_range.py` measures it across every English text in the cache:
scripture, verse, philosophy, mysticism and novels.

| register | words | fraction at 2 | mean | χ² vs body |
|---|---|---|---|---|
| Paradise Lost | 66,368 | **0.1840** | 4.22 | 163.3 |
| The Divine Comedy | 89,225 | 0.2145 | 4.04 | 268.7 |
| Zarathustra | 90,942 | 0.2249 | 4.16 | 118.9 |
| **the author's solved pages** | **723** | **0.2420** | **3.98** | — |
| Dhammapada | 11,806 | 0.2408 | 4.11 | 171.6 |
| Meditations | 59,731 | 0.2437 | 4.03 | 206.2 |
| Beowulf | 32,271 | 0.2510 | **4.40** | 215.6 |
| King James Bible | 634,721 | 0.2549 | 3.81 | 407.7 |
| Tao Teh King | 10,705 | 0.2746 | 4.11 | 264.7 |
| The Kybalion | 29,473 | **0.2950** | 4.40 | 442.3 |
| **the body** | **2,928** | **0.1588** | **4.42** | — |

Twenty-two registers, range 0.1840 to 0.2950, median 0.2422.

- **The author's own pages sit at the 50th percentile.** The front matter is ordinary
  English, so it is not a strange baseline.
- **Not one register reaches the body's 0.1588.** The lowest is Paradise Lost, blank
  verse — the register most likely to shed function words — and it is still 0.184 with a
  residual of −3.2 at length 2.
- The best-fitting register of all twenty-two gives χ² 105.2 on 11 df. Every one fails.

**And matching the mean does not match the shape.** Beowulf has mean word length 4.40
against the body's 4.42 — the same to two decimals — and a 2-rune fraction of 0.2510
against 0.1588. So the body is not simply a wordier register; a register can have
exactly the body's mean and none of its hole.

## Nor is it separators lost at line breaks

The body is laid out in 594 lines of 21.8 runes, and a separator at a line break is the
easiest kind to lose in transcription. Losing one merges two blocks, which is the shape
of the deficit exactly.

The right null is length bias: a long block covers more of a line, so it contains a break
more often whatever the scribe did. Laying the body's own block lengths over its own line
lengths in random order, 500 times:

| | observed | length-bias null | z |
|---|---|---|---|
| blocks spanning a break | 454 | 459.1 ± 9.8 | −0.52 |
| their mean length | 5.753 | 5.981 ± 0.095 | **−2.39** |

Losing separators at breaks would make spanning blocks both commoner and longer. They
are neither — the count is exactly as predicted and the mean is if anything short.

And the deficit survives in the blocks the breaks never touched: 2,474 of them, fraction
at length 2 **0.1774 ± 0.0077** against the author's 0.2420 ± 0.0159, z = −3.65. (That
subset over-samples short blocks, which is why its rate sits above the body's own
0.1588.)

## Do the rubricated titles escape it? A lead at 1.25 sigma

Every contrast above is between the body and something outside it — the author's other
pages, twenty-two English registers, the body's own sections. The seventeen rubricated
titles are *inside* it: same pages, same hand, marked in red, with their extents recorded
in `rubricated_titles.json`.

`experiments/titles_may_escape_the_hole.py`, 52 title blocks:

| comparison | fraction at 2 | z |
|---|---|---|
| **the titles** | **0.231 ± 0.058** | |
| against the rest of the body | 0.158 | +1.25 |
| against the author's own plaintext | 0.242 | **−0.19** |

**The titles are indistinguishable from ordinary plaintext and sit 1.25σ from the body
around them.** On 52 blocks that is a lead, not a finding, and two things qualify it.

The whole-distribution χ² is 9.7 on 9 df — nothing. Only the length-2 cell carries the
signal, which is the cell one would look at first.

And titles are short phrases, which carry *fewer* function words than running text. So the
register confound points the opposite way to the observation: it should push the titles'
2-rune rate **down**, and instead they read higher than the body. That makes the lead more
interesting rather than less, but it is still a confound with no control available.

Reaching three sigma would need about **302 title blocks against the 52 that exist** —
roughly six times as many rubricated titles as have been identified. That is a
transcription task, not an analysis one.

## Nor is it justification

The remaining scribal story is that the scribe joined a short word to its neighbour to
make a 21.8-rune line come out even. That would leave a positional signature, and
assigning each block to the line its first rune falls in, the signature looks
overwhelming: blocks last to start in a line are a rune and a half longer than the rest
and have half the 2-rune fraction, at **z = −8.07**.

It is an artifact. The block last to *start* in a line is the block that *spans* the
break — 454 of the 590 — and long blocks span more often, which
`line_layout_and_the_hole.py` already measured against a length-bias null (454 observed,
459.1 ± 9.8 predicted).

Conditioning on it removes the effect entirely:

| group | blocks | mean | fraction at 2 | z vs rest |
|---|---|---|---|---|
| first in line | 592 | 4.380 | 0.1689 | −0.63 |
| middle | 1,746 | 4.093 | 0.1844 | +1.44 |
| last in line | 136 | 4.449 | 0.1250 | −1.88 |

Among blocks no break touches, no position differs from the rest by two sigma. **The hole
is not positional within the line.**

This is the third length-bias trap in the same statistic. Any subset defined by where a
block sits relative to a break over-samples long blocks by construction, and the
uncorrected number is always dramatic.

## A test that looks decisive and is not

Recorded so it is not repeated. If separators were placed by the line rather than by the
text, the count per line would be more regular, and less coupled to how many runes the
line holds, than a random arrangement of the same blocks. The body reads sd z ≈ −4.3 and
correlation z ≈ −7.5, which looks like exactly that.

Two controls kill it.

| text | lines | sd z | corr z |
|---|---|---|---|
| body | 594 | −4.25 | −7.53 |
| front matter, plaintext | 55 | +9.30 | **−21.86** |
| front matter, enciphered | 92 | −3.2 | −0.6 |
| ordinary prose, same layout | ~590 | −2.9 to −5.4 | +1.4 to +2.7 |

Prose laid out the same way reads the same sd z as the body, and the book's own
**plaintext** front matter reads a correlation z three times more extreme.

The fault is the null. It holds the line lengths fixed and shuffles the blocks, but a
scribe chooses where to break a line to fit what is on it, so line length and content are
not independent. The null breaks that link as well as the hypothesis and manufactures a
coupling the real text never had.

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

## RETRACTION: both numbers were errored against a reference held exact

The two results above — that absorption fits the marginal poorly, and that it leaves the
serial order three sigma short — are both computed against the 723-word reference as
though it had no sampling error. It has a great deal.
`experiments/reference_noise_in_length_tests.py` re-errors them.

**The marginal does not reject absorption.** Under a parametric null in which absorption
is true and both a 723-word reference and a 2,928-block body are drawn from it, the
fitted χ² runs **53.6 ± 30.9** (10th percentile 22.1, 90th 93.4). The observed 29.5 sits
at **P = 0.79**. The 42.9 recorded above as a poor fit was a χ² with only the body's
counts in the denominator.

**The serial gap is one sigma, not three.** The ±0.0058 quoted above is the spread over
merge realisations with the sixteen pages held fixed. Those pages differ enormously —
per-page excesses run from **−0.20 to +0.42** — so the right error is a leave-one-page-out
jackknife. A bootstrap cannot be used: it duplicates pages, and a duplicated page adds
serial structure by construction.

| q | reference | jackknife se | z against the body |
|---|---|---|---|
| 0.00 | 0.0393 | **0.0263** | **−1.35** |
| 0.40 | 0.0264 | **0.0179** | **−1.25** |

**So "two effects, not one" is withdrawn.** Absorbing about 40% of 2-rune units into the
preceding word is consistent with the marginal at P = 0.79 and with the serial order at
1.2 sigma. One mechanism accounts for both, within the precision a 723-word reference
allows.

**And constraint E1 is weaker than recorded.** It contrasts the body's 0.0039 ± 0.0025
with the author's 0.0397 ± 0.0101, where the ±0.0101 is the surrogate spread and carries
no page sampling. With the jackknife the author's figure is 0.0393 ± 0.0263 and the
contrast is **1.35 sigma**, not the strong result the specification records.

What survives untouched is the hole at length 2 itself: that is a distribution comparison
between 2,928 blocks and 723 words, with both samples' errors in the two-sample z from
the start, and it reads −4.81.

## Consequences

- Row E1 should read that the lengths have the marginal of running text *with a hole at
  length 2*, not the marginal of the author's running text.
- Any mechanism proposed for the block lengths now has two numbers to hit, not one: a
  34% deficit at length 2, and a serial excess of 0.004 against a plaintext 0.039.
- The eleven mechanisms measured against E1 were all tested against the serial statistic
  alone. The marginal is a second, independent handle, and it is the sharper of the two
  because it needs no surrogate — it is a distribution comparison.
- Because the hole is uniform across the body, the author's spelling is consistent, and
  no English register of twenty-two reaches the rate, the ordinary explanations are out.
  What remains is a rule applied uniformly to the body and not to the front matter.

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

## Targeted merging is no better than random merging

If the absorbed units were chosen rather than picked at random — every THE, say — the
merges would remove the most predictable transitions and might kill more serial
structure per merge. Measured on the eleven rune-recoverable pages, where word identity
is available:

| rule | merges | excess G² per pair |
|---|---|---|
| none | 0 | 0.0790 ± 0.0010 |
| every THE | 24 (4.9%) | 0.0572 ± 0.0010 |
| random 2-rune units, matched count | 23 (4.7%) | 0.0629 ± 0.0121 |
| every short function word | 68 (14.0%) | 0.0545 ± 0.0011 |
| every 2-rune word | 101 (20.8%) | 0.0292 ± 0.0016 |
| **the body** | | **0.0040 ± 0.0025** |

Targeting THE beats matched random merging by 0.006 against a spread of 0.012, so the
difference is not established. And absorbing **every** 2-rune word — which destroys the
marginal — still leaves seven times the body's serial excess.

These numbers are on 486 words and are not comparable with the 723-word figures
elsewhere in this file; only the rows within the table compare.

## A scope check on the enlarged sample

Adding the five interrupted pages assumes their lengths are their plaintext's. Split by
group:

| group | pages | words | fraction at 2 | excess G² per pair |
|---|---|---|---|---|
| plaintext | 6 | 231 | 0.2597 | 0.0293 ± 0.0265 |
| monoalphabetic | 5 | 255 | 0.2196 | 0.1130 ± 0.0294 |
| **interrupted Vigenère / running key** | 5 | 237 | **0.2489** | **0.0294 ± 0.0320** |

**The interrupted pages match the plaintext pages on both statistics**, which is the
assumption confirmed. The outlier is the monoalphabetic group at 0.1130, 2.1 sigma above
the plaintext group and the reason the eleven-page serial reference reads 0.079 while
the sixteen-page one reads 0.039. That heterogeneity is why the serial reference should
be quoted as 0.039 ± 0.010 and not as a fixed number; the body's 0.0040 ± 0.0025 is
still about three and a half sigma below it.

The 2-rune fraction is stable across all three groups and far above the body in each.

## What no standard distribution explains

If the lengths were generated by the cipher rather than by language they might follow a
clean parametric law. Four families, fitted by chi2:

| family | body (n=2,928) | author's words (n=723) | prose (n=2,928) |
|---|---|---|---|
| geometric | 1024.3 | 166.9 | 903.2 |
| shifted Poisson | 433.3 | 58.6 | 1252.6 |
| negative binomial | 172.4 | 41.8 | 455.2 |
| discrete lognormal | **71.8** | **13.8** | 243.6 |

Discrete lognormal is best everywhere and fits nothing well. Scaled to equal sample size
the body's 71.8 becomes about 12 on 11 df, which is what the author's words give, so
**this test cannot separate them either.** It rules out only that the body's lengths are
a simple generated law, which they are not.

## Falsification

- The 723-word plaintext sample is the weak point. If the 2-rune fraction is a property
  of front matter, any newly solved body page must show 0.159 and not 0.239. That is a
  direct prediction on the next page solved.
- If the body's plaintext spells TH apart, a solved body page will show it. The front
  matter's 125-for-125 consistency predicts it will not.
- The register range is 22 texts, all literary or scriptural. If some English register
  genuinely sits at 0.159 — a technical manual, a word list, heavily nominal prose — the
  objection revives. The prediction is that it will also have a mean far from 4.42,
  since the hole is a shape and not a shift.
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
