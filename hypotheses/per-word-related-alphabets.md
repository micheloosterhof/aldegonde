---
type: hypothesis
---
# Hypothesis: Per-Word Related-Alphabet Cipher (5 Alphabets, Bigram-Dodging Step)

## Claim

The unsolved Liber Primus is a per-word polyalphabetic cipher of **5 mixed
alphabets applied by position-in-word mod 5**, in which the 5 alphabets are
**related by a single fixed step permutation `g` of order 5**, and `base_word`
is advanced word-to-word by a **phase-absorbing free-group walk**:

    c[i]       = base_w( g^(j mod 5)( p[i] ) )              j = position in word
    base_{w+1} = base_w o g^((len_w - 1) mod 5) o sigma_k   (walk step)

This one structure reproduces the **entire** statistical fingerprint at once —
flat unigrams, flat columns, the lag-5 echo, the empty d2/d3/d4, and the doublet
suppression (within-word *and* across word seams) — with the doublet rates
**inherent to the alphabet relations** (`g`'s diagonal within words, `sigma`'s
diagonal at seams), no bolted-on rule, and no ciphertext feedback (so the echo
survives). See `experiments/phase_absorbing_walk.py`.

## Status

**Status**: plausible — superseded by `length-clocked-walk.md`, which
replaces this file's free per-word base with a deterministic length-clocked
walk and is the current statement of the model; read that file first.
(Candidate mechanism; reproduces every *hard* statistical observable in
simulation, not yet inverted on real ciphertext.)

First model in the investigation to jointly reproduce all hard observables —
including the two that killed earlier versions: **cross-word (seam) doublet
suppression** and **cross-word d5 at chance** — from one self-consistent
structure. It fits the statistics; it has not decrypted anything.

Soft observables are deliberately *not* fitted and are flagged as watch-items,
not constraints: the doublet dead-time (min gap 6; p ~ 0.06 vs memoryless), the
d1-delta residual (chi2 41.4, df27, p ~ 0.04), and the lag-1 marking hint
(LR ~ 4). Each is single-digit-sigma in a session that scanned dozens of
statistics; none is load-bearing.

## Mechanism

Within a word, the alphabet at position `j` is `A_{j mod 5} = base_w o g^{j mod
5}`, applied to `p[i]`. Between words, `base` is advanced by
`g^((len_w-1) mod 5) o sigma_k`: the `g`-power **absorbs the outgoing phase** so
that at *every* word boundary the temporally-adjacent alphabets are related by
the *same* fixed diagonal `sigma_k`, exactly as they are related by `g` inside a
word. `g` is order 5 (its 5-cycle closes safely, giving flat doublets by phase
and the sharp d5 echo, `g^5 = id`); `sigma_k` are free mixed permutations (an
unconstrained walk over the symmetric group). The walk step is a function of the
previous word's length, so decryption is progressive.

### Why the walk must be free, and phase-absorbing

Two structured walks were tried and both leak (`experiments/stay_slot_cipher.py`
and follow-ups): **powers of a single permutation** cap at <= 69 states on 29
symbols (ord | 1449 dead-end) and leave a period-5 Friedman spike (periodic IoC
1.22); the **centralizer of `g`** (steps commuting with `g`) preserves `g`'s
cycle structure and leaves periodic IoC 1.52 and a delta chi2 of 218. Any walk
that respects `g`'s structure leaks. The resolution is to make the *seam
relation* constant (via the phase-absorbing `g^a` factor) while the walk
generators `sigma_k` themselves are unstructured — that is the piece that makes
"boundary-blind doublets" and "flat/aperiodic" compatible.

## Why it fits each observable

- **Flat unigrams (IoC 1.00) and flat columns** — `base_word` is re-keyed per
  word, so every word-position column mixes different alphabets. (A *global*
  set of 5 alphabets leaves column 0 monoalphabetic at IoC ~1.8; per-word
  keying is required, and it must cover position 0 — the first-letter columns
  are observed flat.)
