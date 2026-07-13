# Hypothesis: Per-Word Related-Alphabet Cipher (5 Alphabets, Bigram-Dodging Step)

## Claim

The unsolved Liber Primus is a per-word polyalphabetic cipher of **5 mixed
alphabets applied by position-in-word mod 5**, in which the 5 alphabets are
**related by a single fixed step permutation `g`**:

    A_phi = base_word o g^phi        (phi = position_in_word mod 5)

`base_word` is re-keyed per word. This one structure reproduces the **entire**
statistical fingerprint of the corpus at once — flat unigrams, flat columns, the
lag-5 echo, the empty d2/d3/d4, and the doublet suppression — with the doublet
rate **inherent to the alphabet relation**, not a bolted-on rule, and with no
ciphertext feedback (so the echo survives).

## Status

**Status**: plausible (candidate mechanism; reproduces the full fingerprint in
simulation, not yet inverted on real ciphertext)

First model in the investigation to jointly reproduce all five observables from
one self-consistent structure with nothing contradictory and nothing appended.
It fits the statistics; it has not decrypted anything.

## Mechanism

Each word is enciphered independently. Within a word, the alphabet at position
`j` is `A_{j mod 5} = base_word o g^{j mod 5}`, applied to the plaintext rune:
`c[j] = base_word(g^{j mod 5}(p[j]))`. `base_word` is a fresh mixed permutation
per word (the per-word key); `g` is a single global mixed permutation (the
cipher's fixed structural parameter).

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
- **Doublet suppression, INHERENT** — a doublet is
  `c[i]=c[i-1] <=> base(g^phi(p[i])) = base(g^{phi-1}(p[i-1])) <=> p[i-1]=g(p[i])`.
  Choosing `g` so that consecutive outputs land on **rare English bigrams**
  makes doublets inherently rare. It is not a separate rule; it is a property of
  how the alphabets relate.
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

Two ways the 5-cycle can close, which differ observably:

- **Phase counter (modelled here).** The alphabet index is
  `position_in_word mod 5`, so only `g^0..g^4` are ever applied and the exponent
  resets at position 5. `g` may be *any* permutation; **`g^5 != identity`** (the
  optimal `g` has order 170). This gives the lower doublet floor.
- **Self-cycling.** If the alphabet instead advances `A_j = A_{j-1} o g`, closing
  the period needs **`g^5 = identity`**, i.e. `g` of order 5. On 29 runes that
  forces >= 4 fixed points (29 not divisible by 5) -- four forced plaintext-doublet
  bigrams -- and GF(29)* has order 28 with `5 nmid 28`, so no *multiplicative*
  order-5 `g` exists. A clean self-cycling `g` is therefore strongly constrained
  and cannot be affine/multiplicative.

Which of the two the cipher uses is a genuine fork with distinct fixed-point /
doublet-bigram signatures, and is open.

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

- `experiments/related_alphabet_cipher.py` — the full model reproduction plus
  the affine-vs-mixed doublet-floor computation.
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
- `rune-s-lag5-echo.md` — the S-at-d5 finding, now judged an n=11 artifact rather
  than a mechanism feature (the echo value is `base_word`-dependent, so no rune
  should dominate structurally).

## Verdict

Strongest candidate mechanism to date. A per-word cipher of 5 mixed alphabets
related by a fixed bigram-dodging step permutation reproduces the complete
observed fingerprint — flat unigrams and columns, the lag-5 echo, the empty
d2-4, and an inherent, boundary-blind doublet suppression — from one structure,
with no ciphertext feedback and no appended rule. The doublet suppression, the
corpus's defining anomaly, falls out of the alphabet relation rather than being
imposed. It remains unproven as the actual cipher until `g` is recovered from
the doublet structure and a per-word inversion is attempted.
