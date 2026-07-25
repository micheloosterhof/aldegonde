# Hypotheses: Liber Primus Unsolved Sections

This directory tracks cipher hypotheses for the **unsolved** sections of Liber
Primus. Liber Primus is a book of rune-encoded text published by Cicada 3301 in
2014. The community solved several early sections using shift ciphers, Vigenere,
and Beaufort autokey, but the majority of the text remains uncracked.

Files come in two kinds, tagged `type:` in their frontmatter:

- **observations** — a measured statistical feature of the corpus, with a
  self-contained significance script (`experiments/obs_*.py` for the basic
  fingerprint) and a reproduction of its numbers. These are facts any cipher
  must explain.
- **hypotheses** — a proposed cipher mechanism, scored against the
  observations.

See **[INDEX.md](INDEX.md)** for the split list of both. The atomic
fingerprint observations (flat IoC, doublet suppression, zero triplets,
bigram IoC, kappa spectrum) each have an `obs_*.py` script that reproduces
one number; `experiments/lp_corpus.py` is the shared clean-corpus loader.

## Data

All paths are relative to the repository root.

| File | Contents |
|------|----------|
| `data/page0-58.txt` | Full late corpus (13,136 runes; 2,973 words merging line-wraps, 3,367 counting wrap fragments) — includes two solved pages, see contamination note |
| `data/page0-56.txt` | Same file with the solved trailing pages removed |
| `data/liber-primus__transcription--master.txt` | Full transcription (solved + unsolved, 15,933 runes total) |
| `lp_section_data.py` | Per-section word lists and page ranges for all 13 sections |