- **Lag-5 echo (d5 ~ 4.9%)** — positions `j` and `j+5` share a phase, hence the
  same alphabet, so a plaintext coincidence `p[j]=p[j+5]` passes through as
  `c[j]=c[j+5]`. The echo rate is therefore the *English* within-word d5
  coincidence rate, not a cipher artifact (verified: solved-plaintext d5 rate
  6.0%, ciphertext 4.9%, both well above the 3.45% chance floor).
- **Empty d2/d3/d4** — adjacent and near-adjacent positions use *different*
  alphabets, scrambling those coincidences to chance. This only comes out empty
  because the alphabets are *mixed*; a shift (Vigenere) would leave the
  plaintext-difference structure and the d5 delta would not be flat.
- **Doublet suppression, INHERENT and boundary-blind** — a within-word doublet
  is `c[i]=c[i-1] <=> p[i-1]=g(p[i])`, a **seam** doublet (last rune of a word,
  first of the next) is `p_prev = sigma_k(p)` after the phase-absorbing step, so
  BOTH are rare bigram-class events, not a rule. `g`'s diagonal is set to the
  observed within rate (0.0063), `sigma`'s to the observed seam rate (0.0079);
  the seam runs slightly hotter because one `sigma` must satisfy the diagonal at
  every phase at once. This is the piece the earlier per-word-independent version
  got wrong: with independent `base_word` the seam would sit at chance (~0.034),
  contradicting the observed 0.0079 -- the *chained* walk is what makes seams
  suppressed.
- **Suppression is one-hop (only between adjacent alphabets).** The coincidence
  condition at distance `d` is `p[i-d] = g^d(p[i])`, so each distance uses a
  different power of `g`. `g` is tuned to the peaked distance-1 bigrams, but
  `g^2` (phases 1&3), `g^3`, `g^4` are un-tuned permutations that land at chance:

  | distance | relation | model rate | min any perm | chance |
  |---|---|---|---|---|
  | 1 | g | 0.0013 | 0.0013 | 0.0345 |
  | 2 | g² | 0.037 | 0.0050 | 0.0345 |
  | 3 | g³ | 0.033 | 0.0102 | 0.0345 |
  | 4 | g⁴ | 0.034 | 0.0106 | 0.0345 |

  So the low doublets appear strictly between *touching* alphabets (1-2, 2-3, …)
  and not at range 2 (1-3) — exactly as observed. The "min any perm" column
  shows English *has* distance-2/3/4 structure a cipher could suppress; the fact
  that d2-4 sit at chance is positive evidence for a *single* `g` (tuned only for
  d1) rather than independent per-distance alphabets. At d=5 the phases coincide
  (`g^0`), so it is not a `g^d` relation at all but `p[i]=p[i+5]` — the echo.
- **Boundary-blind doublets** — `g` is global (same at every position and every
  word), so the doublet condition `p[i-1]=g(p[i])` and its rate are uniform
  across word and section boundaries, exactly as observed.
- **Kasiski / Friedman silent** — the period resets at each word and word
  lengths vary, so the within-word period-5 is desynchronised from global
  position; periodic-IoC and kappa show no period (only the weak lag-5 bump).
- **Not autokey** — the alphabet is position-based, not keyed by previous
  ciphertext, so positions `i` and `i+5` use the *same* key and the echo is
  preserved. A ciphertext-autokey term destroys the echo (verified: d5 collapses
  0.060 -> 0.037).

## The step permutation g, and how the period-5 closes

The doublet-minimising `g` (minimum-weight matching of the runeglish bigram
matrix) is an **arbitrary, data-driven permutation** — no shift, no affine, no
algebraic pattern (20 distinct `(g(x)-x) mod 29` values). Cycle structure
`[1, 1, 10, 17]`, order 170. Its two fixed points fall on U and Y — the runes
whose plaintext doublets (UU, YY) are rarest — and everywhere else it routes
onto near-zero bigrams. So the *optimal* `g` looks like nothing designed; a real
cipher `g` (producing 0.66%, not the 0.13% floor) would be a less-aggressive
permutation trading dodging for regularity.

