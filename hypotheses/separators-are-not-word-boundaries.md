---
type: hypothesis
---
# Hypothesis: The Body's Separators Mark Cipher Blocks, Not Plaintext Words

## The measurement, on data no cipher touches

Every cipher still entertained here is position-preserving. The ciphertext has the same
runes in the same places, so the **sequence of word lengths passes through untouched** —
whatever the body's plaintext is, its word-length sequence is already readable.

English word lengths are strongly serially dependent: short function words alternate with
long content words. The statistic is the G² of the length-transition table, bucketed at
6+, against a surrogate that shuffles the same lengths within the same page or section.
Reported per pair, so corpora of different sizes compare directly.

| corpus | words | excess G² per pair |
|---|---|---|
| prose, six Gutenberg books carried into runeglish | 120,000 | 0.0484 ± 0.0160 |
| the LP's own solved plaintext | 723 | 0.0397 ± 0.0101 |
| **the unsolved body** | **2,928** | **0.0039 ± 0.0025** |

The two references agree with each other — one register-matched and noisy, one
register-mismatched and tight — and the body sits an order of magnitude below both, on
four times the plaintext's data. Against the LP's own plaintext that is **z = +3.46**;
against prose, **z = +2.75**.

The body's own excess, 0.0039 ± 0.0025, is consistent with **zero**.

## Why the significance is 3σ and not 15σ

A naive comparison — the body's G² of 36.3 against what the plaintext rate predicts,
138.5, divided by the body's own surrogate spread — reads 15σ. That is wrong. The
reference is measured on 723 words and carries ±0.0101 of its own, which dominates the
comparison. Propagating it gives 3.5σ. The same error class as
`scan-maxima-need-surrogate-nulls`: the uncertainty that matters is the one in the
quantity being compared against.

## The merge family, swept properly, cannot fit both observables

`separator-loss-is-selective.md` proposes that separators were lost, merging adjacent
words. Merging prose at the rate that matches the body's mean word length:

| merge p | mean length | 2-rune share | excess per pair |
|---|---|---|---|
| 0.00 | 4.03 | 0.228 | 0.0337 |
| **0.08** | **4.38** | 0.209 | 0.0237 |
| 0.16 | 4.81 | 0.191 | 0.0201 |
| **body** | **4.42** | **0.159** | **0.0039** |

Random merging fails on both axes at once. But the version that could work is merging
only SHORT words, because that removes exactly the short-long alternation the structure
is made of. Swept over the merge probability q:

| rule | mean | 2-rune share | excess per pair |
|---|---|---|---|
| prose untouched | 4.11 | 0.227 | 0.0341 |
| **merge length ≤ 2, q = 0.3** | **4.43** | **0.164** | 0.0199 |
| merge length ≤ 2, q = 0.5 | 4.66 | 0.121 | 0.0115 |
| merge length ≤ 2, q = 0.7 | 4.89 | 0.071 | 0.0062 |
| merge length ≤ 2, q = 0.9 | 5.12 | 0.024 | 0.0043 |
| merge length ≤ 3, q = 0.5 | 5.16 | 0.117 | 0.0074 |
| **body** | **4.42** | **0.159** | **0.0039 ± 0.0025** |

**The two observables demand different rules.** At q = 0.3 the histogram matches almost
exactly — mean 4.43 against 4.42, 2-rune share 0.164 against 0.159 — and the sequence
still carries 0.0199 where the body has 0.0039, a gap of **5.7σ**. Reaching the body's
sequence needs q = 0.9, which drops the 2-rune share to 0.024 and the mean to 5.12.

No rule in the family fits both. This is the quantitative version of the refutation:
the length histogram and the length order cannot be produced by one merge process.

## It is not a segmentation artifact

The obvious alternative is that the tokenizer is wrong — that the structure is there and
the wrong marks are being treated as breaks. Sweeping sixteen conventions, crossing line
wraps, multi-dot marks, page marks and quotes:

| | excess per pair |
|---|---|
| all sixteen conventions | **−0.0011 to +0.0037** |
| best of the sixteen (the repo's own) | 0.0037 ± 0.0026 |
| the LP's own plaintext | 0.0397 ± 0.0101 |
| prose | 0.0484 ± 0.0160 |

**Every convention gives essentially zero.** No segmentation of this text recovers
language-like word-length order.

One convention is worth naming because it fails instructively. Breaking words at line
wraps brings the mean closest to language — 4.07 against the plaintext's 3.99 — and
drives the order *further* to zero (−0.0006). It also makes the histogram fit worse
(0.0861 per word against the plaintext, versus 0.0668 for the repo default), and it is
known to be wrong from the solved pages, where words demonstrably flow across wraps. So
the one convention that improves the mean improves nothing else.

## Encipherment is not what removes the structure

The strongest control available is the author's own enciphered pages, where the word
boundaries are known to be real words because the plaintext is recovered. Measured
exactly like the body:

| group | words | excess per pair |
|---|---|---|
| plaintext pages (6) | 231 | 0.0281 ± 0.0270 |
| monoalphabetic ciphertext (5) | 255 | 0.1111 ± 0.0297 |
| interrupted-Vigenère ciphertext (5) | 237 | 0.0261 ± 0.0322 |
| **unsolved body** | **2,928** | **0.0039 ± 0.0025** |

Each group is noisy at ~240 words, but all three are positive and the **enciphered** ones
carry the structure as plainly as the plaintext ones — as they must, since a
position-preserving cipher cannot touch a word length. So the body's absence is not an
artifact of encipherment, of the tokenizer, or of the statistic.

## The lengths depend on nothing measurable

Both surviving readings predict the block lengths are attached to nothing. Mutual
information against a label-shuffling null, 2,973 blocks:

| block length against | z |
|---|---|
| first rune of the block | +0.24 |
| last rune of the block | −1.22 |
| absolute rune index mod 5 | +0.23 |
| absolute rune index mod 29 | +0.71 |
| line index mod 4 | −0.47 |
| position in line, bucketed | +1.26 |
| the previous block's length | +0.04 |

Nothing. If the lengths were set by the enciphering process they would depend on
position; if by the page layout, on the line; if they still carried plaintext words, on
each other. They are i.i.d. draws from a language-shaped distribution, attached to
nothing — which is what makes them hard to explain and hard to exploit.

## The reference holds under a jackknife

The comparison's load-bearing half is the 723-word plaintext reference, pooled from 16
pages, one of which (`WELCOME WELCOME PILGRIM…`) is conspicuously repetitive. Dropping
one page at a time:

| | excess per pair |
|---|---|
| all 16 pages | 0.0388 ± 0.0103 |
| leave-one-out range | 0.0291 to 0.0609 |
| jackknife sd | 0.0072 |

No page drives it. Every leave-one-out estimate stays far above the body's 0.0039, and
the jackknife spread is *smaller* than the surrogate-based standard error, so the quoted
±0.0103 is conservative.

## Three perturbation families, all failing the same way

Merging is not the only way to lengthen words without reordering them. Nulls and padding
are the classical alternatives, and they behave identically:

| model | mean | 2-rune | excess per pair | histogram vs body |
|---|---|---|---|---|
| prose, untouched | 4.11 | 0.227 | 0.0342 | 0.0448 |
| nulls at rate 0.05 | 4.32 | 0.208 | 0.0287 | 0.0272 |
| **nulls at rate 0.10** | 4.52 | 0.187 | **0.0237** | **0.0240** |
| nulls at rate 0.15 | 4.73 | 0.169 | 0.0230 | 0.0388 |
| pad 0.5 runes per word | 4.61 | 0.132 | 0.0221 | 0.0334 |
| **body** | **4.42** | **0.159** | **0.0039** | — |

The rate that best matches the histogram leaves **0.0237** of order where the body has
0.0039 — the same five-fold failure as the merge family.

That is now three independent families — merge, selective merge, nulls and padding — each
swept across its parameter range, and none reaching the body's order level while keeping
its histogram. **Every mechanism that preserves word identity leaves most of the order
intact.** The order is destroyed, not diluted.

## But the blocks are not memoryless either

A block process that starts a new block with fixed probability per rune would give
**geometric** lengths. The body's are not geometric, and not by a little: G² per word
against a matched-mean geometric is 0.4110 for the body, against 0.4144 for the LP's own
plaintext and 0.4356 for prose. **The body is exactly as far from memoryless as language
is** — mode at 3, near-absent at 1.

So whatever placed these boundaries produced a language-shaped histogram in a random
order. The histograms do still differ from language, and the two references show how much
of that is register:

| G² per word | |
|---|---|
| body vs LP plaintext | 0.0668 |
| body vs prose | 0.0656 |
| **LP plaintext vs prose** | **0.0173** |

The references agree with each other four times better than either agrees with the body.

## The hypothesis

If the separators were placed by a process independent of the plaintext's words, the
resulting lengths would be serially independent and the transition structure would be
zero — which is what the body shows. So:

> **The body's separators delimit cipher blocks, not plaintext words.**

This is not in tension with the word-anchored results; it explains them. It predicts,
and is consistent with:

- **Word-anchored key state.** The blocks *are* the key's unit, so a base change at each
  separator is exactly right. The measured 1.01× leak across boundaries follows.
- **The within-block d5 echo.** The letter phase is scoped to the block because the block
  is the cipher's unit.
- **The 2-rune deficit at z = −10.** Block lengths follow the cipher's rule, not English
  word statistics, so there is no reason for them to match a plaintext length histogram.
- **The mean length gap**, 4.42 against the plaintext's 4.04, for the same reason.
- **Why the front matter differs.** There the separators *are* words — those pages are
  plaintext or monoalphabetic, and their boundaries have to be readable.

## What would falsify it

1. **Block lengths should be i.i.d.** Measured: excess per pair 0.0039 ± 0.0025,
   consistent with zero. Any serial dependence found at higher order kills it.
2. **~~The length distribution should be the cipher's, not language's.~~** Tested and
   **failed**: the histogram is as far from geometric as language is. A memoryless block
   process is out. Two readings survive and are the live ones:
   - **an i.i.d.-length source** — a list rather than prose, whose word lengths carry no
     order because there is no sentence order to carry;
   - **~~block-level reordering~~** — the lengths are the plaintext's, permuted.
     **Narrowed sharply**: a reader has to be able to undo a reordering, so it is a rule,
     not a shuffle, and the classical rules are few. Un-permuting each page under 17 route
     transpositions — reverse, columnar 2–12, rail 2–5 — restores nothing: the best rule
     reaches 0.0034 ± 0.0022 against the language level of 0.0397. The search has full
     power: planting a columnar-7 transposition on prose drops it from 0.0842 to 0.0162,
     and the search recovers the exact rule at 0.0842 with the runner-up at 0.0162. So no
     per-page route transposition of blocks is what happened. A key-driven permutation
     survives, at the cost of the hand-runnability that motivated the reading.

     **Narrowed again**: a columnar transposition is normally KEYED — the columns are
     read out in an order a keyword sets, not left to right — so inverting with the
     identity order, as the route search did, is wrong for every keyed variant and the
     family was not covered. Enumerating it: for c columns there are c! read-out orders,
     and c = 2 to 8 gives **46,232 rules**. The body's best reaches **0.0156**, against a
     structureless null whose search maximum is **0.0140** and a language level of 0.0397.
     The search finds a planted keyed columnar (6 columns, order (3,0,5,1,4,2)) at rank 1
     of 5,912. So keyed columnar transposition is excluded too.

   The list reading is now the simpler of the two.
3. **The plaintext word boundaries are then absent from the text entirely**, so a
   correct decryption would produce unbroken runeglish. Any solution that recovers
   space-delimited words at these separators refutes this outright.
4. **Register.** The prose reference is novels and the LP reference is didactic front
   matter. A register whose word lengths are genuinely serially independent would
   explain the measurement without any of this — but no natural language register is,
   and the two references here bracket the question from both sides.
5. **Segmentation.** Tested and survived: all sixteen tokenization conventions give
   essentially zero, so a wrong tokenizer is not the explanation.

## The separators are still the cipher's units

A fair objection to all of this is that the separators might not be cipher structure at
all. `separators-are-the-cipher-unit.md` answers it: sliding every boundary by a fixed
number of runes, keeping the length sequence unchanged, destroys the d5 echo. The real
positions give 1.427x chance where twelve decorrelated offsets give 0.998 +- 0.103, so
the echo sits +4.17 sigma above that null and is anchored to exactly these marks.

So the author's segmentation is real and deliberate, and is not the plaintext's word
segmentation. Both halves of that sentence are now measured.

## Status

**Status**: plausible, and consequential if true. The measurement is confirmed at 3σ
against two independent references; the interpretation is one hypothesis among others.
`experiments/word_length_sequence.py`, `--merge` for the merge control.

## Related

- `separator-loss-is-selective.md` — the merge explanation this refutes.
- `two-rune-deficit.md` — the anomaly this would explain.
- `length-clocked-walk.md`, `pure-quagmire-word-restart.md` — models that take the
  separator as the key's unit, which this supports while renaming what it delimits.
- `lp-plaintext-register.md` — the register-matched reference.
