---
type: observation
---
# Observation: What Any Solution Must Satisfy — The Surviving Constraints in One Place

## Why this file exists

Sixty-odd files in this directory each exclude something. Nobody has written down what is
left, so every new idea gets re-tested against whichever constraints happen to be
remembered. This is the standing specification: a candidate cipher has to clear every row
below, and each row names the measurement and its scope rather than asserting a verdict.

It is a summary, not a new result. Nothing here is argued; everything is cited.

## A. The alphabet supply

| # | Constraint | Source | Scope |
|---|---|---|---|
| A1 | At least **949 distinct alphabets**, so two random positions collide in alphabet less than once in a thousand | `alphabet_count_bound.py` | From IoC alone — phase-independent, so no interrupter or preventer weakens it |
| A2 | No autonomous machine with alphabet period ≤ **6,478** | `rotor-machine-compact-state.md` | Lag scan; a 3-rotor 29³ odometer is above it |
| A3 | No **word-level state variable** fully indexes the alphabet — ~7,400 cells bound the sharing fraction at ≤ 4.5% | `word_state_sweep.py` | Excludes full indexing, not partial schemes |
| A4 | **Dot counts** do not clock it either | `dot-counts-do-not-drive-the-key.md` | Additive readings of the count only |

## B. The keystream, if it is additive

| # | Constraint | Source | Scope |
|---|---|---|---|
| B1 | Not drawn from **language**: a key with the LP plaintext's spectrum predicts unigram χ² 743 against the observed 26.4 | `running-key-of-language.md` | Additive keystreams; needs no alignment, so no interrupter blinds it |
| B2 | Spectrally flat where the plaintext is not: **\|K̂(j)\|² ≤ 0.0020** at the plaintext's six strongest frequencies | same | Binds only at those frequencies |
| B3 | Not any of **24 deterministic sequences**, at any of 200 start terms, 400 origins, 29 offsets, both senses — 11.1M alignments, best +9.24 against a true key's +13.77 | `running-key-math-sequence.md` | Additive over the standard rune order |
| B4 | No **repeating** key of any period ≤ 949 (IoC) or detectable depth | `no-running-key-depth.md` | — |
| B5 | Not an **integer-sequence keystream** over the standard rune order: 24 generators × 445 window positions × 29 offsets × both senses, running on or restarting, at 14,000 terms. Body best +2.6σ of its own scan against a planted control 2.6 points higher | `no-integer-keystream-anywhere.md` | Covers the prime running key the author uses on the very next page |
| B6 | The cipher **passes no rune through**. The author's interrupt convention is exactly "plaintext F" (12 for 12 over five keyed pages), and F in the body sits +0.53σ from flat, −8.9σ from its pass-through rate — the closest of all 29 | `the-body-passes-nothing-through.md` | Excludes the pass-through convention on any keystream; key-skipping that still enciphers the rune is untouched |

## C. The alphabet family