The 5-cycle must **close**, and how it closes is settled by the data. Adjacent
positions always land on adjacent phases, so the five touching pairs form a
cycle 0-1-2-3-4-0; the wrap pair (phase 4->0) is a touching pair too. Two
possibilities:

- **Phase counter, `g^5 != identity`.** Only `g^0..g^4` applied, exponent resets
  at position 5. Then the wrap transition uses `g^{-4} != g`, so it is *not*
  doublet-suppressed -- it sits at chance, predicting a doublet spike at
  position-in-word `= 0 (mod 5)` and an overall rate `~ (1/5)(1/29)`.
- **Self-cycling, `g^5 = identity`.** The alphabet advances `A_j = A_{j-1} o g`
  and the cycle closes, so `g^{-4} = g` and *every* touching pair (including the
  wrap) suppresses via the same `g` -> uniform doublets across all phases.

**The data selects `g^5 = identity`.** Within-word doublets are flat across
position-in-word mod 5 (wrap bin: 6 observed vs ~30 if it were at chance;
Poisson p ~ 1e-8 against the counter version). So the cipher is the self-cycling
model. Consequences: **`g` has order exactly 5** (five 5-cycles + >= 4 forced
fixed points, since 29 is not divisible by 5, each fixed point a plaintext-doublet
bigram), and it has **no multiplicative/affine form** (GF(29)* has order 28,
`5 nmid 28`). The doublet-minimising order-170 `g` above is therefore *not* the
cipher's `g`; the real `g` is a mixed order-5 permutation.

## Evidence for

- **Generative reproduction.** `experiments/related_alphabet_cipher.py` runs
  order-2 Markov runeglish through the cipher and reproduces the fingerprint:

  | | uniIoC | d1 | d2 | d3 | d4 | d5 | cols |
  |--|--|--|--|--|--|--|--|
  | model | 1.00 | 0.0042 | 0.034 | 0.032 | 0.029 | 0.060 | 1.0 |
  | LP | 1.00 | 0.0066 | ~0.034 | ~0.034 | ~0.034 | 0.049 | flat |

- **The doublet floor forces mixed, not affine, alphabets.** The lowest doublet
  rate a substitution can reach on runeglish bigrams (a minimum-weight matching
  of the bigram matrix) is **0.13% for a general mixed permutation** but only
  **1.25% for an affine one**. The observed 0.66% is inside the mixed range and
  below the affine floor — so the doublet suppression *can* be inherent to a
  mixed alphabet relation but *cannot* be affine, and cannot be a plaintext
  bigram-class effect under an affine cipher.

## Evidence against / open questions

- **Not inverted.** Reproducing the statistics is necessary, not sufficient;
  the model has decrypted no text. Other mechanisms could fit the same marginals.
- **Exact doublet rate is g-dependent.** The minimum-weight `g` gives ~0.42% on
  Markov plaintext; the observed 0.66% corresponds to a slightly less aggressive
  `g`. The rate is a free consequence of `g`, not pinned.
- **The per-word `base` is high-entropy.** For the cipher to be decryptable, the
  per-word base cannot be free; it must be expanded from a small per-word seed.
  That seed / keystream is the unknown, and it has no detectable relation to
  word index, length, or neighbours (all tested flat).
