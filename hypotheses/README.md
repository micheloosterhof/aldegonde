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
| `data/page0-58.txt` | "Unsolved" ciphertext (13,136 runes, 2,973 words) — see contamination note |
| `data/liber-primus__transcription--master.txt` | Full transcription (solved + unsolved, 15,933 runes total) |
| `lp_section_data.py` | Per-section word lists and page ranges for all 13 sections |

In the transcription files, delimiters are: `-` = word boundary, `.` = sentence
boundary, `%` = line break within a page, `&` = page break, `$` = section
break (red rune divider). `/` and newlines are line wraps, **not** word
boundaries — words span them (verified in the readable sections:
`ᛋᚪᚳ/ᚱᛖᛞ` = SAC/RED). Tokenizing correctly gives 2,973 words, mean length
4.42; the previously documented 3,367 counted line-wrap fragments.

**Contamination note**: `page0-58.txt` is not all unsolved. Of its 12
`$`-sections, section 10 (85 runes) is the **solved** AN END page
(`P = C - (p_n - 1) mod 29`) and section 11 (95 runes) is the **unencrypted**
Parable. The clean unsolved cipher corpus is sections 0-9 = **12,956 runes,
86 doublets**. See `cryptodiagnostics-page0-58.md`.

The early pages of the master transcription are already solved. You can
recognize them because they decode to readable runeglish (e.g.
`ᛋᚩᛗᛖ-ᚹᛁᛋᛞᚩᛗ` = "some wisdom"). For analysis of the unsolved cipher, use
`data/page0-58.txt`.

## Observed statistical properties

Any valid hypothesis must account for all of these:

Numbers below are for the clean corpus (sections 0-9, 12,956 runes).

| Property | Observed | Expected (random) | Notes |
|----------|----------|--------------------|-------|
| Alphabet | 29 runes, all used | — | Elder Futhark |
| Distribution | Uniform (chi-sq p=0.55) | 1/29 per rune | |
| Shannon entropy | 4.857 bits | 4.858 (max) | 99.98% of maximum |
| IOC | 0.0345 | 1/29 = 0.0345 | Indistinguishable from random |
| Doublet rate | 0.66% (86) | 3.45% (1/29, 447) | 5.19x suppressed, 17 sigma |
| Kappa skip >= 2 | Normal | Normal | Only skip=1 is anomalous |
| Triplets | 0 | ~15 | Complete absence |
| Friedman test | No period | — | No polyalphabetic key length signal |
| Word boundaries | Preserved | — | 2,973 words, plausible English lengths |
| Off-diagonal bigrams | Uniform (chi-sq p=0.23) | — | No structure beyond doublet suppression |
| Repeated phrase | ᛞᛄᚢ-ᛒᛖᛁ twice, word-aligned | ~0.005 expected | 6,395 runes apart; see `cryptodiagnostics-page0-58.md` |
| Within-word d=5 coincidences | 4.92% (102/2073); 9 `XY···XY` repeats | 3.45%; 1.5 repeats | Permutation-verified p~0.001; cross-word d=5 random; see `within-word-d5-coincidence.md` |

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