| # | Constraint | Source | Scope |
|---|---|---|---|
| C-0 | **g has five five-cycles** — it fixes 4 of the 29 runes and moves 25. The body's lag-2,3,4,6,7 profile filters a pool of order-5 permutations by 100×, and the survivors' cycle-count profile [0,0,2,22,36] matches a planted k=5 control | `d-profile-pins-g-to-five-cycles.md` | Key-free: the base cancels from a lag-k coincidence. Controls at true k = 1, 3, 5 all recover the truth |
| ~~C-1~~ | ~~**g's graph carries ≈ 0.026 of the plaintext bigram mass**~~ — **WITHDRAWN, no replacement.** The quantity is real and important, but the body's d1 is that rate after suppression, giving one equation in two unknowns, and nothing else correlates with it: lag 6 uses the same power of g and correlates at −0.13, and the d-profile filter's survivors have the same mass as the whole pool | `graph-mass-is-not-recoverable.md` | Was Read off the seam-to-within-word doublet ratio, which `one-parameter-fits-both-suppressions.md` now shows is not a constraint at all: a single φ ≈ 0.90 lands the seam and the within-block rate together and the ratio falls out at 1.07–1.35 around the corpus's 1.25. The derivation also assumed a preventer whose seam rate is g-free, which the cross-seam identity contradicts. Treat 0.026 as unsupported until re-derived |
| C0 | The base family is **A₂₉** — no algebraic structure to exploit | `base-family-is-the-symmetric-group.md`, narrowed by `sigma-is-even.md` | A₂₉ or S₂₉ from the classification; A₂₉ once σ is even, which is conditional on the DJU-BEI return |
| C1 | The per-word base family acts **2-transitively** — H₂, H₄ and H₇ subgroups of AGL(1,29) excluded by 1–2 orders of magnitude | `base-family-is-2-transitive.md` | H₁₄ survives but its extra invariant is scrambled by a non-affine g, so it carries nothing |
| C2 | No rune partition into **three or more blocks** (planted detection 100%), and every small block size 2-5 excluded by exhaustive enumeration at 67-100% power | `no-block-partition.md` | What remains is subsets that leak nothing measurable, which a solver would gain nothing from knowing |
| C3 | **order(σ) ≥ 307**, or ≥ 1,536 under a per-word phase reset | `key-local-channel-is-empty.md` | Assumes bases generated by iterating one σ. The clock cannot be settled here (`clock-convention-is-out-of-reach.md`); the return's rune gap favours continuous at 5 : 1, hence 307 |
| C4 | **σ is even**, so σ ∈ A₂₉ | `sigma-is-even.md` | Conditional on the DJU-BEI return; holds under four of six tokenizations and is vacuous under the other two |
| C5 | **σ moves at least 24 of the 29 runes** | `sigma-moves-almost-every-rune.md` | Planted controls at six fixed-point counts |
| C6 | σ's cycle type is one of **151** (continuous clock) or exactly **(11,7,5,4,2)** (reset) | `sigma-cycle-type-narrowed.md` | Parity × order, class-weighted: 4.3 or 11.6 bits |
| C7 | **g has at least two 5-cycles**, best fit four or five | `g-has-more-than-one-cycle.md` | Superseded by C-0, which measures five and is the row to quote |
| C8 | The base is **effectively distinct for every block** — pools below ~2,713 excluded | `base_pool_floor.py`, `dju-bei-needs-a-product-step.md` | Replaces the ~300 floor previously cited on trust. The 2,713 is from the pool floor, not from `two-rune-depth-no-base-reuse.md`, which this row used to cite |

## D. The clock and its units

