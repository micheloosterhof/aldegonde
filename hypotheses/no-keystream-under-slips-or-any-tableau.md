---
type: observation
---
# No Integer-Sequence Keystream, Under Key Slips or Under Any Tableau; No Period Smeared by Slips

## Why this needed doing

Rows B3 and B5 exclude integer-sequence keystreams with two stated limits: the alignment
may slip at most 200 times over the body (57-rune windows, sized on the AN END page's one
interrupt in 85 runes), and the arithmetic is additive over the standard rune order.
Row B4 scans single lags for a repeating key.

A doublet preventer that re-enciphers with the next key term breaks all three. A would-be
repeat arises once in 29 runes, so the key slips about 360 times; a 57-rune window is
slip-free one time in five; the running index leaves the 200 allowance half way through
the body; and a repeating key's coincidence peak is spread over a band of lags. A space
that consumes a key term slips 2,927 times. A mixed alphabet defeats subtraction. None of
these needs the order-5 letter step or σ: they are T1 questions
(`what-any-solution-must-satisfy.md`).

## 1. Under any pattern of key slips, standard rune order

`experiments/slip_tolerant_keystream.py`. The alignment is a Viterbi path: the key index
of rune i is base(i) + s, and s may stay, rise by one (a term skipped) or fall by one (the
key stalled). Emission is the log-likelihood ratio of the decrypted rune under the
author's plaintext unigrams. 34 generators (the 24 of `sequence_key_sweep`, plus
prime(prime(n)), prime(n)², n·prime(n), running sums of primes and of totients,
semiprimes, and the base-29 digits of π, e, the golden ratio and √2), 29 offsets, three
senses, three layouts (runs on, restarts per section, restarts per page) and three bases
(a rune eats a term; a space eats one too; each word starts one term after the last).

The null has to be matched to the generator: with a thousand free moves a path scores a
structured key differently from a random one whatever the text. prime(n)−1 reads about
150 nats above a random key on a **shuffled** body, which against a random-key null looks
like +5σ. Each generator is therefore scored on the body and on twelve surrogate bodies
(`c3301.low_doublet_null`: rune counts and doublet rate kept, order destroyed).

| | score, nats | same key on surrogate bodies | z |
|---|---|---|---|
| control: prime(n)−1 planted with the key-skipping dodge | 3,907 | −2,891 ± 28 | **+239** |
| control: the same with spaces eating key | 3,886 | −2,913 ± 15 | **+456** |
| the body, best of 306 cells (semiprimes, per page, spaces eat key) | | | +3.87, family P 0.41 |

The 306 body cells have mean +0.19 and sd 1.10. **No generator aligns under any pattern
of skips and stalls** within a slack of 900 terms running on, 400 per section and 150 per
page.

## 2. Under any tableau, fixed alignment

`experiments/any_tableau_keystream.py`. If C = T(P, K) for any fixed table whose row is
chosen by the key residue (Vigenère, Beaufort, any Quagmire with any keyed alphabets, any
Latin square, 29 unrelated alphabets), the runes enciphered under one residue are a
monoalphabetic sample of plaintext, so the 29 × 29 table of (cipher rune, key residue)
fails a chi-square test of independence. No alphabet enters. Three labels: K, and
C₋₁ ± K for one rune of ciphertext feedback; the same 34 generators, layouts and bases;
every start term to 2,000.

| | z of the best start |
|---|---|
| control: Quagmire IV, two random alphabets, prime(n)−1 from term 123 | **+247.6**, at start 123 |
| the control's wrong generator, best of 300 starts | +2.89 |
| the body, best of 918 cells | +8.79 |
| five surrogate bodies, best of 918 cells | +8.04 ± 1.27 (6.56 to 9.43) |

The body's best cells are all `n!` with the feedback label. That generator is zero after
28 terms, so the label is the previous rune alone and the cell measures the doublet
deficit; the surrogates carry the same deficit and read the same. **No generator selects
the body's alphabet under any tableau.** The alignment is fixed, so this covers a cipher
with no preventer, a tuned relation, and a preventer that inserts a null.

