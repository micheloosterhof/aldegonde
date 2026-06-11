# AGENTS.md - Hypotheses Directory

## Purpose

This directory tracks cipher hypotheses for the **unsolved** sections of Liber
Primus (Cicada 3301). Each hypothesis is a self-contained Markdown file with a
claim, evidence, predictions, and verdict. See `README.md` for the full
statistical properties table and status definitions.

## Key context

- The unsolved ciphertext is in `data/page0-58.txt` (13,136 runes, 3,367
  words). All file paths are relative to the repository root.
- The full transcription (solved + unsolved) is in
  `data/liber-primus__transcription--master.txt`. Do NOT analyze the solved
  early pages as if they were unsolved ciphertext.
- The alphabet is 29 Elder Futhark runes. See `src/aldegonde/c3301.py` for the
  alphabet, rune-to-index mappings, and Gematria Primus prime values.
- The aldegonde library uses **0-indexed** rune numbering internally (F=0,
  EA=28). Cicada's Gematria Primus assigns a **prime value** to each rune
  (F=2, U=3, TH=5, O=7, ..., EA=109). These are not sequential indices —
  they are the first 29 primes. Whether the cipher arithmetic uses the
  library's 0-based index, the GP prime values, or some other numbering is an
  open question — do not assume any particular scheme.
- Word boundaries are preserved in the ciphertext (delimited by `-`).
- `lp_section_data.py` has per-section word lists and page ranges.

## Constraints on valid hypotheses

The unsolved text has a very specific statistical profile. Any hypothesis must
explain ALL of these (see `README.md` for exact numbers):

1. **Flat distribution**: All 29 runes near-equally frequent
2. **Doublet suppression**: 5.09x below random expectation (0.68% vs 3.45%)
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

- The last 95 runes of `data/page0-58.txt` are the solved plaintext Parable
  page. Exclude them: the cipher stream is 13,041 runes with 88 doublets.
- `aldegonde.stats.isomorph` compares against *uniform random* text. The
  doublet suppression alone collapses pattern diversity, which makes the
  cipher look 6-11 sigma anomalous on isomorphs. Under a doublet-corrected
  Markov null the anomaly vanishes entirely
  (`experiments/isomorph_corrected.py`). Always use a doublet-corrected
  null for pattern-class statistics.
- Line-initial rune frequencies are strongly non-uniform. This is a
  typesetting artifact (present in solved pages too), not cipher structure.


- The rune numbering question is unresolved. The cipher could use 0-based
  indices, GP prime values, or some other mapping. Do not assume any scheme.
- Many simple cipher classes are already disproved. Check existing hypothesis
  files before proposing a mechanism that is already ruled out.
- Do not overstate any single hypothesis. None are confirmed.