| # | Constraint | Source | Scope |
|---|---|---|---|
| D1 | The **separators are the cipher's units**: the d5 echo is anchored to them at +4.17σ, and sliding every boundary destroys it | `separators-are-the-cipher-unit.md` | Inherits the echo's own ~3.7σ |
| D2 | Boundary-anchored structure exists **only at lags 4, 5 and 6** — where a letter step of order 5 puts it, with g's two diagonals moving in opposite directions | same | Σz² = 25.10 against a shifted max of 11.13 |
| D3 | The **doublet deficit is not boundary-anchored** — sliding boundaries leaves it at 0.193 ± 0.011 against the observed 0.182, z = −1.02, while the same slide destroys the d5 echo. It belongs to the emitted stream, not the block's alphabet schedule | same | Rules out deriving the deficit from the per-block relation; a preventer that inspects the *output* is untouched |
| D4 | No **emitting interrupter**: the author's own rule (every plaintext F passes through literally) predicts 205 interrupts and the flat unigrams allow at most 47, z = −4.43 | `interrupter-is-a-plaintext-rule.md` | A non-emitting clock perturbation leaves no unigram trace and is untouched |
| D14 | **One φ fits both suppressions**: at φ ≈ 0.90 the within-block rate reads −0.39σ and the seam +0.09σ, and the ratio falls out at 1.07–1.35 around the corpus's 1.25. the ratio constraint is dissolved, and C-1, which was read off it, is left unsupported | `one-parameter-fits-both-suppressions.md` | With no preventer the walk gives an elevated within-block rate and a chance seam; one parameter suppresses both |
| D5 | The **repeat suppression is context-free AND rune-blind**: its failures must be as likely at a seam as inside a word, and as likely for one rune as another. The 86 survivors use 28 of 29 runes at χ² 27.8 on 28 df | `seam-to-d1w-ratio-is-a-constraint.md`, `separators-are-the-cipher-unit.md`, `survivors-use-every-rune.md` | Rune-blindness refutes a fixed-τ substitution arithmetically: survivors force \|fix(τ)\| ≥ 28, suppression forces ≈ 5.6 |
| D8 | The suppression is **the cipher's, not the language's and not the author's usual**: his plaintext reads 0.0264 on the sixteen-page register, his monoalphabetic ciphertext inherits 0.0198, and his interrupted Vigenère returns to chance at 0.0300 (z −0.71). The body is 0.0066, 81% suppression, and 0.0079 at seams against his 0.0284 | `nothing-else-in-the-book-suppresses-repeats.md` | The Vigenère is the decisive control: a key that changes between adjacent positions destroys a plaintext doublet, so any residual deficit there would be the cipher's. There is none |
| D10 | The clock perturbation rate is **q ∈ [0.003, 0.262]**, point estimate 0.096, from the d5 shortfall of −0.0097 ± 0.0048 against prose | `d5-bounds-the-clock-perturbation.md` | Loose but not vacuous: a rule perturbing at 40% of positions is excluded. The dodge's 0.034 and a clean walk's 0 both fit. Channel exhausted |
| D12 | The base **changes at essentially every block edge**: cross-block lag-5 reads 0.0347 ± 0.0018 against 0.0363 for a stepping walk and 0.0595 for a fixed one, so at most 15% of edges can carry an unchanged base | `base_changes_every_block.py` | Closes any cipher unit larger than the block — phrase, line or page |
| D11 | The suppression is **strictly adjacent**: in a 4×4 cross-seam window only the adjacent cell is suppressed (z −16.3), the other fifteen sit at chance with \|z\| ≤ 1.6. No window rule, no memory beyond one rune | `the-preventer-is-strictly-adjacent.md` | Verified by an exact identity: the base cancels across a seam as well as inside a block |
| D9 | The suppression's strength is **φ ≈ 0.90**, the probability of acting on a would-be repeat, with [0.85, 0.95] inside 1σ and [0.80, 1.00] inside 2σ. The plain clock dodge is φ = 1 and is **not excluded** at +1.73σ | `how_strong_is_the_preventer.py` | CORRECTS the earlier "81% effective": that divided 86 by 447 = pairs/29, but the same walk with no preventer gives **515 ± 163** repeats, since a would-be repeat needs the plaintext bigram mass on g's graph and that exceeds 1/29. The key-to-key spread is the dominant term at every φ |
| D6 | Exactly **one state return** in the corpus, at the end of the body. A block-aligned whole-block repeat of 6+ runes has probability 0.00037, 1 in 2,693; any repeated 6-gram anywhere would be 1 in 8 | `dju-bei-is-more-surprising-than-recorded.md`, `dju-bei-stands-alone.md`, `dju-bei-ends-the-body.md` | No shorter returns at any length 3–8; the continuation test is impossible |
| D7 | The base is **chained, not redrawn**. Two counts must give one pool: `identical` gives 2,752 and the chain reading of `returns` gives 566 [153, 22,369], while the chainless reading gives 53 [28, 334] and is excluded. Independently, holding the corpus's 17 repeats fixed and shuffling only word order puts two of them adjacent once in 20,000 | `word-repeat-accounting.md`, `the-chain-shows-only-in-extension.md` | Rests on one repeated phrase, so quote it as a consistency argument. Every marginal battery cell is blind to the distinction |
| D13 | The base step is a **product**, not a bare σ — no divisor of the word gap survives the base-pool floor | `dju-bei-needs-a-product-step.md` | Needs no σ order floor and survives every tokenization |
| D15 | The body's blocks carry **none of English's sentence-edge profile**. The strictest comparison is like-for-like on one glyph class: the author's 87 four-dot marks give **+1.28 ± 0.28** runes of sentence-final lengthening, the body's 136 blocks before a ④ give **−0.32 ± 0.20** — **z = −4.65**. The joining model run forward predicts +0.75 ± 0.04. But the mark SPACING is over-dispersed for sentence ends (CV 0.972 ± 0.145 against 0.771 for English, 0.970 for random), so the marks may not fall at sentence ends at all | `sentences-do-not-end-long.md` | The two transcriptions prove `.` and ④ are one glyph class (46 clean swaps, totals identical) and pages 0–14 carry no ⑬/③/⑩, so the reference is pure four-dot, not a mixture. Within the body ④ carries the anomaly and ⑬ is an unresolved cell (25 blocks). Mechanical mark placement IS excluded at 6.7σ; the random-vs-English spacing evidence runs 3:1 to 33:1 and rests on Austen as a register proxy. Mark rate differs 2.3× between the sections (z = +5.02) |
| D16 | The cipher **does not restart at any structural boundary**. Blocks following a sentence mark coincide at 0.0338 against a length-matched null of 0.0348 ± 0.0011: **z = −0.96**, where a planted base reset reads +53 (with the clock) or +17 (without). Page breaks agree at z = −0.28 on 18 blocks | `the-cipher-does-not-restart.md` | Key-free: a shared base makes boundary-following blocks coincide at the plaintext rate. **Silent on a clock-only reset** (planted: −1.6), and that is structural — different bases coincide at chance whatever the phase, so no key-free channel can see it. The page-break cell excludes a full reset only (+4σ control). D12's 15% cap had left room for this |