## 3. A repeating key smeared by slips

`experiments/smeared_period.py`. Coincidences summed over a window of consecutive lags,
maximised over the window's position, for widths 3 to 160, against 400 surrogate bodies.

| planted period, with the key-skipping dodge | best band | P over lags | |
|---|---|---|---|
| 100 | lags 481–490 (the fifth multiple) | 0.002 | found |
| 300 | lags 287–291 | 0.002 | found |
| 600 | lags 2,315–2,324 (the fourth multiple) | 0.005 | found |
| 1,000 | — | 0.122 | not found |
| 2,000 | lags 3,868–3,887 (the second multiple) | 0.035 | found |

The body's best band is lags 5,428–5,447 at z +4.15 (P 0.020 at that width); a surrogate
does as well over the seven widths 10% of the time. Its coincidences lean on runes
6,000–7,000 against 11,400–12,450 and exceed what one aligned key could supply, which is
what two stretches with skewed rune counts give. **No smeared period up to 600**; the
control is unreliable beyond.

## 4. A key that restarts per unit, under any tableau, key-skipping preventer included (11 November 2026)

`experiments/any_tableau_unit_heads.py`. Tests 1 and 2 leave one cell: a key-skipping
preventer with mixed alphabets. When the key restarts at a unit the cell is reachable
without the rune order and without a fixed alignment, because the first few dozen runes
of every unit are still aligned and there are many units. The (cipher rune, key residue)
table is taken over the heads of pages and sections (first 20, 36 and 60 runes) and over
whole lines, for the same 34 generators, three bases and start terms to 300.

| | z of the best start |
|---|---|
| control: Quagmire IV, prime(n)−1 restarting per page, key-skipping dodge; first 36 runes of each page | **+12.96**, at start 0 |
| the same control over whole pages at a fixed alignment | +7.55, at start 9 (the wrong start) |
| the body, best of 918 cells | +4.97 |
| eight surrogate bodies, best of 918 cells | +5.11 ± 0.38 (4.53 to 5.69) |

**No generator restarting at a page, a section or a line selects the body's alphabet.**

One trap, recorded because it produced a false positive on the first run. The first two
runes of every written line are left out of every table. Their distribution is set by
glyph width (`line-initial-bias.md`: wide runes such as EA, P, D begin lines, narrow ones
such as I and R do not), and any key whose early terms label line positions apart reads
that typesetting as dependence: `n!` on lines read +7.27 and the prime gaps +6.08 against
a surrogate maximum of 5.53 until those two runes were dropped.

## 5. A keyword alphabet under a running key with key slips (11 November 2026)

