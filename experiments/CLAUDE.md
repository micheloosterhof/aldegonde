# experiments/ guide for AI assistants

Rules for writing or changing a script in this directory.

## Check the library first

Before writing a helper in a script, look it up in the table below. Two
surveys of this directory found `ioc` written inline 16 times, a prime sieve
4 times, keyword alphabets 8 times, and English-to-rune transliteration 12
times, all of which the library provided. An inline copy drifts, skips
validation, and hides which scripts a shared fix would reach.

If what you need is not in the table, check `docs/library-candidates.md`. It
may be on the list; add the script you are writing as one more place that
needs it.

## Lookup table

Imports are package-level: `from aldegonde.stats import nioc`,
`from aldegonde.maths import permutation`, `from aldegonde import c3301`.

### Symbols and integers

| Need | Use |
|---|---|
| Runes to indices 0..28 and back | `c3301.RUNES.encode`, `c3301.RUNES.decode`; single items `c3301.r2i`, `c3301.i2r` |
| English spelled as the book spells it, to indices | `c3301.encode_english`; back to labels `c3301.decode_english` |
| Any other alphabet to integers | `alphabet.Alphabet(symbols).encode` |
| Mark and boundary sets of the transcription | `c3301.WORD_BOUNDARY`, `c3301.WORD_MARKS`, `c3301.CLUSTER_MARKS`, `c3301.LINE_WRAP`, `c3301.dot_count` |

### Frequencies, IoC, entropy

| Need | Use |
|---|---|
| Index of coincidence, raw or normalized | `stats.ioc`, `stats.nioc(text, alphabetsize)` |
| N-gram IoC | `stats.ioc2`, `stats.ioc3`, `stats.ioc4` |
| Sliding-window IoC | `stats.sliding_window_ioc` |
| Mutual IoC of two texts | `stats.mioc`, `stats.nmioc` |
| Shannon and Renyi entropy | `stats.shannon_entropy`, `stats.renyi` |
| N-gram counts, positions, distributions | `stats.ngrams`, `stats.ngram_distribution`, `stats.ngram_positions` |
| Chi-square or G-test against a reference text | `stats.chi_test`, `stats.gtest`, `stats.chi_square` |
| N-gram log-probability scoring | `c3301.quadgramscore`, `c3301.trigramscore` (string input; the tables load at import) |

### Coincidence, periodicity, repeats

| Need | Use |
|---|---|
| Kappa at one skip; doublet and triplet counts | `stats.kappa`, `stats.doublets`, `stats.triplets` |
| Kappa z at every skip against the frequency-matched rate | `stats.kappa_spectrum` |
| Friedman period test, with interrupter variant | `analysis.friedman_test`, `analysis.friedman_test_with_interrupter` |
| Kasiski repeat distances and factor spectrum | `analysis.kasiski_examination`, `analysis.repeat_distances`, `analysis.distance_spectrum` |
| Repeated n-gram positions | `stats.repeat_positions`, `stats.repeat_distribution` |
| Lag match indicator; pairs of matches at a separation | `analysis.match_indicator`, `analysis.joint_coincidence` |
| Gaps between consecutive matches | `analysis.match_separations` |
| Within-word repeat rate at a lag, monographs or n-grams | `analysis.within_word_match_rate(words, lag, length)` |
| Within-word against across-word coincidence | `analysis.boundary_coincidence` |
| Do the word boundaries know where the matches are | `analysis.boundary_permutation_test`, with `analysis.recut_words`, `analysis.word_index_map` |
| Is the key a function of a public feature | `analysis.bucket_coincidence(stream, labels)` |
| Pair table at a lag inside words | `stats.pair_counts(words, size, lag)` |
| Rate of pairs with u == perm[v]; its exact minimum and maximum | `stats.relation_rate`, `stats.extremal_relation_rate` |
| Dependence beyond equality in a pair table | `stats.independence(table, off_diagonal=...)` |
| Messages in depth, shared keystream | `analysis.alignment_coincidence` |
| Difference streams | `analysis.delta`, `analysis.delta2` |
| Isomorphs | `stats.isomorph`, `stats.isomorph_statistics` |
| Frequency by position in the word | `stats.position_frequency_chi2` |