## E. The plaintext side

| # | Constraint | Source | Scope |
|---|---|---|---|
| E1 | The **block lengths carry little language order** — excess G² per transition 0.0039 ± 0.0025 against the author's own plaintext. The reference's error was quoted as ±0.0101, which is surrogate spread only; a leave-one-page-out jackknife gives 0.0393 ± 0.0263 and the contrast is **1.35 σ**, not the strong result once recorded | `separators-are-not-word-boundaries.md`, `block-lengths-have-a-hole-at-two.md` | Per-page excesses run −0.20 to +0.42 over the sixteen solved pages. E3's hole at length 2 is unaffected: that is a two-sample comparison with both errors carried, at −4.81 |
| E2 | The lengths are **attached to nothing** — content, absolute position, line, previous length, all \|z\| < 1.3 | `block_length_independence.py` | Marginal dependence on those seven variables |
| E9 | The hole is explained by **joining short units**: absorbing 2-rune units at q ≈ 0.40 fits the marginal at P = 0.79 and the serial order at 1.2σ. The boundary is between 2 and 3 — absorbing 3-rune units is dead at P = 0.00. Predicts a plaintext of 3,100–3,300 words with 170–400 joined | `short-units-are-written-joined.md` | The front matter does not do it, which is unexplained |
| E3 | The length **marginal has a hole at 2**: 0.1588 against the author's own 0.2420 over 723 words from all sixteen solved pages, z = −4.33 against the between-page spread and −4.81 binomially. No one-parameter register tilt fits (χ² 84.0 on 10 df, residual −5.1 at length 2), the hole is uniform across the body's nine sections (χ² 3.9 on 8 df, none reaching 0.239), the author never spells a digraph apart (125 tokens, 0 split), separators are not being lost at line breaks (454 spanning blocks against a length-bias null of 459.1 +- 9.8, and the deficit survives in the 2,474 blocks no break touches at z = -3.65), and none of 22 English registers from Paradise Lost to the Kybalion reaches 0.159 — the lowest is 0.184 and the author's own pages sit at the median | `block-lengths-have-a-hole-at-two.md` | Absorbing a third of the 2-rune units closes it and nothing else does, but at that rate the serial excess is still 0.023 against the body's 0.004. Two effects, not one |
| ~~E8~~ | ~~Not produced by **merging**~~ — **RETRACTED**. The "five times too much order" compared the body to a 723-word reference held exact. Re-errored with a leave-one-page-out jackknife the gap is 1.2σ, and E9 replaces this row. Nulls and padding remain excluded | `reference_noise_in_length_tests.py` | The two rows contradicted each other for three ticks |
| E10 | Not restored by any **route or keyed columnar transposition** — 17 route rules and 46,232 keyed ones, the best failing cross-validation at +0.0011 on held-out pages | `separators-are-not-word-boundaries.md` | Per-page, whole blocks |
| E5 | Not a **vocabulary list** (type-weighted lengths are unmistakable) and not **sorted** (sorting creates order, eighty-fold) | same | |
| E6 | Not **interleaved** at any depth to 30 — the language peak would move, not vanish | `interleaving_depth.md` | |
| E7 | **Blocks are words**, on two independent lines. The lengths: the author's own words with short ones joined fit at P = 0.83 with one free parameter, while a discrete lognormal and a negative binomial are rejected at P = 0.00 with two. The d5 length-trend agrees but weakly, +0.0369 ± 0.0202, 1.73σ from cuts | `blocks-are-still-words.md`, `lengths_say_words_not_cuts.py` | WEAKENED: the row quoted two point estimates and no error. 806 blocks reach six runes and supply a lag-5 pair. Matters because E7 is what keeps crib programs valid | 1.55σ; rescues the crib programmes |

