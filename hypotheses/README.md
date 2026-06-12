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
| `data/page0-58.txt` | Unsolved ciphertext (13,136 runes, 3,367 words) |
| `data/liber-primus__transcription--master.txt` | Full transcription (solved + unsolved, 15,933 runes total) |
| `lp_section_data.py` | Per-section word lists and page ranges for all 13 sections |

**Caution — plaintext contamination**: the last 95 runes of `page0-58.txt`
are the solved plaintext "Parable" page (ᛈᚪᚱᚪᛒᛚᛖ. = "PARABLE. LIKE THE
INSTAR..."). The true unsolved cipher stream is the first **13,041 runes**
(with **88** doublets, not 89). Exclude the final section before computing
statistics. In the master transcription the solved pages are the *first*
2,797 runes; `page0-58.txt` is the remainder (rune offset 2,797 onward).

In the transcription files, delimiters are: `-` = word boundary, `.` = sentence
boundary, `%` = line break within a page, `&` = page break, `$` = section
break (red rune divider).

The early pages of the master transcription are already solved. You can
recognize them because they decode to readable runeglish (e.g.
`ᛋᚩᛗᛖ-ᚹᛁᛋᛞᚩᛗ` = "some wisdom"). For analysis of the unsolved cipher, use
`data/page0-58.txt`.

## Observed statistical properties

Any valid hypothesis must account for all of these:

| Property | Observed | Expected (random) | Notes |
|----------|----------|--------------------|-------|
| Alphabet | 29 runes, all used | — | Elder Futhark |
| Distribution | Uniform (chi-sq p=0.55) | 1/29 per rune | |
| Shannon entropy | 4.857 bits | 4.858 (max) | 99.98% of maximum |
| IOC | 0.0345 | 1/29 = 0.0345 | Indistinguishable from random |
| Doublet rate | 0.68% | 3.45% (1/29) | 5.09x suppressed |
| Doublet kappa skip=1 | 86 | 447 | 17 sigma below random |
| Kappa skip >= 2 | Normal | Normal | Only skip=1 is anomalous |
| Triplets | 0 | ~15 | Complete absence |
| Friedman test | No period | — | No polyalphabetic key length signal |
| Word boundaries | Preserved | — | Convention: a line break is NOT a word break (words wrap across lines); merged, the cipher has 2,953 words, mean 4.42 runes, English-like shape (solved pages: 4.01, Parable: 4.75 — within the author's stylistic range). Sentences run much longer than solved pages (17.3 vs 8.0 words, p=7e-6) |
| Off-diagonal bigrams | Uniform (chi-sq p=0.23) | — | No structure beyond doublet suppression |
| Repeated 7-gram ᛞᛄᚢᛒᛖᛁᚫ | 1 (word-aligned) | 0.005 | Key-state recurrence; see `repeated-phrase-dju-bei.md` |
| Word transform pairs (shift/beaufort/affine/reversal/rotation/anagram) | At chance | — | Excludes ALL per-word constant-transform ciphers; see `word-transform-census.md` |
| Running-key depth (difference-IOC, all lags) | None (= doublet-suppressed surrogate) | spike to nIoC~1.05 at key period | Excludes all repeating/self-referential keys; see `running-key-text.md` |
| Word-length-context keystream | At chance (1/29) | — | Key is not a function of word-length metadata; see `word-length-keystream-and-boundaries.md` |
| Word-length sequence autocorrelation | ~0 (flat, high power) | English: ±0.06-0.09 (register-dependent) | Flatter than solved pages (~1.9σ) — possible synthetic boundaries, unresolved |
| Pairwise dependence C[i] vs C[i+d] | None for d=2..100 (full 29x29 contingency) | — | Only d=1 (doublets) is anomalous |
| DFT spectrum (all multipliers, all real frequencies) | White noise | — | No periodic additive keystream of any period |
| Line-initial runes | Non-uniform (chi-sq p~1e-7) | Uniform | Layout artifact: solved pages show the same bias (p=0.009, r=0.41 correlation); line-final runes uniform — consistent with glyph-width-driven line wrap, not cipher structure |

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
