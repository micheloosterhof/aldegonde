# AGENTS.md - Hypotheses Directory

## Purpose

This directory tracks cipher hypotheses for the **unsolved** sections of Liber
Primus (Cicada 3301). Each hypothesis is a self-contained Markdown file with a
claim, evidence, predictions, and verdict. See `README.md` for the full
statistical properties table and status definitions.

## Key context

- The clean unsolved corpus is `data/page0-56.txt`: master pages 15-70,
  **12,956 runes, 2,928 words, 86 doublets**. Load it with
  `experiments/lp_corpus.load_words()` (or `load_clean`, `load_tokenized`),
  which wraps `aldegonde.c3301.tokenize`, the one tokenizer. Do not split on
  `%`, `$` and the marks by hand. All file paths are relative to the
  repository root.
- `data/page0-58.txt` is the same body plus two solved sections at the end
  (the "AN END" page and the plaintext Parable). If you read it, keep
  sections 0-9 only. See the contamination note in `README.md`.
- The full transcription (solved + unsolved) is in
  `data/liber-primus__transcription--master.txt`. Do NOT analyze the solved
  early pages as if they were unsolved ciphertext. The author's own
  plaintext, for calibration, is `experiments/lp_plaintext_register.corpus()`.
- The alphabet is 29 Elder Futhark runes. See `src/aldegonde/c3301.py` for the
  alphabet, rune-to-index mappings, and Gematria Primus prime values.
- The aldegonde library uses **0-indexed** rune numbering internally (F=0,
  EA=28). Cicada's Gematria Primus assigns a **prime value** to each rune
  (F=2, U=3, TH=5, O=7, ..., EA=109). These are not sequential indices —
  they are the first 29 primes. Whether the cipher arithmetic uses the
  library's 0-based index, the GP prime values, or some other numbering is an
  open question — do not assume any particular scheme.
- Word boundaries are preserved in the ciphertext. The transcription writes
  the marks as circled numerals by dot count (`①` is the word separator,
  `④` the four-dot mark, `⑬` closes a section); `-` and `.` are the legacy
  two-character encoding. Line wraps `/` are NOT word boundaries. The sets
  are in `c3301.WORD_MARKS`, `c3301.CLUSTER_MARKS`, `c3301.WORD_BOUNDARY`.
- `lp_section_data.py` has per-section word lists and page ranges.
- The standing specification every candidate must clear is
  `what-any-solution-must-satisfy.md`; the ranked directions beyond the
  current models are in `docs/new-directions.md`.

## Constraints on valid hypotheses

The unsolved text has a very specific statistical profile. Any hypothesis must
explain ALL of these (see `README.md` for exact numbers):

1. **Flat distribution**: All 29 runes near-equally frequent
2. **Doublet suppression**: 5.19x below random expectation (0.66% vs 3.45%)
3. **No triplets**: Zero occurrences
4. **No Friedman period**: No detectable periodic key length
5. **Normal kappa at skip >= 2**: Only adjacent pairs are anomalous
6. **Preserved word boundaries**: Words match English word-length distributions

## Working with hypothesis files

- Follow `TEMPLATE.md` for the file format. Key sections: Claim, Status,
  Mechanism, Evidence for/against, Predictions, Scripts, Related, Verdict.
- Status values: `disproved`, `unresolved`, `plausible`, `confirmed`. See
  `README.md` for definitions.
- File naming: lowercase with hyphens, e.g. `ciphertext-autokey.md`.
- When a hypothesis is a specific variant of another, create a separate file
  and cross-reference using the Related section.
- Scripts can live in this directory or in `experiments/`. Use the aldegonde
  library:
  ```python
  from aldegonde import c3301, masc, pasc, auto
  from aldegonde.stats import ioc, kappa, ngrams
  from aldegonde.analysis import friedman_test
  ```

## Common pitfalls

- `data/page0-58.txt` is contaminated with solved material: section 10 (the
  AN END page, 85 runes) and section 11 (the plaintext Parable, 95 runes).
  Exclude both: the clean cipher stream is sections 0-9, 12,956 runes with
  86 doublets. (Older analyses citing 13,041 runes / 88 doublets excluded
  only the Parable and still include the solved AN END page.)
- `random_isomorph_statistics` defaults to *uniform random* text. The
  doublet suppression alone collapses pattern diversity, which makes the
  cipher look 6-11 sigma anomalous on isomorphs. Under a doublet-corrected
  null the anomaly vanishes entirely (`experiments/isomorph_corrected.py`).
  Pass `null=c3301.low_doublet_null(), observed=seq`, and use a
  doublet-corrected null for every pattern-class statistic.
- Line-initial rune frequencies are strongly non-uniform. This is a
  typesetting artifact (present in solved pages too), not cipher structure.


- The rune numbering question is unresolved. The cipher could use 0-based
  indices, GP prime values, or some other mapping. Do not assume any scheme.
- Many simple cipher classes are already disproved. Check existing hypothesis
  files before proposing a mechanism that is already ruled out.
- Do not overstate any single hypothesis. None are confirmed.
