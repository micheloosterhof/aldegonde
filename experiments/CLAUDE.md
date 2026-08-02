# CLAUDE.md — experiments/ directory guide

Instructions for AI assistants writing or modifying experiment scripts in
this directory.

## The prime directive: check the library first

Before writing **any** helper function in an experiment script, check the
lookup table below. A survey of this directory (see
`docs/extraction-candidates.md`) found `ioc` re-implemented inline ~15
times, prime sieves 4 times, and keyword-mixed alphabets 3 times — all of
which the library already provided. Inline re-implementations are bugs:
they drift, they skip validation, and they hide which experiments would
benefit from a shared fix.

If the primitive you need is not in the table, check
`docs/extraction-candidates.md` — it may be slated for extraction, and
you should flag the file you're writing as another duplication site.

## Lookup table: question → library API

All imports are package-level: `from aldegonde.stats import nioc`, etc.

### Frequencies, IoC, entropy

| Need | Use |
|---|---|
| Index of coincidence (raw / normalized) | `stats.ioc`, `stats.nioc` |
| Bigram/trigram/tetragram IoC | `stats.ioc2`, `stats.ioc3`, `stats.ioc4` |
| Sliding-window IoC | `stats.sliding_window_ioc` |
| Mutual IoC between two texts | `stats.mioc`, `stats.nmioc` |
| Rényi entropy family | `stats.renyi` |
| Shannon entropy | `stats.shannon_entropy`, `stats.shannon2_entropy` |
| N-gram counts/positions/distributions | `stats.ngrams`, `stats.ngram_distribution`, `stats.ngram_positions` |
| Chi-square / G-test vs a reference distribution | `stats.mychisquare`, `stats.chisquarescipy`, `stats.gtest` |
| N-gram log-probability fitness scoring | `stats.NgramScorer` (tables ship in `aldegonde/data/ngrams/`) |

### Coincidence, periodicity, repeats

| Need | Use |
|---|---|
| Kappa test at a skip; doublet/triplet counts | `stats.kappa`, `stats.doublets`, `stats.triplets` |
| Period detection (Friedman), with interrupter variant | `analysis.friedman_test`, `analysis.friedman_test_with_interrupter` |
| Kasiski: repeat distances, factor spectrum | `analysis.kasiski_examination`, `analysis.repeat_distances`, `analysis.distance_spectrum` |
| Repeated n-gram positions/distribution | `stats.repeat_positions`, `stats.repeat_distribution` |
| Periodicity in irregular/mixed material | `analysis.krakup` |
| Lag-L match indicator; joint (4th-order) coincidence | `analysis.match_indicator`, `analysis.joint_coincidence` |
| Within-word vs cross-word coincidence at lag d | `analysis.boundary_coincidence` |
| Word-boundary permutation test | `analysis.boundary_permutation_test` (+ `analysis.recut_words`, `analysis.word_index_map`) |
| Messages-in-depth / shared keystream detection | `analysis.alignment_coincidence` |
| Delta/difference streams (any modular op, any skip) | `analysis.delta`, `analysis.delta2`, `analysis.DeltaOp` |
| Isomorph patterns and statistics | `stats.isomorph`, `stats.isomorph_statistics`, `stats.random_isomorph_statistics` |
| Position-in-token frequency bias | `stats.position_frequency_chi2` |

### Significance testing

| Need | Use |
|---|---|
| Monte Carlo: observed statistic vs null model | `stats.monte_carlo` (scalar), `stats.monte_carlo_map` (per-key) |
| Family-wise p-value for the best peak in a scan | `stats.family_pvalue` |
| Null models: shuffle, doublet-free, doublet-rate-matched | `stats.shuffle`, `stats.no_doublet_shuffle`, `stats.doublet_shuffle` |
| z-score | `stats.z_score` |

Discipline: any statistic scanned over lags/periods/offsets needs a
multiple-comparison correction — use `stats.family_pvalue`, or state the
Bonferroni budget explicitly. Any doublet-sensitive statistic tested
against a uniform null on doublet-suppressed text will produce artifacts
(see `missed_tests.py`, `word_transform_census.py`).

### Ciphers, keys, math

| Need | Use |
|---|---|
| Monoalphabetic encrypt/decrypt; Caesar/affine/atbash/random keys | `masc.masc_encrypt`, `masc.masc_decrypt`, `masc.shiftedkey`, `masc.affinekey`, `masc.atbashkey`, `masc.randomkey` |
| Keyword-mixed alphabet; permutation cycles | `masc.mixedalphabet`, `masc.cycles` |
| Polyalphabetic (Vigenère/Beaufort/Quagmire 1–4 tabula recta) | `pasc.pasc_encrypt`, `pasc.vigenere_tr`, `pasc.beaufort_tr`, `pasc.quagmire1_tr`…`quagmire4_tr` |
| Autokey ciphers | `auto` |
| Transposition / columnar | `trns`, `column` |
| Primes (sieve/generator), factorization | `maths.primes`, `maths.gen_primes_opt`, `maths.prime_factors`, `maths.factor_pairs` |
| Totient, gcd, coprimality, Möbius | `maths.phi_func`, `maths.gcd`, `maths.is_coprime`, `maths.moebius` |
| Modular inverse/division | `maths.modInverse`, `maths.modDivide` |
| Cicada alphabet, rune↔index↔value conversions | `c3301.CICADA_ALPHABET`, `c3301.r2i`, `c3301.i2r`, `c3301.r2v`, `c3301.v2r` |
| Bigram diagram visualization | `grams.bigram_diagram` |

## Conventions for this directory

- **Corpus loading:** use the shared local loaders (`lp_corpus.py`,
  `lp_structure.py`) rather than re-parsing the `%`/`$` conventions
  inline. LP parsing stays in `experiments/`; it does not belong in
  `src/aldegonde`.
- **No absolute paths.** Some older scripts hardcode `/Users/...` paths;
  do not copy that pattern — resolve paths relative to the repo root.
- **Self-test your attacks.** Before trusting a negative result, plant a
  known key/plaintext through your own pipeline and confirm the attack
  recovers it (see `walk_verifier.py`, `lp_battery14.py` for the
  pattern).
- **When the library gains a primitive you had inlined,** migrate the
  experiment to the library call — the migration is the regression test.
