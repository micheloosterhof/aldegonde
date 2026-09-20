---
type: hypothesis
---
# Hypothesis: The Cipher is a Rotor Machine (a Compact-State Device)

## Claim

Michel's objection to `length-clocked-walk.md`: an evolving permutation table
is not how anyone would run an encryption algorithm. A real cipher has an
algebraic form you can compute — a device with bounded state, not a 29-entry
alphabet you update by hand at every word boundary. A rotor machine is the
standard candidate: compact state, alphabet changes every letter, no
bookkeeping beyond wheel positions.

"Compact" is given a specific and **narrower meaning than the objection
deserves**. To operate the cipher you must know the current alphabet `base_w`.
Every base lies in the coset `base_0·⟨g, σ⟩`, so `|⟨g, σ⟩|` bounds how many
settings there are. If that is small you can index it — a wheel with `|G|`
positions, a counter, a lookup table.

**What this file does NOT show is that no hand procedure exists**, and the
distinction matters. A large state space can still be trivially operable: an
LFSR has astronomical state and steps in one operation; Schneier's Solitaire
keeps a 54-card deck — a permutation, not a wheel position — and is designed
for hand use. The walk is arguably that kind of object: hold two 29-entry
wirings and compose one into the running alphabet at each word. Tedious, but a
procedure. So the results below bear on **"is there a wheel with N
positions"**, not on "is this runnable by hand at all", and the original
objection may well have an answer this file never tested — that it is a
deck-permutation cipher rather than a machine cipher.

## Status

**Status**: disproved for autonomous machines (three legs; the strong one is
the lag scan). The **wheel-indexable** form of the compact-state idea fails
under the walk's premises, for transitive state groups. Intransitive groups
occupy the middle ground: excluded at six or more blocks, **untestable at four
or fewer**. Nothing here settles whether a hand procedure of some other shape
exists.

## The main result: 29 is prime, so there is no middle-sized TRANSITIVE group

`experiments/compact_state_dichotomy.py`.

**Burnside**: a transitive permutation group of prime degree `p` is either
2-transitive or embeds in `AGL(1,p)`. For `p = 29` the 2-transitive groups
are only `A₂₉` and `S₂₉` — 29 is not `(q^d−1)/(q−1)` for any prime power `q`
(checked exhaustively for q ≤ 200, d ≤ 7) and no sporadic 2-transitive group
has degree 29. So a transitive `G ≤ S₂₉` satisfies

    |G| ≤ |AGL(1,29)| = 812     or     |G| ≥ |A₂₉| = 4.4 × 10³⁰

with **nothing in between — among transitive groups**. That qualifier is
load-bearing and was dropped in earlier drafts of this file: intransitive
groups can be any size at all, and they are the escape priced further down.
The walk needs an order-5 letter step; brute-forcing all 812 affine maps on 29
points, the element orders present are `{1, 2, 4, 7, 14, 28, 29}` — **no
order 5** — so the small branch cannot contain `g`.

Measured, not just argued: for random order-5 `g` (cycle type 5⁵1⁴) against a
random mixed σ, and against a 29-cycle σ (the "rotating mixed disk" device of
`sigma-power-step.md`), `|⟨g, σ⟩|` came out at 4.4×10³⁰ or 8.8×10³⁰ in every
trial, always transitive.

**Reading, at proper scope: there is no wheel to index.** No small set of
settings parameterises the alphabet. That is narrower than "no compact device
exists" (see the Claim's caveat about deck-permutation ciphers), and it rests
on **three** conditions, all of which must be stated together:

1. **period-5** — if `g` does not have order 5, `AGL(1,29)` reopens and
   812-state arithmetic machines become available;
2. **transitivity** of `⟨g, σ⟩` — intransitive groups occupy the middle;
3. **the walk being the right frame at all** — the whole state-space argument
   is derived from `base_w = base_0 ∘ prefix_w` and says nothing if the cipher
   is some other shape.

Condition 1 is a 2–3σ result, and the repo is **internally inconsistent** about
it: `d5-partial-alphabet-leak.md` calls order-5 `g` confirmed, while
`within-word-d5-coincidence.md` says in as many words that "period-5 confirmed"
overstates it. Do not treat it as settled in either direction.

This does invert an earlier speculation in this investigation — that a
multi-rotor machine "could supply hundreds of bases and a compact state". It
cannot, in the wheel sense.

