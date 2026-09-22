---
type: hypothesis
---
# Short Units Are Written Joined, and the Boundary Sits Between Two Runes and Three

## Status

**Status**: the surviving explanation for the block-length anomalies, not a proof. Each
rule is scored against its own parametric null, so the comparison is fair and the errors
carry the 723-word reference.

## What is being explained

The body's block lengths differ from the author's own words in one place: **0.1588 at
length 2 against 0.2420**, z = −4.81. Register across 22 corpora, orthography,
section-to-section variation, line-break transcription and justification are all measured
and all fail (`block-lengths-have-a-hole-at-two.md`).

After that file's retraction, one mechanism survives. Joining about 40% of 2-rune units
to the unit before them is consistent with the length **marginal** at P = 0.79 and with
the **serial order** at 1.2 sigma — one mechanism, not two.

## Which lengths

A rule acting on length 2 but not length 1 would be strange. A rule acting on everything
short is ordinary: in runeglish, two runes or fewer is almost exactly the function-word
class — THE, TO, OF, IS, BE, WE, HE, A, I, AN, OR, DO.

`experiments/which_lengths_merge.py` scores each candidate against a null in which that
rule is true and both a 723-word reference and a 2,928-block body are drawn from it.
Comparing raw χ² across rules would be unfair, since they move the distribution by
different amounts.

| rule | best q | χ² | null, rule true | P |
|---|---|---|---|---|
| **absorb length 2** | 0.40 | 29.5 | 55.2 ± 34.1 | **0.83** |
| **absorb length 1 or 2** | 0.35 | 31.9 | 51.2 ± 29.7 | **0.70** |
| absorb length 1 | 0.25 | 181.7 | 64.2 ± 34.5 | 0.02 |
| absorb length 3 | 0.10 | 187.0 | 56.6 ± 29.2 | **0.00** |
| absorb length 3 or less | 0.15 | 101.9 | 52.6 ± 31.0 | 0.07 |

**The boundary sits between 2 and 3.** Absorbing two-rune units fits, absorbing one- or
two-rune units fits equally, absorbing three-rune units is dead, and absorbing only
one-rune units is rejected. The one- and two-rune versions cannot be separated: the
author's 723 words hold only 29 of length one.

## The boundary was found, not assumed

Every comparison in this file partitions the book at page 15, because that is where the
solved pages stop. A change-point scan removes the assumption
(`experiments/where_the_joining_starts.py`): fit one 2-rune rate before each possible
split and one after, take the likelihood ratio against a single rate, and price the
maximum against a surrogate null rather than a χ² table.

| scan over | max | null | P | best split |
|---|---|---|---|---|
| the whole book | **24.2** | 4.3 ± 2.3 | **0.0000** | p14: 0.243 → 0.160 |
| pages 14+, a second change? | 2.3 | 4.2 ± 2.4 | 0.77 | — |
| pages 0–13, an earlier one? | 8.0 | 2.5 ± 2.1 | 0.02 | p7: 0.201 → 0.294 |

**One change, at page 14**, which is where the partition had put it. The localisation is
soft — splits at 13, 14, 15, 17 and 18 all score within four units — so the boundary is
13–15 and no finer, but that still covers the solved/unsolved edge.

**Nothing changes after it** (P = 0.77), so the joining is a single switch rather than a
drift. Together with `the-body-is-one-uniform-text.md`, which reaches the same verdict
across sections by a different route, that is what **one different exemplar** looks like
and not what a scribe changing habits looks like. It is the first positive evidence for
reading 1 below, which had survived by elimination.

The page-7 flag is **not supported**: it does not track cipher kind (both halves hold
plaintext, monoalphabetic and Vigenère pages), it rests on pages 8–10 running high at
about 2σ each, and three scans were run. Recorded so it is not mistaken for a finding.

## The form of the rule: a habit, not a threshold

`which_lengths_merge.py` settled which unit gets absorbed (≤2 runes, not 3) but varied
only the absorbed unit's length — the *neighbour* was never part of any candidate rule.
That is what separates the two readings of who did this:

- a **habit**: a scribe running short words into a neighbour some of the time, with no
  rule about when. Merging is then independent of the neighbour, so merged units inherit
  the long tail of the word distribution.
- a **mechanical step**: plaintext prepared into units of bounded size before
  enciphering, merging a short word whenever the result still fits. The merged mass then
  piles up below the cap and the tail keeps the author's own shape.

`experiments/is_the_joining_mechanical.py`, each rule against its own parametric null:

| rule | fitted | χ² | null, rule true | P |
|---|---|---|---|---|
| forward, probabilistic | q = 0.35 | 18.6 | 24.2 ± 13.0 | 0.70 |
| backward, probabilistic | q = 0.40 | 17.5 | 22.0 ± 12.4 | 0.55 |
| **forward, capped at N** | **N = 4** | **112.4** | 30.0 ± 16.3 | **0.00** |
| to the shorter neighbour | q = 0.30 | 32.5 | 27.0 ± 16.0 | 0.30 |

**The deterministic size rule is dead.** Giving it a probability as well does not rescue
it: the fit drives N to 11, the top of the grid, where the cap never binds and the model
collapses back to the plain probabilistic one.

So the merge does not consult the neighbour's length — which a preparation step trimming
units to a bounded size would have to do. This is consistent with reading 1 (a different
hand or exemplar with an inconsistent habit) and is a second, independent argument
against the preparation reading that the cipher-gradient test already killed.

The direction stays undetermined: forward and backward fit equally well, and joining to
whichever neighbour is shorter survives weakly at P = 0.30. This experiment settles the
*kind* of rule, not its direction.

## The rate, and what it predicts

Within the null's own spread the rate is indistinguishable over **q ∈ [0.22, 0.50]**, best
0.40.

| q | plaintext words | joined to a neighbour |
|---|---|---|
| 0.22 | 3,097 | 169 |
| 0.40 | 3,242 | 314 |
| 0.50 | 3,331 | 403 |

**The body's plaintext held somewhere near 3,100 to 3,300 words, of which 170 to 400 were
written joined to their neighbour.** A solved body page tests that directly, and it is the
sharpest prediction this directory has about the plaintext.

## The part that is still strange

The front matter does not do it. Its 2-rune fraction is 0.2420, sitting at the median of
22 English registers, and it is the reference this whole comparison uses. So the
convention differs between the front matter and the body of the same book, written in the
same hand.

**Measured directly, September 2026** (`experiments/does_the_author_ever_join.py`).
The fraction is indirect evidence — a text could join and still land at the median. The
solved pages can be *read* instead: their ciphers preserve position, so the recorded
plaintext splices back into each page's own separator layout, and every separated unit
can be checked against a dictionary and against the author's own vocabulary. A unit
counts as joined only if it is **not** an English word and **does** split into two words
he writes separately elsewhere, each used twice or more. (A loose test is useless here:
it flags AND as AN+D and WITHIN as WITH+IN.)

| | |
|---|---|
| units on the 16 solved pages | 723 |
| units of ≤ 2 runes | 204 (28.2%) |
| **strict join candidates** | **0** |
| the same detector on his text joined at q = 0.40 | **45** |

Zero against forty-five. The detector finds about half the joins q = 0.40 would create,
so seeing none puts the author at **q < 0.015** by the rule of three — **24× below** the
body's fitted rate. His commonest short units are THE (43), TO (23), IS (22), A (19),
WE (18), OF (9), and he writes every one of them separately.

So "the front matter does not do it" is now a measurement rather than an inference, and
the gap between the two halves of the book is 24-fold rather than suggestive.

Three readings, none tested:

1. **The body's scribe or exemplar differs.** The book escalates its cipher page by page;
   it may escalate its orthography too.

   *Tested, weak support at best.* A different hand should show in more than word
   lengths. Two scribal features are in the transcription — line measure and which marks
   end a block — and both are confounded.

   **Line measure** has an encipherment confound that must be handled first: enciphered
   text has no word shapes to break on, so a scribe fills to a measure while plaintext
   breaks at sentence ends. Paragraph-final lines dropped:

   | group | lines | runes per line |
   |---|---|---|
   | front: plaintext | 49 | 18.59 ± **6.49** |
   | front: monoalphabetic | 46 | 19.52 ± **3.17** |
   | front: interrupted Vigenère | 37 | 20.32 ± **2.60** |
   | **the body** | 539 | **21.92 ± 2.32** |

   The spread tightens monotonically, which is the confound doing its work. Against the
   right comparison — the *enciphered* front matter — the body's lines are 1.6 runes
   longer, about 8%, at z = +6.02. Real, but far smaller than the raw front-against-body
   gap of +2.5 suggests, and an 8% line measure is not obviously a different hand.

   **Mark inventory cannot be read at all.** The front matter uses `.` and never a
   circled numeral; the body uses circled numerals and never `.`. Those are the same
   manuscript feature under two *transcription* conventions — the circled numeral records
   a dot count the `.` does not (`marks-are-not-one-glyph`). Comparing them measures the
   transcriber. What is comparable is the rate: 12.5% of front-matter blocks end in a dot
   mark against 5.7% in the body, which is ordinary for short instructional paragraphs
   against continuous text.
