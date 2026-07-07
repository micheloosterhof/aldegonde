# Hypotheses: Liber Primus Unsolved Sections

This directory tracks cipher hypotheses for the **unsolved** sections of Liber
Primus. Liber Primus is a book of rune-encoded text published by Cicada 3301 in
2014. The community solved several early sections using shift ciphers, Vigenere,
and Beaufort autokey, but the majority of the text remains uncracked.

Each hypothesis gets its own Markdown file and optional supporting scripts.

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
boundary, `%` = line break within a page, `&` = page break, `$` = section
break (red rune divider). `/` and newlines are line wraps, **not** word
boundaries — words span them (verified in the readable sections:
`ᛋᚪᚳ/ᚱᛖᛞ` = SAC/RED). Tokenizing correctly gives 2,973 words, mean length
4.42; the previously documented 3,367 counted line-wrap fragments.

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
| Shannon entropy | 4.857 bits | 4.858 (max) | 99.98% of maximum |
| IOC | 0.0345 | 1/29 = 0.0345 | Indistinguishable from random |
| Doublet rate | 0.66% | 3.45% (1/29) | Fits (1/5)x(1/29) with no free parameters (z=-0.36): acceptance probability exactly 1/5, realized memorylessly (no positional mod-5 frame) |
| Doublet kappa skip=1 | 86 | 447 | 17 sigma below random |
| Kappa skip >= 2 | Normal | Normal | Only skip=1 is anomalous |
| Digraphic kappa skip=5 | 29 | 15.4 | Part of a confirmed paired-match structure: lag-5 matches pair up at separations 1 and 4 (joint z=+4.1, global p~=0.01, split-half stable) and the matches are word-boundary-aware (9 of 29 d1 events are in-word `XY···XY` repeats). See `lag5-digraph-structure.md` |
| Bigram IOC | 1.0256 (normalized) | 1.0251 (doublet-suppressed null) | The +8 sigma elevation vs plain uniform is fully explained by doublet suppression |
| N-gram repeat counts | Match doublet-suppressed null | — | Apparent trigram-repeat deficit vs uniform null is an artifact |
| Page-aligned kappa | ratio 1.002 (z=+0.2) | 1.0 | No shared keystream resetting at page/section boundaries |
| Triplets | 0 | ~15 | Complete absence |
| Friedman test | No period | — | No polyalphabetic key length signal |
| Word boundaries | Preserved | — | Convention: a line break is NOT a word break (words wrap across lines); merged, the cipher has 2,953 words, mean 4.42 runes, English-like shape (solved pages: 4.01, Parable: 4.75 — within the author's stylistic range). Sentences run much longer than solved pages (17.3 vs 8.0 words, p=7e-6) |
| Off-diagonal bigrams | Uniform (chi-sq p=0.23) | — | No structure beyond doublet suppression |
| Repeated 7-gram ᛞᛄᚢᛒᛖᛁᚫ | 1 (word-aligned) | 0.005 | 6,395 runes apart (= 5 x 1279, both prime); key-state recurrence; see `repeated-phrase-dju-bei.md` |
| Word transform pairs (shift/beaufort/affine/reversal/rotation/anagram) | At chance | — | Excludes ALL per-word constant-transform ciphers; see `word-transform-census.md` |
| Running-key depth (difference-IOC, all lags) | None (= doublet-suppressed surrogate) | spike to nIoC~1.05 at key period | Excludes all repeating/self-referential keys; see `running-key-text.md` |
| Word-length-context keystream | At chance (1/29) | — | Key is not a function of word-length metadata; see `word-length-keystream-and-boundaries.md` |
| Word-length sequence autocorrelation | ~0 (flat, high power) | English: ±0.06-0.09 (register-dependent) | Flatter than solved pages (~2σ) — possible synthetic boundaries, unresolved |
| Sentence-final word lengths | = random words (z=-1.2) | English: strongly elevated (solved: z=+7.1) | **'.' marks do not mark English sentence ends** (contrast z=+5.9); see `word-length-keystream-and-boundaries.md` |
| Within-word d=5 coincidences | 4.92% (102/2073); 9 `XY···XY` repeats | 3.45%; 1.5 repeats | Permutation-verified p~0.001; cross-word d=5 count at chance; reconciled with the lag-5 pairing: paired AND isolated matches are both word-boundary-aware (p=0.014 / 0.018), one word-aware phenomenon; see `within-word-d5-coincidence.md`, `experiments/lag5_word_boundary.py` |
| Within-word d=5 delta histogram | Flat off zero (nonzero bins 0.62-1.18x) | Key-sharing: plaintext Q leaks at f~0.55 | Kills within-word key sharing at z=+3.6 (copy model wins by 6.4 nats); real runeglish matches at ~6.1% within words (both controls); see `within-word-key-sharing.md` (disproved) |
| Repeated nonzero lag-5 deltas at seps 1/4 | At chance (z=+0.2/-0.1) | Additive drift: elevated like the zero bin | The lag-5 pairing is value-literal — only exact glyph equality pairs up (zero bin z=+3.3/+3.1); see `experiments/delta5_generalization.py` |
| Mod-5 / class projections (index mod 5/2/7, div 6; gematria value mod 5/3, last digit) | All flat (grand max z 3.1 over 420 tests, null expects ~3.5) | — | No hidden symbol-class structure; the corpus "5" is not a partition of the alphabet; see `experiments/mod5_projection_battery.py` |
| Within-word d=6 matches | 31 vs 44.5 ± 6.2 (P<=0.013; ~0.09 after look-elsewhere) | 71.5 (1/29 of pairs) x opportunity | Watched hint: replicates in both halves, NOT produced by the copy model; see `experiments/within_word_d6_deficit.py` |
| Word-scoped copy model (5 calibrated rates, 12 emergent stats) | All \|z\| <= 1.8 | — | ~39 events / ~66 copied glyphs (~0.5%) reproduce the full lag-5 + boundary fingerprint; see `experiments/word_scoped_copy_simulator.py`, catalog in `lag5-event-catalog.json` |
| Fibonacci-spacing probes (battery 20) | All flat | — | Rune extraction at Fibonacci positions (6 alignments), word/sentence-length enrichment, boundary positions, Fibonacci-interrupt keystreams (880 page-tests): nothing. One absorbed curiosity: doublet gaps contain 0 Fibonacci values vs 3.3±1.8 under the dead-time-conditioned null (p=0.03 uncorrected, ~15-test family); see `experiments/lp_battery20.py` |
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
and trigram repeats: any null for this corpus must include the doublet
rate); delete-marker periodicity scans (29 interrupter candidates x
periods 2-30) close the "periodic key hidden by AN-END-style interrupts"
loophole; marker-reset keying flat; numeric autocorrelation flat (lag-1
r = -0.0297 is quantitatively the doublet artifact); DFT spectrum has no
lines; per-rune positions uniform; sliding-window nIoC homogeneous
(retiring KRAKUP's nonhomogeneity hint); cross-section distributions
identical. The corpus has exactly two statistical departures from
randomness: doublet suppression and the lag-5 pairing.

## Structural constraints

Two consequences of the table that prune whole mechanism families
(derivations and simulations in `experiments/mechanism_fingerprint.py`):

1. **Doublet suppression requires output feedback.** A ciphertext doublet
   needs dP = -dK; constraining only the keystream (e.g. K[i] != K[i+1])
   leaves the rate at ~3.46%. Any key schedule fixed before a rune is
   emitted — running keys, math sequences, word-level keys,
   position-within-word keys, fractionation — cannot produce the observed
   0.66%. The encryptor must see the previous ciphertext rune (or
   equivalently select keys plaintext-aware) and avoid doublets ~80% of the
   time.
2. **The lag-5 structure is literal, word-scoped copying — every additive
   reading is dead.** The paired-match structure is unexplained by any
   tested per-rune mechanism (autokey families, running keys, bifid
   p5/p7/p10, lag-5-tapped lagged-Fibonacci keystreams, output-avoidance
   streams, Hill variants, group-edge carryover), and as of July 2026 the
   additive interpretations of the anomaly itself are disproved: repeated
   nonzero lag-5 deltas are at chance (no local key drift,
   `experiments/delta5_generalization.py`) and the within-word delta
   histogram is flat off zero (no within-word key sharing at the f pinned
   by the match excess, rejected z=+3.6, `within-word-key-sharing.md`).
   Information theory narrows the surviving options for the deterministic
   copies to: inserted nulls, plaintext-repeat back-references, or
   author-side composition artifacts (key+plaintext coincidence is now
   excluded by the same delta tests). None of these three is currently
   distinguishable from the others by ciphertext statistics — see the
   degrees-of-freedom audit in `lag5-back-reference.md`. Constraints: the
   matches are word-boundary-aware (`experiments/lag5_word_boundary.py`),
   and the copy rule itself is word-scoped — plaintext offers lag-5
   repeats at ~6.1% across word boundaries too (the runeglish IoC rate,
   measured on two plaintext controls), yet cross-word ciphertext pairs
   match at exactly 1/29.

## Status values

| Status | Meaning |
|--------|---------|
| `disproved` | Contradicted by the observed statistical properties. Cannot be the cipher. |
| `unresolved` | Not yet contradicted, but no strong positive evidence either. Needs testing. |
| `plausible` | Consistent with the statistics, with some positive evidence. Not yet confirmed. |
| `confirmed` | Proven correct (none so far). |

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