## F. Uniformity

| # | Constraint | Source | Scope |
|---|---|---|---|
| F3 | **One g runs through the body at 5 to 1**, and the filter is stable. A two-sample χ² between the halves' five d-values reads 6.9, against 5.5 ± 3.2 for a planted single g and 26.7 ± 19.6 for a g changing at the midpoint — P(≤ body) 0.67 against 0.13. The filter's score vector separately passes split-half at 0.800 against a planted 0.73–0.95 | `does_g_change_mid_book.py`, `one_g_through_the_body.py` | The SCORE-VECTOR version of this test is powerless and was withdrawn — it is dominated by shared plaintext structure, and a planted g-change still reads 0.535 ± 0.325 against 0.867 ± 0.164. Comparing the d-values directly is what works |
| F1 | The body is **one cipher**: over 9 sections χ² 5.0 and 4.1 on 8 df for doublets and d5, IoC sd 0.0070; over 55 pages χ² 62.0 on 54 df and 46.7 on 49 df, IoC sd 0.0385. The most extreme page is −4.20 sd on 66 runes | `the-body-is-one-cipher.md` | The test has power: the Parable, a plaintext page spliced in, surfaces at nIoC 1.819, **+7.06 sd** |
| F2 | **No window** from 100 runes up reads as plaintext or monoalphabetic — the body's best window is below a shuffled corpus's | `no-plaintext-window.md` | Coincidence only; a differently-keyed polyalphabetic stretch would not show |

## G. The information ceiling

| # | Constraint | Source |
|---|---|---|
| G1 | The measured channels reach **16 bits of 283** — g 6.2 of 79.7, σ under 10 of 101.8 and only under a right-acting step, base₀ **0 of 101.8**. C-0's cycle structure is worth 0.0024 bits, since 99.8% of order-5 permutations have five five-cycles | `the-bit-budget.md` | base₀ has no channel at all: every block draws its own alphabet, so nothing accumulates. Supersedes the earlier "13 bits on g and 0 on σ" |
| ~~G1b~~ | ~~The local channel is worth **13 bits on g and 0 on σ**~~, against an 80- and 103-bit search | `why-the-body-resists.md` |
| G2 | The key is nonetheless **over-determined 69×** by the ciphertext, so a unique answer exists | `unicity-distance.md` |
| G3 | A **battery cell count is not evidence** — a maximally wrong cipher lands 12 of 19; only d1w, d6w, doublet_gap_min, returns and seam discriminate | `battery-cell-counts-are-not-evidence.md` |
| G4 | **Eleven of the nineteen cells test the key, not the mechanism** — between-key spread exceeds within-key spread, and that includes `d1w` and `doublet_gap_min`. Score a model by the fraction of keys that make the corpus plausible, never by one key | `battery-cells-test-the-key.md` |
| G5 | On the four reachable cells the three preventer shapes are indistinguishable: median 2 of 4 for the substitution preventer and for the plain dodge, and only 4 cells of 19 separate the shapes at all | `battery-cells-test-the-key.md` |