2. **The joining is part of the enciphering**, done when the plaintext was prepared rather
   than when it was composed. That would make it uniform across the body, which it is
   (χ² 3.9 on 8 df over nine sections), and absent from pages enciphered by simpler means,
   which it is.

   ***Tested and dead.*** If joining were preparation it should track how hard the page's
   cipher is. `experiments/joining_is_not_preparation.py` finds no gradient at all:

   | cipher | pages | words | fraction at 2 | z vs the body |
   |---|---|---|---|---|
   | plaintext (no cipher) | 6 | 231 | 0.2597 | −3.41 |
   | monoalphabetic | 5 | 255 | 0.2196 | −2.27 |
   | interrupted Vigenère | 4 | 212 | 0.2406 | −2.71 |
   | prime running key | 1 | 25 | 0.3200 | −1.72 |
   | **all enciphered pages** | | 492 | **0.2337** | **−3.70** |
   | **the body** | | 2,928 | **0.1588** | |

   All four groups sit between 0.22 and 0.32, within each other's errors and around the
   0.2422 median of twenty-two English registers. The AN END page — the hardest cipher
   the author ever solved — reads the *highest* of any group at 0.320, though on 25 words
   it cannot carry the argument alone.

   **Being enciphered is not what distinguishes the body.**
3. **The 2-rune deficit is not joining at all** but some other process that happens to
   leave the same marginal and the same serial order.

   *One candidate now measured, and rejected.* The obvious alternative is **depletion** —
   the body's plaintext simply carrying fewer function words, with nothing merged. Both
   models take one free parameter and start from the author's own 723 words
   (`does_the_author_ever_join.py`):

   | model | fitted | χ² over 13 length cells |
   |---|---|---|
   | **joining**: a ≤2-rune unit merges with the next | q = 0.35 | **20.2** |
   | **depletion**: a ≤2-rune unit is simply absent | d = 0.40 | **63.9** |

   Depletion must renormalise the whole distribution upward, so it over-predicts lengths
   3 and 4 (0.2702 and 0.1999 against the body's 0.2486 and 0.1771) and under-predicts
   everything past 7, where joining puts the merged mass. **The deficit at two really is
   a merge.** Reading 3 still stands as a possibility, but it now has one fewer candidate
   mechanism and no positive instance.

Reading 2 was the one that fitted the pattern of the book without needing a second hand.
It is now dead, so what survives is reading 1 — the body's scribe or exemplar differs —
or reading 3, that the deficit is not joining at all. Nothing else measured produces the
same marginal and the same serial order, which is what keeps reading 3 unattractive
rather than excluded; depletion is the one alternative tested and it fails by a factor
of three in χ².

**The tension is now sharp rather than suggestive.** The body's block lengths are the
author's own word lengths with about a third of the short units merged, and the author
merges at under 1.5%. Same book, same alphabet, same hand by every other measure. That
is the finding to explain, and it presses hard on whether the body's separators are the
same kind of object as the front matter's at all
(`separators-are-not-word-boundaries.md`).

## Falsification

- A solved body page settles it: count its words against its blocks. The prediction is
  about one joined pair every nine or ten blocks.
- If the joining is orthographic, a solved page shows compounds a reader would recognise
  — THEWORD, TOTHE. If it is a cipher-preparation step, the joins fall where the plaintext
  gives no reason for them.
- The rule must not act on three-rune units. If a solved page shows three-rune words
  joined, the boundary is wrong and the whole fit changes.
- The rate must be uniform. If a solved page shows a joining rate far outside
  [0.22, 0.50], the single-rate model fails.

## Scripts

- `experiments/which_lengths_merge.py`
- `experiments/reference_noise_in_length_tests.py` — the retraction that made this the
  surviving reading.
- `experiments/does_the_author_ever_join.py` — the direct bound on the author's own rate,
  and depletion tested against joining.
- `experiments/is_the_joining_mechanical.py` — the deterministic size rule rejected.
- `experiments/where_the_joining_starts.py` — the change-point scan that locates the
  boundary and finds no second change.

## Related

- `block-lengths-have-a-hole-at-two.md` — the anomaly and everything that does not
  explain it.
- `separators-are-the-cipher-unit.md`, `blocks-are-still-words.md` — the two readings of
  what a block is; this says blocks are words with the short ones joined.