### Significance

| Need | Use |
|---|---|
| A count against a stated rate | `stats.binomial_z(hits, trials, rate)`; state the model's rate, not 1/29 by habit |
| Interval for a proportion | `stats.wilson_interval` |
| Do two rates differ | `stats.two_proportion_z` |
| Chi-square with df, p and z | `stats.uniformity`, `stats.goodness_of_fit`, `stats.rate_uniformity` (bins of unequal exposure) |
| Monte Carlo against a null | `stats.monte_carlo`, `stats.monte_carlo_map` |
| Significance of the best peak in a scan | `stats.family_pvalue` |
| Nulls that rearrange the observed symbols | `stats.shuffle`, `stats.no_doublet_shuffle`, `stats.doublet_shuffle`, `c3301.low_doublet_null` |
| Nulls that draw fresh from a process | `stats.markov_null`, `stats.fitted_markov`, `stats.doublet_markov`, `c3301.low_doublet_markov_null` |
| Standard score | `stats.z_score` |

A statistic scanned over lags, periods or offsets is a family of tests. Use
`stats.family_pvalue`; do not read one cell's p on its own. A null that
destroys more than the hypothesis under test manufactures artifacts; say in
the script what the null keeps and what it destroys.

### Keys, ciphers, simulation

| Need | Use |
|---|---|
| Permutation algebra | `maths.permutation`: `compose`, `inverse`, `power`, `order`, `cycles`, `cycle_type`, `parity`, `fixed_points`, `conjugate`, `shift`, `transposition`, `from_cycles`, `random_permutation`, `random_with_cycle_type` |
| A masc dict key as a permutation and back | `maths.permutation.from_key`, `maths.permutation.to_key` |
| Monoalphabetic ciphers and keys | `masc.masc_encrypt`, `masc.masc_decrypt`, `masc.shiftedkey`, `masc.affinekey`, `masc.atbashkey`, `masc.randomkey`, `masc.mixedalphabet` |
| Polyalphabetic tabula recta | `pasc.vigenere_tr`, `pasc.beaufort_tr`, `pasc.quagmire1_tr` to `pasc.quagmire4_tr`, `pasc.pasc_encrypt` |
| Autokey, transposition | `auto`, `trns`, `column` |
| Language-like text from n-gram counts | `stats.fit_markov(training, order)`, `stats.MarkovModel.sample` |
| Primes, factors, totient, Moebius, modular inverse | `maths.primes`, `maths.prime_factors`, `maths.phi_func`, `maths.moebius`, `maths.modInverse` |

## Conventions

- **Integers inside.** Convert runes and English to indices at the top of
  the script and work on integers. The library's table and algebra
  functions take integers and an explicit alphabet size.
- **Corpus loading.** Use an existing loader (`lp_corpus.load_clean`,
  `body_parse`) rather than parsing `%`, `$` and the marks again. There
  should be one tokenizer; see `docs/library-candidates.md`.
- **No absolute paths.** Resolve paths from the repository root.
- **Compute the verdict.** Print conclusions from the numbers the script
  computes, never as a fixed string. A fixed string stays behind when the
  numbers move.
- **No copied constants.** A number another script produced is read from
  that script or recomputed, not typed in.
- **Quote a spread.** A figure from a random draw carries its spread; a
  figure that moves on the seed alone is not a result.
- **Plant a key before trusting a negative.** A search or cascade that
  cannot recover a planted key proves only its own brokenness.
- **Tracked files.** Some scripts rewrite `data/register_vocab.txt`,
  `experiments/walk_reference.json` and
  `experiments/plaintext_control_stats.json`. Check `git status` after a run.
- **When the library gains a primitive you had inlined,** migrate the
  script to it. The migration is the regression test.