## Rotor machines specifically: at most 29^k alphabets

`experiments/rotor_machine.py` implements one (odometer-stepping wheels
between static entry and output stages) with a round-trip self-test.

For a single stepping rotor `W` with entry `E`, writing `s = E⁻¹ρE`:

    A_t = A_0 · V^t · s^t          with V = a 29-cycle
    R_t = A_t⁻¹A_{t+1} = s^{−t} K s^{t}   for a fixed K

Both identities verified numerically over 60 steps on 3 random keys. Since
`ord(V) = ord(s) = 29`, **a single stepping rotor has exactly 29 alphabets and
period 29, for every wiring, entry and output choice.** Confirmed by direct
enumeration: k=1 gives 29 distinct alphabets, k=2 gives 841.

Consequences, using results already on the books:

- k=1 gives 29 base states against the **≥ ~300** that
  `two-rune-depth-no-base-reuse.md` requires (a 29-state schedule is excluded
  there at 10⁻¹²⁴). Dead immediately.
- The adjacent relation being a *rotation-conjugate* `s^{−t}Ks^t` means its
  diagonal is smeared over wheel positions. Averaged over `t` it equals the
  diagonal of `K` on the s-symmetrised plaintext table, which depends only on
  displacement classes, so the floor is `min_δ D(δ)` — the plain-Vigenère
  floor — attained only when `K` is a translation, which is precisely the
  degenerate 29-state case. **Derived, not numerically confirmed**; the state
  count already closes the case, so the floor was not separately computed.

## The DJU-BEI divisibility test

`experiments/rotor_period_closure.py`. An autonomous machine (state advances
without reading the text) has an eventually periodic state sequence, so it
returns to an earlier state **iff the elapsed step count is a multiple of the
period**. The corpus contains one exact state return.

The gap is measured from the corpus rather than taken from the documentation
(the script locates the unique word-initial repeated 6-gram and asserts the
result): **6,395 runes = 5 × 1279**, **1,449 words = 3²·7·23**. Both
occurrences word-initial 3+3, as recorded.

| clocking | period must divide | divisors | 29 a divisor? |
|---|---|---|---|
| letter | 6395 (invariant) | 1, 5, 1279, 6395 | **no** |
| word | 1449 (convention-dependent, see below) | 1, 3, 7, 9, 21, 23, 63, 69, 161, 207, 483, 1449 | no *at this tokenization only* |