**Caution — plaintext contamination**: `page0-58.txt` is not all unsolved. Of
its 12 `$`-sections, section 10 (85 runes) is the **solved** "AN END" page
(`P = C - (p_n - 1) mod 29`, with ᚠ keystream interrupts) and section 11
(95 runes) is the **unencrypted** Parable (ᛈᚪᚱᚪᛒᛚᛖ. = "PARABLE. LIKE THE
INSTAR..."). The clean unsolved cipher corpus is sections 0-9 =
**12,956 runes, 86 doublets**. (Some earlier analyses excluded only the
Parable, giving 13,041 runes / 88 doublets — those figures include the
solved AN END page.) In the master transcription the solved early pages are
the *first* 2,797 runes; `page0-58.txt` is the remainder (rune offset 2,797
onward). See `cryptodiagnostics-page0-58.md`.

In the transcription files, delimiters are: `-` = word boundary, `.` = sentence
boundary, `%` = page break, `&` = chapter/segment break, `$` = section
break (red rune divider). `/` and newlines are line wraps, **not** word
boundaries — words span them (verified in the readable sections:
`ᛋᚪᚳ/ᚱᛖᛞ` = SAC/RED). Tokenizing correctly gives 2,973 words in the full
file (2,928 in the clean sections 0-9), mean length 4.42; the previously
documented 3,367 counted line-wrap fragments. (Note that words also span
`%` page breaks — 46 of the 57 are mid-word — so the standard `- . % & $`
tokenization slightly over-splits; see the convention check in
`word-length-keystream-and-boundaries.md`. The difference is ~50 words and
does not move any reported statistic materially.)

The early pages of the master transcription are already solved. You can
recognize them because they decode to readable runeglish (e.g.
`ᛋᚩᛗᛖ-ᚹᛁᛋᛞᚩᛗ` = "some wisdom"). For analysis of the unsolved cipher, use
`data/page0-58.txt` sections 0-9 (or `data/page0-56.txt`).

## Observed statistical properties

Any valid hypothesis must account for all of these:

Numbers below are for the clean corpus (sections 0-9, 12,956 runes).

| Property | Observed | Expected (random) | Notes |
|----------|----------|--------------------|-------|
| Alphabet | 29 runes, all used | — | Elder Futhark |
| Distribution | Uniform (chi-sq p=0.55) | 1/29 per rune | |
| Shannon entropy | 4.8565 bits | 4.8580 (max) | 99.97% of maximum |
| IOC | 0.0345 | 1/29 = 0.0345 | Indistinguishable from random |
| Doublet rate | 0.66% | 3.45% (1/29) | Fits (1/5)x(1/29) with no free parameters (z=-0.36): acceptance probability exactly 1/5, realized memorylessly (no positional mod-5 frame) |
| Doublet kappa skip=1 | 86 | 447 | 17 sigma below random |
| Kappa skip >= 2 | Normal | Normal | Only skip=1 is anomalous |
| Digraphic kappa skip=5 | 29 | 15.4 | Part of a confirmed paired-match structure: lag-5 matches pair up at separations 1 and 4 (joint z=+4.1, split-half stable; global p~=0.01 with the hand-picked pattern family, p~=0.033 under the family-blind re-assessment) and the matches are word-boundary-aware (9 of 29 d1 events are in-word `XY···XY` repeats). See `lag5-digraph-structure.md` |
| Bigram IOC | 1.0256 (normalized) | 1.0251 (doublet-suppressed null) | The +8 sigma elevation vs plain uniform is fully explained by doublet suppression |
| N-gram repeat counts | Match doublet-suppressed null | — | Apparent trigram-repeat deficit vs uniform null is an artifact |
| Page-aligned kappa | ratio 1.002 (z=+0.2) | 1.0 | No shared keystream resetting at page/section boundaries |
| Triplets | 0 | ~15 | Complete absence |
| Friedman test | No period | — | No polyalphabetic key length signal |
| Word boundaries | Preserved | — | Convention: a line break is NOT a word break (words wrap across lines); merged, the clean corpus has 2,928 words (2,953 with the solved AN END page included), mean 4.42 runes, English-like shape (solved pages: 4.01, Parable: 4.75 — within the author's stylistic range). Sentences run much longer than solved pages (17.4 vs 8.0 words per '.' mark on the clean corpus, p=4e-6; per *qualifying* sentence the same signal reads 19.7 vs 8.9 — see `word-length-keystream-and-boundaries.md`) |
| Off-diagonal bigrams | Uniform (chi-sq p=0.23) | — | No structure beyond doublet suppression |
| Repeated 6-gram ᛞᛄᚢ-ᛒᛖᛁ (two words) | 1 (word-aligned) | 0.14 | 6,395 runes apart; key-state recurrence; the once-cited 7th rune ᚫ is the first rune of the solved AN END page (cross-boundary coincidence, retracted); see `repeated-phrase-dju-bei.md` |
| Word transform pairs (shift/beaufort/affine/reversal/rotation/anagram) | At chance | — | Excludes ALL per-word constant-transform ciphers; see `word-transform-census.md` |
| Running-key depth (difference-IOC, all lags) | None (= doublet-suppressed surrogate) | spike to nIoC~1.05 at key period | Excludes all repeating/self-referential keys; see `running-key-text.md` |
| Word-length-context keystream | At chance (1/29) | — | Key is not a function of LOCAL word-length context (own length, position, neighbour lengths). Whole-prefix schedules clocked by the length sequence (e.g. `length-clocked-walk.md`) are invisible to this bucketing test and are NOT excluded; see `word-length-keystream-and-boundaries.md` |
| Word-length sequence autocorrelation | ~0 (flat, high power) | English: ±0.06-0.09 (register-dependent) | Flatter than solved pages (~2σ) — possible synthetic boundaries, unresolved |
| Sentence-final word lengths | = random words (z=-1.2) | English: strongly elevated (solved: z=+7.1) | **'.' marks do not mark English sentence ends** (contrast z=+5.9); see `word-length-keystream-and-boundaries.md` |
| Within-word d=5 coincidences | 4.92% (102/2073); 9 `XY···XY` repeats | 3.45%; 1.5 repeats | Permutation-verified p~0.001; cross-word d=5 count at chance; reconciled with the lag-5 pairing: paired AND isolated matches are both word-boundary-aware (p=0.014 / 0.018), one word-aware phenomenon; see `within-word-d5-coincidence.md`, `experiments/lag5_word_boundary.py` |
| Within-word d=5 echo by rune | S: 11 pairs; next rune 7 | 1.75 (S); ~2.5 (others) | The d=5 excess is carried disproportionately by one rune, S (Sigel): p=2.4e-6 against identity-preserving nulls, Bonferroni-clean, distance-5-specific, within-word only. Under base-scrambling models (the walk) the same concentration is expected-level, P≈0.08-0.15 — refutes identity-preserving mechanisms, no tension with the walk; see `rune-s-lag5-echo.md`, `experiments/rune_s_walk_test.py` |
| Pairwise dependence C[i] vs C[i+d] | None for d=2..100 (full 29x29 contingency) | — | Only d=1 (doublets) is anomalous |
| DFT spectrum (all multipliers, all real frequencies) | White noise | — | No periodic additive keystream of any period |
| Line-initial runes | Non-uniform (chi-sq p~1e-7) | Uniform | Layout artifact: solved pages show the same bias (p=0.009, r=0.41 correlation); line-final runes uniform — consistent with glyph-width-driven line wrap, not cipher structure |

## Negative results from the gap audit

`experiments/gap_audit.py` closed eight previously untested angles, all
clean: no keystream reuse at any lag 1-6400 (rules out keystreams continuing
across pages and periods up to ~6400); doublet suppression present in every
section with no per-section periodicity or split signal (one corpus-wide
mechanism, not different cipher families per section); reversed-direction
(right-to-left) autokey excluded by split tests on the reversed corpus; no
acrostics in first runes of words/lines/sentences/pages; doublet rune values
uniform (no marker rune); no per-line keystream reset; zero compressible
redundancy (zlib); word GP-sums unremarkable under the proper null.

`experiments/missed_tests.py` added the remaining unused tests, all
negative: full 29x29 contingency chi2 at every lag 1-60 is flat
off-diagonal (the ONLY pairwise structure at any distance is the lag-1
doublet diagonal); isomorph duplicates are flat against a
doublet-suppressed null (the library's uniform baseline shows a FAKE +6
sigma — third artifact of the doublet-suppression trap, after bigram IoC
and trigram repeats; a fourth appeared in the seam-bigram census
(`seam-channel-clean.md`: a fake ~2σ pair-IoC lean from the diagonal
deficit packing the seams into 812 effective cells) and a fifth in the
word-prefix catalog (`repeated-phrase-dju-bei.md`: word-initial digraphs
are adjacent pairs, so 29 of the 841 cells are suppressed and a uniform
null overstates every density statistic): ANY null for this corpus must
include the doublet rate — the trap recurs wherever adjacent runes are
counted, which is nearly everywhere); delete-marker periodicity scans (29 interrupter candidates x
periods 2-30) close the "periodic key hidden by AN-END-style interrupts"
loophole; marker-reset keying flat; numeric autocorrelation flat (lag-1
r = -0.0297 is quantitatively the doublet artifact); DFT spectrum has no
lines; per-rune positions uniform; sliding-window nIoC homogeneous
(retiring KRAKUP's nonhomogeneity hint); cross-section distributions
identical. A runeglish-trigram-fitness scan (`experiments/englishness_scan.py`,
July 2026) confirms this in the language dimension: no section or 500-rune
window resembles English above chance (best window matched by ~30% of
shuffled corpora; the one sectional blip, section 5 at z=+2.6, decomposes
entirely into a chance rune-composition lean — its ORDER structure is null
under a within-section shuffle, z=+1.2). Calibration: the same scorer
separates the plaintext Parable at fitness -3.4 vs corpus -6.9. At the rune-stream level the corpus has exactly two broad
statistical departures from randomness: doublet suppression and the lag-5
structure — plus one isolated event, the DJU-BEI state return
(`repeated-phrase-dju-bei.md`). Metadata-level anomalies are separate: the
`.` marks do not carry English sentence semantics (z=+5.9 contrast) and
the word-length autocorrelation is suspiciously flat (~2 sigma), see
`word-length-keystream-and-boundaries.md`.

## Structural constraints

Three consequences of the table that prune whole mechanism families —
the first two about what the cipher can be, the third about what any
attack on it can do (derivations and simulations in
`experiments/mechanism_fingerprint.py` and the scripts cited inline):

1. **Doublet suppression requires output feedback OR a bigram-tuned
   alphabet relation.** For ADDITIVE ciphers a ciphertext doublet needs
   dP = -dK; constraining only the keystream (e.g. K[i] != K[i+1]) leaves
   the rate at ~3.46%, so any additive key schedule fixed before a rune is
   emitted — running keys, math sequences, additive word-level or
   position-within-word keys, fractionation — cannot produce the observed
   0.66%. Under that cipher class the encryptor must see the previous
   ciphertext rune and avoid doublets ~80% of the time. There is exactly
   one known feedback-free escape: general MIXED substitution alphabets
   whose adjacent-alphabet relation is tuned to rare plaintext bigrams
   (`c[i]=c[i-1] <=> p[i-1]=g(p[i])`, achievable range 0.13%-15%) — the
   mechanism of `length-clocked-walk.md` / `per-word-related-alphabets.md`.
   Affine relations cannot get below 1.25%, so the escape requires
   non-arithmetic mixed permutations. **Sharpened (July 2026), with a scope caveat.**
   Two EXHAUSTIVE floor computations show the relation cannot be
   arithmetic: a plain 5-letter Vigenere step floors at 1.19% over all
   29 shifts (`length-clocked-walk.md`), and every arithmetic family for
   `σ` floors at 1.22%-2.11% on the cross-word table, over all family
   members (`sigma-power-step.md`) — against the observed 0.63%/0.79%.
   The keyword families have now been EXHAUSTED
   too (`experiments/keyword_exhaustion.py`: 196,898 dictionary words x 4
   construction rules = 787,592 alphabets, with a matched random null),
   and they split: **`g` CAN be keyword-derived** — 12,064 alphabets
   clear its 0.0063 diagonal, an enumerable candidate list — while
   **`σ` cannot**, with 0 of 787,592 keyword and 0 of 40,000 random
   alphabets reaching 0.0079 (minima 0.0092 and 0.0099). So no *sampled*
   alphabet supplies σ as a rotating disk; only a designed permutation
   does. Net: the "no small key" conclusion holds specifically at the
   SPACE step, and the letter step is enumerable
   (`mixed-alphabet-vigenere.md`). (The once-equivalent hold variant —
   a period-5 hold exposing 1/5 of plaintext doublets, `stay-slot-hold.md`
   — is disproved by the doublet position-profile test: exposed plaintext
   doubles would be start-forbidden and end-heavy, and the observed
   doublets are positionally flat. The same test constrains the surviving
   tuned diagonal: its bigram class must be positionally near-baseline.
   See `experiments/doublet_position_profile.py`.)
2. **The lag-5 structure has two faces with two rival readings, neither
   confirmed.** The WITHIN-WORD d5 coincidence excess (the echo) is
   reproduced by the period-5 same-alphabet leak of the length-clocked
   walk family (`length-clocked-walk.md`, `d5-partial-alphabet-leak.md`):
   positions 5 apart in a word share an alphabet and plaintext
   coincidences show through. The PAIRED {1,4} match events
   (`lag5-digraph-structure.md`) are not produced by any single tested
   per-rune mechanism (autokey families, running keys, bifid p5/p7/p10,
   lag-5-tapped lagged-Fibonacci keystreams, output-avoidance streams,
   Hill variants, group-edge carryover); information theory narrows the
   options for deterministic copies to: inserted nulls, key+plaintext
   coincidence (rate-disfavored), plaintext-repeat back-references, or
   author-side composition artifacts. None of these is currently
   distinguishable from the others by ciphertext statistics — see the
   degrees-of-freedom audit in `lag5-back-reference.md` before treating
   any simulation "match" as confirmation. **Update (July 2026):** an
   information-theory argument splits the pairing in two. A deterministic
   `C[i]=C[i-5]` copy destroys `P[i]`'s information, so the only coherent
   copy fires where `P[i]=P[i-5]` — which under `g^5=id` is just the walk's
   echo, not a separate mechanism. Measuring real runeglish plaintext
   (`experiments/plaintext_lag5_pairing.py`): the **d1** face (repeated
   bigram at distance 5, `XY···XY`) IS a real plaintext morphology feature
   (3.7x baseline) that the walk echo passes through with no overlay; the
   **d4** face ((1st,5th)-of-5 frame) is BELOW chance in plaintext and so
   is NOT explained by the echo. Net: d1 is accounted for by the walk
   alone; d4 is the residual count excess — and the July 2026 anatomy
   (`experiments/d4_frame_anatomy.py`) found no geometric or key-equation
   structure in it (most legs cross one boundary, where walk
   alphabet-coincidence is impossible; no σ-relation cell enriched), so it
   is a watch-item compatible with scan noise, not an attack surface.
   (This retracts an earlier
   "walk + copy overlay does both" claim — the overlay was
   information-theoretically incoherent.) The two faces overlap in the
   nine in-word `XY···XY` repeats and are reconciled as ONE word-aware
   phenomenon in `within-word-d5-coincidence.md`. Additional constraint
   (July 2026): the lag-5 matches are word-boundary-aware — both the
   paired and the isolated matches sit inside words above the
   boundary-permutation null (`experiments/lag5_word_boundary.py`) — so
   the mechanism sees the word structure, favoring word-scoped state over
   purely positional copy semantics.

3. **The key search has no gradient, so the attack must be enumerative**
   (July 2026, `experiments/two_rune_gradient.py`; validated on planted
   keys in simulated walk ciphertext). Scoring candidate keys on the 465
   two-rune words — `THE` is exactly `ᚦᛖ` in runeglish and the class is
   dominated by eight function words (69% of register tokens) —
   recovers `base_0` **exactly on the first restart** once `g` and `σ`
   are known (true key −1319 vs −5366 for a random base, 4,047 nats).
   So `base_0` is effectively free: a 29!-fold reduction of the key
   space. But score\*(g, σ), the score after optimally fitting `base_0`,
   is a **delta function**: −1296 at the true key, −4968 with `σ` off by
   a single transposition, −4994 at random. `g` and `σ` enter the base
   chain once per word, so a one-swap error is applied ~2,900 times and
   every base past the first is destroyed. No hill-climb, annealing or
   evolutionary search over `(g, σ)` can work, with this or any
   comparable objective. The whole difficulty is concentrated in
   `(g, σ)`, which must come from enumeration over structurally
   constrained candidates — and constraint 1 says those candidates
   cannot be keyword-sized. The prefix escape was tested and fails from
   BOTH ends: basin width and statistical power move oppositely with
   prefix length and never overlap — at K=10 words a 1-swap-wrong σ
   still retains 94% of the signal but 49 runes cannot pin a
   29-permutation (climbs reach near-true scores at 1/29 correct),
   while by K=160 the basin is down to 14% and the climb never leaves
   the flat. With the joint space at ~1e48, neither search nor
   enumeration works — the one reducible object is the designer's
   construction PROCEDURE, not the key. See
   `no-known-plaintext-foothold.md`.

## Status values

| Status | Meaning |
|--------|---------|
| `disproved` | Contradicted by the observed statistical properties. Cannot be the cipher. |
| `unresolved` | Not yet contradicted, but no strong positive evidence either. Needs testing. |
| `plausible` | Consistent with the statistics, with some positive evidence. Not yet confirmed. |
| `confirmed` | Proven correct. No CIPHER hypothesis is confirmed; characterization files (measured statistical properties, not cipher proposals) use `confirmed (characterization)`. |

Observation files grade evidential strength with two additional values:
`weak` (nominal signal that does not survive multiple-test correction; kept
as a watch-item) and `partial` (one component verified, another underpowered
or undecidable). Observations with a verified anomaly but no known mechanism
use `plausible (verified anomaly; mechanism unknown)`.

## Directory structure

```
hypotheses/
  README.md            # This file
  AGENTS.md            # Instructions for AI agents
  TEMPLATE.md          # Template for hypothesis files
  <hypothesis>.md      # One file per hypothesis
  <hypothesis>.py      # Optional supporting scripts
```

Scripts may also live in `experiments/` at the repo root and be referenced from
hypothesis files.

## Adding a hypothesis

1. Check existing files first. If your idea is a variant of an existing
   hypothesis, consider whether it belongs as a separate file or an update to
   the existing one. Separate files are appropriate when the mechanism or
   predictions differ meaningfully (e.g. `ciphertext-autokey.md` vs
   `beaufort-autokey-ea.md`).
2. Copy `TEMPLATE.md` to `<descriptive-name>.md`. Use lowercase with hyphens.
3. Fill in all sections. The Predictions section is important: state what
   testable consequences the hypothesis has.
4. Add supporting scripts as `<descriptive-name>.py` or reference existing
   scripts in `experiments/`.
5. Keep the status up to date as evidence accumulates.