## What that leaves

A cipher that: supplies a thousand or more alphabets from a state no visible variable
indexes; steps its letter alphabet with a permutation of order 5, re-anchored at each
scribal separator; changes base at those separators under a σ of order at least several
hundred; suppresses adjacent repeats by inspecting its own output rather than its
schedule; and segments a plaintext whose word order has left no trace in the block
lengths.

The largest unexplained facts were two. One is now reduced to a tension over a number.

**E1/E2/E3 — the block lengths are detached from everything.** They have the marginal of
running text, the serial order of nothing, and depend on no visible variable. Ten
mechanisms have been measured against it and all fail. E3 adds a second, independent
number to hit: the marginal is not the author's either, being short of 2-rune units by a
third, and the one rule that closes that hole leaves the serial excess six times too
high.

**D6 — the single state return, now partly explained.** One repeat, 1 in 2,700 by
chance, at the end of the body, with no shorter companions. The walk's own rate is
measured rather than argued: one return in 1,440 simulated corpora, which agrees with the
1-in-2,700 figure and withdraws the claim that no unfitted key could produce it.

Read conditionally rather than marginally the event stops being strange. From 17 identical
word pairs, a chained base pool of a few hundred produces at least one extension 19% of
the time; independent per-word draws produce one 0.7% of the time. So DJU-BEI is an
ordinary event for a chained cipher, and "no shorter companions" is what chance gives:
`word-repeat-accounting.md` shows 11.1 of the 17 shorter repeats are three-rune
coincidence, leaving an excess of 5.9 +- 3.4. With the floor subtracted and the LP's own
plaintext register used, `identical` implies a pool of 3,083 and the chain reading of
`returns` implies 795 with a 95% interval of [216, 31,442]. The two agree; the chainless
reading gives 63 with an interval of [33, 396] and does not. There is no pool tension.

The strongest form of the evidence needs no register at all. Shuffling the ORDER of the
corpus's own ciphertext words holds all seventeen repeats fixed and destroys only
adjacency: two of them land adjacent in the same order once in 20,000 shuffles.

Everything else in this table is a constraint. These two are the facts a solution has to
explain.

## Status

**Errors swept 2026-10-06.** Every row was checked for whether its claim carries an
error, an interval or a bound. Nineteen of fifty-one did not. Most were rows that compress
away a figure their source file does carry, and the load-bearing ones — D3, D6, F1 — now
quote it. One was a real gap and is corrected in place: **E7** stated a d5 length-trend of
+0.0369 against +0.0029 for cuts with no error on either, and bootstrapped over the 806
contributing blocks it is ±0.0202, so the separation is 1.73σ rather than decisive.

The rule this follows from four earlier instances: a headline of the form *observed
against reference* needs the error on both, and it is usually the size of the gap.

**Audited 2026-10-04.** Fifty rows, all ids now distinct — three pairs had collided
(D7, E3, E4) through many ticks of insertion. One live contradiction was found and
resolved: a row excluding **merging** sat beside one saying merging explains the block
lengths. The merging exclusion rested on the mis-errored reference retracted in
`reference_noise_in_length_tests.py` and is now struck through as E8. Stale figures were
refreshed where the plaintext register grew from 486 to 723 words (D7, D8, D4) and where
a later row supersedes an earlier one (C7 by C-0, B3 by B5, D4 by B6).

**Status**: summary. Every row is confirmed in its own file at the scope stated there;
this file adds no measurement and should be regenerated rather than trusted if it drifts
from those files.