**Tokenization check (Michel's question), `experiments/mark_clock_conventions.py`.**
The word gap depends on which visible marks advance the clock, so it was
audited rather than assumed. The apostrophe is **not** in
`c3301.WORD_BOUNDARY`, and all four apostrophes are rune-flanked on both sides
(strictly mid-word), so words flow across them. The double quote **is** in
`WORD_BOUNDARY`, but all fourteen sit adjacent to a mark and none is
rune-flanked, so it can never split a word — counting it changes nothing
(2,928 words either way). Consequences if the LP's own algorithm clocked
differently:

**The digits matter too (Michel's follow-up).** Sections 0-9 contain **367
ASCII digits**. Most are the two number grids and a lone literal `7`, none of
which touch runes. But **five are line-initial headers `1 2 3 4 5`** (rune
offsets 8805, 8944, 9035, 9133, 9229) that immediately precede a rune — and
**all five fall between the DJU-BEI occurrences**. Digits are in
`WORD_BOUNDARY`, and one of them (`3`, on a line whose predecessor ended in a
mid-word wrap `ᚠᛒ/`) currently **splits a word**: 2,928 words against 2,927
with digits transparent.

| convention | words | rune gap | word gap | small periods |
|---|---|---|---|---|
| repo default | 2,928 | 6,395 | 1,449 = 3²·7·23 | 3, 7, 9, 21, 23 |
| apostrophe also breaks | 2,932 | 6,395 | **1,451 (prime)** | none |
| quote does not break | 2,928 | 6,395 | 1,449 | 3, 7, 9, 21, 23 |
| sentence marks do not break | 2,785 | 6,395 | 1,378 = 2·13·53 | 2, 13, 26, 53 |
| digits transparent | 2,927 | 6,395 | 1,448 = 2³·181 | 2, 4, 8 |
| digits are word tokens | 3,205 | 6,395 | **1,709 (prime)** | none |
| digits tokens + apostrophe breaks | 3,209 | 6,395 | **1,711 = 29·59** | **29**, 59 |

The **rune gap is invariant at 6,395** under every convention (apostrophes,
quotes and digits are not runes), so the letter-clocked argument and the full
lag scan are untouched.

**Convention ruling (Michel, on reading the contexts).** The apostrophe does
**not** break a word; the digits `1`–`5` **do** — they are a numbered list of
five items. Both rulings coincide with the repo default, so the operative gap
is **1,449** and 29 does not divide it. The absent mark before item 3 is a
source-side omission by 3301, not a tokenizer fault — and it would not change
the word count either way, since a mark there would break the word exactly as
the digit does.

**On the 29·59 temptation.** The word gap 1,711 = 29·59 is arithmetically real
but does not survive scrutiny, on three counts:

1. It requires `apostrophe-breaks = True` **and** `digits = token`, i.e. both
   of the rulings above reversed.
2. Over the full 24-convention space there are 18 distinct gaps and **two** are
   divisible by 29 — 1,450 = 29·50 and 1,711 = 29·59. P(at least one) ≈ 0.47.
   Finding a 29-multiple is a coin flip, and 29·50 is arguably the prettier of
   the two, so there is not even a unique attractor. Both live in the
   apostrophe-breaks branch.
3. Divisibility is necessary, not sufficient. Measured under the exact 1,711
   tokenization, word-period-29 coincidence is **0.0319, z = −11.32** below the
   shared-alphabet level — the machine the arithmetic would license is
   directly falsified.

**The sharpened 29-disk test (`experiments/word_period_phase_ioc.py`).** Under
`g⁵ = id`, positions `j` and `j'` in words a period apart share an alphabet
whenever `j ≡ j' (mod 5)` — so every same-phase position pair can be pooled,
not just equal positions. That quadruples the sample.

| cell | rate | nIoC | z vs chance |
|---|---|---|---|
| **P=0 same-phase (positive control)** | 0.0481 | **1.396** | **+3.48** |
| P=29, first letters only (`j=j'=0`) | 0.0321 | 0.930 | −0.71 |
| P=29, all same-phase pairs (12,806) | 0.0333 | 0.965 | −0.75 |
| P=29, different-phase (control) | 0.0340 | 0.987 | −0.50 |

The P=0 row is the known within-word echo, reproduced exactly — so the harness
demonstrably detects a shared alphabet when one is present. Calibrating P=29
against **that measured value** rather than any theoretical full-leak figure
(no external reference, no register model, partial leak already included):
**z = −7.86**.

The first-letter cell is additionally **assumption-free about `g`**: `c[w][0] =
base_w(p[w][0])` with `g⁰ = id`, so it tests `base_w = base_{w+29}` alone. It
reads nIoC 0.930 where a shared base requires ~1.74.

Period scan 1–120: **29 ranks 91st of 120**; the strongest periods (89, 56, 62,
48) reach only z ≈ +2.3, and the scan maximum is 3.95 against ~3.09 expected
for noise. Nothing at 29.

**A 29-word disk is dead by direct measurement**, independently of DJU-BEI and
of every tokenization question. Scope: the scan needs ≥2,000 pairs, so it
covers P ≤ 120 — a two-disk 841-period machine is not reachable this way.

**The continuous-phase variant is dead too (`word_period_continuous_phase.py`).**
The test above assumes the letter phase RESETS per word. If it runs
continuously the alphabet is `B(w mod P) ∘ g^(i mod 5)` and two runes share it
only when `w ≡ w' (mod P)` **and** `i ≡ i' (mod 5)` — so the offset between
words P apart is the cumulative rune count mod 5, drifting from word to word.
A fixed-offset test looks in the wrong place. Bucketing every rune by
`(w mod 29, i mod 5)` instead:

| | pairs | rate | nIoC | z vs chance |
|---|---|---|---|---|
| **planted 29-disk, true period (control)** | 575,971 | 0.0863 | **2.502** | **+215.4** |
| planted, wrong period 23 | 725,809 | 0.0343 | 0.994 | −0.90 |
| **LP, bucketed (w mod 29, i mod 5)** | 575,971 | 0.0348 | **1.008** | +1.13 |
| LP, paired at the drifting offset | 11,280 | 0.0338 | 0.980 | −0.41 |
| LP, phase alone (`i mod 5`, no disk) | 16,779,316 | 0.0345 | 1.001 | +0.54 |

The planted control is found at z = +215 and a wrong period reads −0.90, so the
test is both powerful and specific. (The synthetic plaintext is more peaked
than runeglish — IoC ≈ 2.5 against ≈ 1.75 — so +215 overstates the real-world
power by roughly half; it remains overwhelming.) The LP sits at nIoC 1.008,
which is **z = −80.7** below a runeglish shared alphabet and −47.3 below even
the corpus's own measured echo strength. Period scan 2–120: 29 ranks 47th of
119 and the scan maximum |z| is 2.81, *below* the ~3.09 noise expectation.

The last row is a bonus exclusion: a continuous global 5-phase with no per-word
step would surface there on 16.8M pairs, and does not — independent
confirmation that the period-5 structure is word-scoped, not
absolute-position-scoped.

**Every phase-offset rule, swept (`word_phase_offset_sweep.py`).** A `g^(n_w)`
in front of each word is unobservable when `n_w` is free — it folds into
`base_w`. It bites only when `n_w` follows a rule, and the natural rules are
accumulations of a per-word increment: if word `i` advances the phase by
`(L_i + c)` then `n_w = (A_w + c·w) mod 5`. So the family is
`n_w = (a·A_w + b·w) mod 5`, 25 rules, crossed with every base period 2–120 —
**2,975 cells**.

Planted control (a=1, b=3, P=17) is localised **exactly**, at z = +789; the
runner-up is (1, 3, **34**), the correct harmonic of the true period, which is
the right behaviour rather than a miss.

On the LP, **scan max |z| = 3.45 against ~4.00 expected from noise** at that
many cells — the maximum is *below* the noise floor. Best cells reach only
nIoC 1.021–1.045 where a shared alphabet needs ~1.74. The named members at
P = 29:

| rule | reading | nIoC | z |
|---|---|---|---|
| a=0, b=0 | phase resets per word | 0.990 | −1.57 |
| a=1, b=0 | phase continuous | 1.008 | +1.13 |
| a=1, b=4 | the walk's own absorber | 1.000 | +0.01 |
| a=0, b=1 | one step per word | 0.995 | −0.73 |

Scope: the family is linear in `(A_w, w)`; rules depending on word content or
non-linear in the length sequence are not covered, the period ceiling is 120
(≥3,000 pairs), and the phase modulus is fixed at 5 by the period-5 premise.

**Standing caveat regardless.** The word-clocked divisibility argument is
convention-fragile and should not be leaned on; cite the measurement instead.

What is robust is the direct measurement. Word-period-29 coincidence, computed
under each tokenization:

| tokenization | rate | z vs shared-alphabet |
|---|---|---|
| repo default | 0.0320 | −11.31 |
| digits transparent | 0.0316 | −11.43 |
| digits tokens + apostrophe | 0.0319 | −11.32 |
| sentence marks do not break | 0.0352 | −9.92 |

Flat under all four. So word-clocked 29-state machines are excluded by
measurement regardless of which convention is right — which is the leg to
cite, not the arithmetic.

So no 29-position wheel machine can produce the return at all, and only
period 5 survives letter-clocked among small periods. Each surviving period
was then tested directly — a shared alphabet forces coincidence at the
plaintext rate (~0.060, calibrated by the repo's own controls at 0.0636
in-domain / 0.0611 lexicon) rather than 1/29:

| period | rate | z vs chance | z vs shared-alphabet |
|---|---|---|---|
| letter 5 | 0.0370 | +1.56 | **−11.0** |
| letter 1279 | 0.0374 | +1.74 | **−10.3** |
| letter 6395 | 0.0303 | −1.84 | **−10.1** |
| word 3…483 | 0.032–0.038 | −1.5…+1.7 | −8.5…−11.4 |

## The general scan: every autonomous period at once

Rather than arguing about which machine, scan every lag. A machine of period
`p` reuses its alphabet at lag `p`, whatever its construction.

- **Letter lags 1..6478**: max coincidence **0.0437** (lag 6002, itself the
  expected maximum of 6,478 tests). **No lag reaches 0.055.** Lag 29 (single
  rotor) 0.0349; lag 841 (two rotors) 0.0352.
- **Word periods 1..1464**: max **0.0430** at period 1449 — exactly the
  DJU-BEI word gap, and again the expected maximum over ~1,450 tests. None
  reach 0.055.

**Any autonomous machine with alphabet period ≤ 6478 is excluded**, rotor or
otherwise. The surviving corner is period > 6478 — e.g. a 3-rotor odometer at
29³ = 24,389, which never reuses an alphabet inside a 12,956-rune corpus —
but such a machine cannot produce DJU-BEI as a state return either, so it
must declare that repeat a coincidence (the repo's Monte Carlo puts that at
~1%).

## The weakest leg: word-boundary scope

`experiments/rotor_word_scope.py`. An autonomous machine's alphabet is a
function of absolute position only; it cannot see the separators. So its
distance-5 statistics must be indifferent to where word boundaries fall —
which is exactly the word-length permutation null.

Reproduces `within-word-d5-coincidence.md` independently as a harness check
(102/2073 within, 377/10878 cross). Against the boundary-blind null:
**102 observed vs 76.4 ± 7.9, z = +3.22, P = 0.0016**, and the effect is
specific to d5 across the d1–d7 controls.

This leg is only as strong as the d5 echo itself — ~3σ here, ~2.3σ
family-blind per `negative-control-battery.md`. Do not lean on it.

## The escape: intransitivity — narrowed, not closed

If `⟨g, σ⟩` is intransitive the runes split into blocks no base ever mixes,
`|G|` can be small, and the machine becomes hand-runnable again (five
5-position wheels plus a 4-position wheel is 5⁵×4 = 12,500 states, comfortably
above the ≥300 floor). Two costs, both measured:

**1. Unigram masses** (`experiments/intransitive_block_cost.py`). A block `B`
never exchanges mass with any other, so its ciphertext mass equals its
plaintext mass; the ciphertext is flat, so each block must carry `|B|/29`.
Four *singleton* blocks (g's four fixed points standing alone) are expensive:
the best possible choice of four still forces some rune ≥23.4% off, i.e. a
ciphertext count of 342 or 534 against 447 ± 20.8 (z ≈ −5.0), while the
observed counts span 399–492. **Four singletons excluded.** But letting the
four fixed points share one block of size 4 drops the worst mass error to
0.7% — masses alone do not close the escape.

**2. Block-bigram leak** (`experiments/block_bigram_leak.py`). Block-level
bigram mass passes through untouched: `P(c_i∈B, c_{i+1}∈B') = P(p_i∈B,
p_{i+1}∈B')`. So the plaintext's block-bigram dependence is deposited in the
ciphertext whatever the wiring. Calibrated against a **doublet-preserving**
surrogate (the raw χ² is inflated by the suppressed diagonal — the trap
`bigram-ioc.md` documents):

**Corrected (self-audit).** An earlier version of this table calibrated every
block shape against a single surrogate (80.2 ± 15.6). That was wrong: the
surrogate mean scales with the block COUNT (χ² has df = (nb−1)²), running from
~146 at 9 blocks to ~11 at 2. Each shape is now calibrated separately.

| block shape | blocks | surrogate mean | required leak χ² | honest z |
|---|---|---|---|---|
| [5,5,5,5,5,1,1,1,1] | 9 | 146.2 | 1048.2 | **+58.3** |
| [5,5,5,5,5,2,2] | 7 | 101.2 | 661.2 | **+34.3** |
| [5,5,5,5,5,4] | 6 | 78.4 | 326.3 | **+17.2** |
| [10,5,5,5,3,1] | 6 | 79.3 | 129.8 | +3.7 |
| [9,5,5,5,5] | 5 | 61.9 | 110.9 | +3.4 |
| [10,10,5,3,1] | 5 | 58.8 | 54.1 | −0.4 *(no power)* |
| [10,9,5,5] | 4 | 41.0 | 47.1 | +0.5 *(no power)* |
| [25,4] | 2 | 11.4 | 0.0 | −2.1 *(no power)* |

The observed ciphertext reads z = −0.62 against its own surrogate: no block
structure detectable.

So the reading changes. Shapes with **six or more blocks — the compact,
hand-runnable ones — are excluded**, up to z = +58. At five blocks it is
marginal (+3.4). At **four or fewer the test has no power at all**: the leak a
block machine would deposit is *smaller than the surrogate's own noise*, so a
null there is uninformative rather than confirming.

**The intransitive escape is closed for many-block shapes and untested for
few-block ones** — which is weaker than the earlier claim that specific shapes
"survive".

## Every word-level state variable, swept (`word_state_sweep.py`)

The tests above all index the base by WORD COUNT. That is one scheme among
many. The general principle needs no key: if the alphabet is a function of a
state `S` a solver can compute from visible data, two runes sharing `(S, phase)`
share an alphabet and coincide at the plaintext rate.

Thirteen state variables — word index, cumulative rune count, `A±w`, the word's
own length, the previous word's length, sentence index, position within
sentence / section / line, section index, line index, and a two-disk
`(w mod 29, A mod 29)` — each crossed with every modulus 2–60 and both phase
conventions. Best cells:

| scheme | best nIoC | z |
|---|---|---|
| `A+w` (disk turned L+1 per word) | 1.033 | +3.79 |
| `A−w` (the walk's own increment) | 1.022 | +3.07 |
| `w` (disk per word) | 1.018 | +2.81 |
| `A` (letter-clocked disk) | 1.014 | +2.34 |
| `(w, A)` two-disk, 841 states | 1.061 | +1.83 |
| `L` (base = the word's own length) | 1.000 | −0.10 |

**The argument is effect size, not significance.** A state variable that fully
determines the alphabet gives nIoC **1.74 by construction**. The best of ~7,400
cells reaches **1.033**, bounding the sharing fraction at **≤4.5%**.

Two closures worth naming: the **two-disk machine** (841 states) and the
**letter-clocked disk** (`A mod M`, a disk turned by the word length) were both
flagged earlier in this file as not reachable. They are reachable by bucketing,
and both are negative.

Relaxing the period-5 premise — letter-step order `q ∈ 1..8`, 7,367 cells —
leaves the picture unchanged. The purest cell, **q=1 (no letter step at all,
base only)**, reaches nIoC 1.005.

**What this does and does not exclude.** It excludes schemes where the state
*fully* determines the alphabet. Against **partial** schemes it has much less
power: anything contributing under ~5% is invisible. "No word-level state
variable exists" would be too strong; "none that fully indexes the alphabet"
is what was measured.

Null-quality note (`word_state_null_check.py`): the pooled-coincidence z values
use a binomial variance, and pairs sharing a rune are not independent. Checked
against doublet-preserving surrogates, the inflation is **0.94–1.04×** — so the
figures stand. The planted controls, re-run against register-realistic
plaintext (nIoC 1.750 rather than the over-peaked 7.9 used first), detect the
true cell at nIoC 1.736, **empirical z = +113** — an order of magnitude below
the +1052 first reported, and the quotable figure.

## Predictions

- Any surviving intransitive design commits to a specific partition of the 29
  runes into blocks. A decryption would expose it immediately (every plaintext
  rune shares a block with its ciphertext everywhere in the book), so this is
  a sharply falsifiable class rather than a vague one.
- If period-5 is ever retired, `AGL(1,29)` reopens and this whole file's main
  result lapses — an 812-state affine machine would then be compact, and
  hand-runnable.

## Scripts

- `experiments/rotor_machine.py` — the machine, round-trip self-test, the
  `A_t = A_0 V^t s^t` identity, state counts 29 / 841.
- `experiments/rotor_period_closure.py` — DJU-BEI gap measured and factorised,
  per-divisor tests, full letter-lag and word-period scans.
- `experiments/rotor_word_scope.py` — boundary-blind null, with the d1–d7
  control ladder.
- `experiments/compact_state_dichotomy.py` — Burnside arithmetic, brute-forced
  AGL(1,29) element orders, measured `|⟨g,σ⟩|`.
- `experiments/intransitive_block_cost.py` — block-mass cost of intransitivity.
- `experiments/block_bigram_leak.py` — the block-bigram leak, doublet-preserving
  calibration, and the sweep over all admissible block shapes.
- `experiments/mark_clock_conventions.py` — which marks advance the word clock,
  and the gap/divisor consequences of each convention.
- `experiments/word_period_phase_ioc.py` — 29-word disk, phase resetting per
  word, pooling all same-phase position pairs.
- `experiments/word_period_continuous_phase.py` — the continuous-phase variant,
  with a planted-machine control.
- `experiments/word_phase_offset_sweep.py` — every `n_w = (a·A_w + b·w) mod 5`
  phase-offset rule × every base period.
- `experiments/word_state_sweep.py` — thirteen word-level state variables ×
  modulus × phase convention × letter-step order.
- `experiments/word_state_null_check.py` — the self-audit: empirical surrogate
  nulls instead of binomial z, and register-realistic planted controls.

## Scope and caveats

**Framing.** "Compact" here means *wheel-indexable*. It does **not** mean
"runnable by hand" — see the Claim. Nothing in this file rules out a
deck-permutation procedure in the style of Solitaire, which is arguably what
the walk is.

**Conditions on the main result**, all three required: period-5, transitivity
of `⟨g, σ⟩`, and the walk being the right frame. Period-5 is 2–3σ and the repo
disagrees with itself about how firmly to state it.

**Power and its limits.**

- The planted controls are drawn from the **same families the tests were built
  to find**. They show the harness works on those shapes; they are not evidence
  that a differently-shaped machine would surface.
- The bucketing tests excludes full state-determination, not **partial**
  schemes (bound ~5%).
- The block-leak test discriminates only at roughly **five blocks or more**.
  Below four the required leak sits under the surrogate's own noise, so a null
  there is *uninformative*, not confirming. An earlier draft mis-read those
  cells as "surviving".
- Scan-maximum comparisons against `√(2 ln n)` assume independent cells. The
  cells are heavily correlated (nested moduli, overlapping states), so the true
  expectation is **lower** and observed maxima are marginally more notable than
  those comparisons suggest. The effect-size bound is the argument that does
  not depend on this.
- The lag scan covers periods ≤ 6478; the word-level sweeps mostly ≤ 60–120.

**Taken on trust, not verified here**: the ≥300-base floor of
`two-rune-depth-no-base-reuse.md` (which is what makes "29 alphabets is too
few" bite), and the repo's plaintext coincidence reference ~0.060.

**Cited, not proved here**: Burnside plus the CFSG classification of
2-transitive groups. The `AGL(1,29)` half is brute-forced.

**Register**: the block-leak test uses the repo's shipped runeglish bigram
table and carries the standing register caveat.

**Data bug found**: the shipped runeglish ngram tables spell J as U+1682 (`ᛂ`)
while `c3301.CICADA_ALPHABET` uses U+1684 (`ᛄ`). Any script indexing those
tables by the alphabet drops that rune silently — 0.305% of bigram mass.
Normalised here; ~20 scripts touch those tables and the rest are unaudited.

## Related

- `length-clocked-walk.md` — the model whose form this defends, on grounds the
  model itself never gave.
- `sigma-power-step.md` — the rotating-disk σ proposal, here shown to generate
  the full alternating group once combined with an order-5 `g`.
- `two-rune-depth-no-base-reuse.md` — the ≥300-base floor that kills a single
  rotor outright.
- `within-word-d5-coincidence.md` — the period-5 evidence the main result rests on.

## Verdict

**What is solid.** A single stepping rotor has at most 29 alphabets, for every
wiring and every stepping schedule — algebra, verified. That is far below the
≥300 the base-depth result requires. No autonomous alphabet period ≤ 6478
survives the lag scan. And across roughly 10,000 word-level indexing schemes,
nothing reaches more than ~4.5% of the effect a genuine state variable would
produce. Rotor machines and word-counter schemes are not the cipher.

**What is conditional.** Given period-5, transitivity, and the walk frame,
there is no wheel with a small number of settings that indexes the alphabet —
29 being prime leaves no middle-sized transitive group. Any of those three
conditions failing reopens it, and the first is a 2–3σ result the repo states
inconsistently.

**What this does not establish.** That the cipher has no hand procedure. The
argument is about wheel-indexability, and a permutation-carrying scheme in the
style of Solitaire is not addressed at all — the walk plausibly *is* one. The
original objection may therefore have a good answer that this file never
tested. Nor does anything here exclude partial state schemes, or block
structures with four or fewer blocks, where the tests have no power.

An earlier verdict here read "the walk is descriptive *because its premises
force it to be*". That overstates on two counts: it drops the transitivity and
frame conditions, and it conflates "no wheel" with "no procedure". The
defensible version is narrower — **no wheel, under three assumptions** — and
period-5 remains the most productive thing to attack, not because the rest is
settled but because it is the load-bearing premise.