`experiments/keyed_alphabet_slips.py`. For a keyword alphabet the open cell is a sweep:
each alphabet is one alignment of test 1. 1,216 alphabets (the four constructions of
`keyword_exhaustion.alphabets` over the 316 words of 3301's own vocabulary), three
placements (keyed plaintext alphabet, keyed cipher alphabet, the same on both sides), two
bases, 29 offsets, three senses, skips and stalls, on the first 2,000 runes.

Twelve of the 34 generators cannot be the key under any additive tableau and are left
out: their residues are uneven, the cipher's rune counts are the plaintext's convolved
with the key's, and the body's counts are flat. They are n², the triangular numbers, the
prime gaps, n!, Fibonacci, Lucas, Pell, the divisor count, Möbius, Thue-Morse, the n-th
rune value and prime(n)². The rest fall into 19 classes under the 29 offsets.

The null is the sweep: all but at most one alphabet is wrong. The best alphabet of the
best cell is still the best of 138,624 tries on 2,000 runes, so the top cells are
re-scored on the whole body against surrogate bodies, where a true key keeps gaining
about 0.4 nats a rune.

| | |
|---|---|
| control: FROM (cyclic construction) on both sides under prime(n)−1 with the dodge | 597 against −412 ± 14 for 200 wrong alphabets, robust z **+73** |
| the body, best alphabet of each of 114 cells, on the opening | robust z mean +4.80, sd 1.07, max +8.16 (−374 against −438 ± 8) |
| the five best cells re-scored on the whole body | z −0.70, +1.64, +2.35, −0.57, −0.67 |

**No keyword alphabet from 3301's vocabulary aligns the body with a number-sequence key
under key slips.** The body's best opening score is −374 where the planted key reads
+597; none of the top cells extends.

## 6. One arbitrary mixed alphabet under a running key with key slips (11 November 2026)

`experiments/one_sided_alphabet_slips.py`. One unknown alphabet on either side, the
other side in the standard rune order:

- cipher side, P = a[C] ∓ K, a an arbitrary arrangement of the cipher runes;
- plain side, P = b[C ∓ K], b an arbitrary arrangement of the plaintext runes.

A free alphabet absorbs the reflection, so the two signs cover the Beaufort senses. The
alphabet is searched by swaps with the alignment of test 1 inside the loop (forward
slips, any start term within a slack of 150), on the first 2,000 runes, for the 19
generator classes and two bases of test 5.

With one side known the search can climb, because every rune of the alphabet that is
right pays on its own positions. It is a wait and not a descent: on a planted key it
sits at the noise level until it falls into the true alphabet, after a number of steps
that varies with the seed. Cooling schedules solved between a quarter and three
quarters of the cipher-side plants. Holding one temperature (8 nats: a swap out of a noise fit costs 5
to 15, out of the true alphabet about 60) for 85% of the steps solves nearly all of
them, and the controls measure the rate.

The null is the same generator on surrogate bodies. A first version used random keys
and read the key n at +8.9σ; the same key on surrogate bodies reads −324 ± 26 against
the body's −312.

| | cipher side | plain side |
|---|---|---|
| the planted alphabet's score (prime(n)−1, key-skipping dodge) | 611 | 614 |
| searches that find it | 11 of 12, all 29 runes exact | 12 of 12, at 630 |
| chance that both searches of a cell miss a true key | ≤ 0.020 | ≤ 0.005 |
| the same generators on surrogate bodies | −357, sd 14 | −403, sd 16 |
| the body's best search of 152 | −293 | −315 |

The 304 searches of the body have z mean −0.08, sd 1.09 and maximum +3.16 against their
own generators' surrogates, family P 0.21. **No number-sequence key with one arbitrary
mixed alphabet, on either side, aligns the body's opening under key slips.**

On the plain side the search ends above the planted alphabet's score with 13 of 29
runes in their planted places: unigrams cannot order plaintext runes of similar
frequency.

**Two arbitrary alphabets do not yield to this.** A position pays only when both of its
lookups are right, so the gain is quadratic in how much is right and a random start
sees nothing. On a planted Quagmire IV four searches of 800,000 steps stayed near −370
where the true key reads +730; fixing one rune by the rotation symmetry did not help;
and alternating an exact assignment of the alphabet with a re-alignment, the plan of
`docs/new-directions.md` 9.2, fails from a random start for one alphabet as well.

## What is left open

One cell, narrowed twice: a key-skipping preventer **and** an integer-sequence key that
**runs on** through the body **and** a tableau with two arbitrary alphabets, or one
arbitrary alphabet used on both sides (Quagmire III and IV with alphabets that are not
keyword alphabets from 3301's vocabulary). Restarting keys are closed by test 4,
keyword alphabets by test 5, one arbitrary alphabet by test 6.

Limits of tests 5 and 6. Both read the first 2,000 runes, so the key must enter within
the slack: about 70 terms go to the slips, which leaves start terms to about 80. Both
score the plaintext with the author's unigrams. Twelve of the 34 generators are set
aside by the flat rune counts and not searched.

Also open, as before: sequences outside the 34, and keys that are not sequences.

## Status

**Status**: confirmed (six negatives, each with a planted positive control).

## Related

- `no-integer-keystream-anywhere.md`, `running-key-math-sequence.md` — rows B5 and B3,
  which these extend.
- `no-periodicity.md`, `no-running-key-depth.md` — row B4.
- `the-body-composes-the-taught-devices.md` — the Quagmire with a numeric key proposed
  there is test 2's control, and is excluded for these generators at a fixed alignment.