- **The base keystream is finite-period, not one-time.** The DJU-BEI repeat
  (`repeated-phrase-dju-bei.md`) proves the base state recurs exactly. The two
  occurrences are **6395 = 5 x 1279 runes** apart (both prime) but **1449 words**
  apart (= 3^2 x 7 x 23, *not* a multiple of 5). So the recurrence is
  **rune-counted, not word-counted** — a `word_index mod 5` term is excluded
  (1449 mod 5 = 4 would misalign it), while a rune-level period of 5.1279 is
  consistent. This is a *different* 5 from the within-word phase-5. The
  recurrence is momentary, though: word-aligned cross-coincidence around the
  phrase is ~0.042 (chance 0.034), not the ~0.06 of a sustained depth, so it
  gives a period clue rather than a depth crib.
- The single-rune doublet marker of `doublet-marker-rune-ea.md` is *not* revived:
  a fixed-rune marker needs a ciphertext autokey (disproved, and it breaks the
  echo). This model recasts the doublet trigger as a **rare plaintext
  bigram-class** relation `p[i-1]=g(p[i])`, which is inherent and feedback-free.

## Predictions / how to attack

- `g` should be **recoverable from the doublet structure**: the ~86 doublet
  positions mark plaintext pairs satisfying `p[i-1]=g(p[i])`, so their
  distribution constrains `g` (a fixed 29-symbol permutation).
- With `g` fixed, decryption reduces to recovering `base_word` per word; if
  `base_word` is seed-generated the cipher is breakable, if effectively random
  it is a one-time key.
- A correct `g` should make the doublet-marked plaintext bigrams consistent and
  English-rare; a wrong `g` should not.

## Scripts

- `experiments/phase_absorbing_walk.py` — the **final model**: order-5 `g` +
  phase-absorbing free-group walk; reproduces every hard observable including
  seam doublets and cross-word d5.
- `experiments/stay_slot_cipher.py` — head-to-head battery harness; documents the
  failed structured walks (powers-of-h, centralizer) that forced the free walk.
- `experiments/related_alphabet_cipher.py` — the within-word core plus the
  affine-vs-mixed doublet-floor computation.
- `experiments/period5_quagmire_sim.py` — the per-word-reset building block:
  shows global 5-alphabet keying fails (columns 1.8, first letters spike) and
  per-word keying is required (columns 1.0).

## Related

- `five-block-boundary.md` — the `(1/5)(1/29)` doublet framing and the
  "consecutive-distinct" rule; this hypothesis replaces that rule with an
  inherent alphabet relation and keeps the parameter-free spirit.
- `within-word-d5-coincidence.md`, `lag5-digraph-structure.md`,
  `docs/lag5-phenomenon.md` — the lag-5 echo, here explained as a period-5
  same-alphabet plaintext-coincidence leak.
- `doublet-marker-rune-ea.md`, `ciphertext-autokey.md`,
  `beaufort-autokey-ea.md` — the falsified single-rune / autokey doublet
  mechanism; this recasts the trigger as a feedback-free bigram-class relation.
- `autokey-plus-substitution.md`, `affine-autokey.md`, the quagmire notes —
  neighbouring polyalphabetic families.
- `rune-s-lag5-echo.md` — the S-at-d5 finding (11 vs 1.75, Bonferroni-clean,
  p=2.4e-6) is UNEXPLAINED by this model: the echo value is
  `base_word`-dependent, so no rune should dominate structurally. Either the
  S-dominance is an n=11 fluke or it is evidence against a value-randomizing
  per-word base. Unresolved — see that file; do not treat it as retired.

## Verdict

Predecessor of the current candidate model (`length-clocked-walk.md`
supersedes this file). A per-word cipher of 5 mixed alphabets
related by a fixed bigram-dodging step permutation reproduces the complete
observed fingerprint — flat unigrams and columns, the lag-5 echo, the empty
d2-4, and an inherent, boundary-blind doublet suppression — from one structure,
with no ciphertext feedback and no appended rule. The doublet suppression, the
corpus's defining anomaly, falls out of the alphabet relation rather than being
imposed. It remains unproven as the actual cipher until `g` is recovered from
the doublet structure and a per-word inversion is attempted.
