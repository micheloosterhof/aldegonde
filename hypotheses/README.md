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
| `data/page0-58.txt` | Unsolved ciphertext (13,136 runes, 3,367 words). Caution: the final two `%`-pages in this file are NOT unsolved — they are the solved "AN END" page (85 runes, prime-1 keystream with ᚠ interrupts) and the plaintext parable page (95 runes). Exclude them when computing statistics of the unsolved cipher. |
| `data/liber-primus__transcription--master.txt` | Full transcription (solved + unsolved, 15,933 runes total) |
| `lp_section_data.py` | Per-section word lists and page ranges for all 13 sections |

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
| Digraphic kappa skip=5 | 29 | 15.4 | Part of a confirmed paired-match structure: lag-5 matches pair up at separations 1 and 4 (joint z=+4.1, global p~=0.01, split-half stable). See `lag5-digraph-structure.md` |
| Bigram IOC | 1.0256 (normalized) | 1.0251 (doublet-suppressed null) | The +8 sigma elevation vs plain uniform is fully explained by doublet suppression |
| N-gram repeat counts | Match doublet-suppressed null | — | Apparent trigram-repeat deficit vs uniform null is an artifact |
| Page-aligned kappa | ratio 1.002 (z=+0.2) | 1.0 | No shared keystream resetting at page/section boundaries |
| Triplets | 0 | ~15 | Complete absence |
| Friedman test | No period | — | No polyalphabetic key length signal |
| Word boundaries | Preserved | — | Match English word-length distribution |
| Off-diagonal bigrams | Uniform (chi-sq p=0.23) | — | No structure beyond doublet suppression |

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
2. **The lag-5 paired-match structure is unexplained.** No simulated
   mechanism (autokey families, running keys, bifid p5/p7/p10, lag-5-tapped
   lagged-Fibonacci keystreams, output-avoidance streams) reproduces the
   selective d=1/d=4 pattern of `lag5-digraph-structure.md`. It is the
   primary open discriminator for new hypotheses.

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
