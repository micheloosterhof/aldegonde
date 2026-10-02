# Library candidates from the experiments

What `experiments/` keeps writing by hand, what the library now has for it,
and what is still open. Updated 2026-10-02.

Two surveys feed this list: one of about 120 scripts on 2026-08-02 (branch
`claude/extract-experiments-primitives-qx8dqx`, head `5623a05`, now deleted)
and one of 518 scripts on 2026-09-29. Both found the same thing: the
experiments import almost nothing from the library except `c3301`, and
re-implement the same helpers. Adding functions does not fix that on its
own; every new module should be followed by migrating one experiment onto
it, which is both the regression test and the proof that the API fits.

## Design rule

Integers inside, symbols at the edge. Functions that index tables or do
arithmetic take symbols as integers `0..N-1` and an explicit alphabet size;
`aldegonde.alphabet.Alphabet` converts at the edge, and `c3301.RUNES` and
`c3301.encode_english` do it for the Liber Primus. Statistics that only
compare symbols for equality stay generic. Never infer the alphabet size
from the data: a symbol absent from the text would shrink it.

## In the library

| Need | Use |
|---|---|
| Symbols to integers and back | `alphabet.Alphabet`; `c3301.RUNES` |
| English spelled the way the book spells it | `c3301.encode_english`, `c3301.decode_english` |
| Permutation algebra | `maths.permutation`: `compose`, `inverse`, `power`, `order`, `cycles`, `cycle_type`, `parity`, `conjugate`, `shift`, `transposition`, `from_cycles`, `random_with_cycle_type`, `from_key`, `to_key` |
| Count against a stated rate, interval, two rates | `stats.binomial_z`, `stats.wilson_interval`, `stats.two_proportion_z` |
| Pair table inside words; rate of a permutation relation; its exact extremes | `stats.pair_counts`, `stats.relation_rate`, `stats.extremal_relation_rate` |
| Chi-square with df, p and a normal-scale z | `stats.uniformity`, `stats.goodness_of_fit`, `stats.rate_uniformity` (unequal exposure), `stats.independence` (pair table, diagonal optional) |
| Within-word repeat rate at a lag, n-grams included | `analysis.within_word_match_rate(words, lag, length)` |
| Is the key a function of a public feature | `analysis.bucket_coincidence(stream, labels)` |
| Gaps between matches | `analysis.match_separations` |
| Kappa at every skip against the frequency-matched rate | `stats.kappa_spectrum` |
| Language-like text from n-gram counts | `stats.MarkovModel`, `stats.fit_markov` |
| Nulls that rearrange the observed symbols | `stats.shuffle`, `stats.no_doublet_shuffle`, `stats.doublet_shuffle`, `c3301.low_doublet_null` |
| Nulls that draw fresh from a process | `stats.markov_null`, `stats.fitted_markov`, `stats.doublet_markov`, `c3301.low_doublet_markov_null` |
| Monte Carlo against a null, one statistic or a scan | `stats.monte_carlo`, `stats.monte_carlo_map`, `stats.family_pvalue` |
| Coincidence split by word boundary; boundary permutation test | `analysis.boundary_coincidence`, `analysis.boundary_permutation_test` |

## Open, ranked by counted duplication

1. **Corpus tokenizer.** 177 scripts read the corpus file directly and at
   least 6 tokenizers exist (`lp_corpus.load_clean` has 93 importers,
   `fingerprint_battery.lp_words` 53, `walk_verifier.load_words` 28,
   `anomaly_scan.parse` 21, `body_parse`). Two recorded tokenizer bugs: a
   page break cut 34 blocks in two; a stale mark class returned 60 words
   instead of 2,928. One function returning runes with word, line, page and
   section ids and the closing mark. Open question: whether blocks join
   across page breaks by default. The 2026-08 survey put this in one shared
   experiments module rather than `src/`; the 2026-09 survey put it in
   `c3301`. Either way there must be exactly one.
2. **Lazy n-gram tables and an integer scorer.** `stats/compare.py` loads
   the English tables at import and `c3301.py` the runeglish ones, so any
   `aldegonde.stats` import costs 245 MB and 1.0 s and `c3301` 357 MB. 27
   scripts load the files themselves because the scorer takes strings. Load
   on first use; keep a dense `29^n` log-probability array (2.8 MB for
   quadgrams); score integer arrays in one call. Decide the floor for unseen
   n-grams first: the library uses `log10(0.01 / total)`, `quagmire_runner`
   uses `0.2 / total`. Check how the tables were built; they may predate the
   book's spelling.
3. **Word-structured null models.** `NullModel` is flat sequence in, flat
   sequence out, so it cannot keep word lengths. About 25 scripts shuffle
   text as a null at the word level: shuffle runes keeping lengths, shuffle
   inside each word, shuffle whole words, shuffle lengths keeping the
   stream. Each docstring should say what it keeps and what it destroys.
4. **Remaining count helpers.** Pair count `sum n(n-1)/2` over a counter
   (37 scripts), repeated-word pairs and their chance floor (6 scripts).
5. **Hill climbing.** 14 to 20 scripts climb; the deleted branch had a
   generic climber with an injected score and move, `multi_start`, and
   swap and conjugation moves. Sound design. Port it together with the
   first experiment migrated onto it, so the API is exercised.
6. **Filter cascade with a funnel report.** The sweeps chain cheap filters
   before an expensive verifier and should report how many candidates each
   stage passed; a stage that passes everything is dead weight, a cascade
   that passes nothing needs a planted key. The branch had a 73-line
   version.
7. **The length-clocked walk cipher** as a library cipher, once the
   permutation module has a user: `walk` and `step_products` have 6
   importers each.
8. **Keystream toolkit** (from the 2026-08 survey): an offset scan that
   standardizes each offset's score against the scan's own spread; the
   drift-tolerant Viterbi decryption; the key-index framing enumerator
   (reset per word, per section, never); the crib drag that tests the
   implied key fragment for structure. All additive-key tools. The Liber
   Primus work has excluded additive keys, so these serve the library, not
   the current research.
9. **Linear-relation scan** over a modular alphabet, `(x[i+d] + a x[i]) mod
   N` for every lag and coefficient. Same remark as 8.
10. **Spectral detectors**: FFT cross-correlation of two streams for the
    alignment at which they coincide most, and a multiplier DFT for
    non-integer periods. The first is general; the second assumes additive
    structure.
11. **Ciphertext-autokey repeat classes**: positions forced to share a
    plaintext symbol inside a repeated ciphertext run, key-independent.
    General; the autokey families are excluded for the Liber Primus.
12. **Integer sequences as keys**: primes, gaps, totients, Moebius,
    figurate numbers, Fibonacci and Lucas, behind one catalogue. 12 scripts;
    partly duplicates `maths.primes` and `maths.totient`.
13. **Repeat upgrades**: mismatch-tolerant maximal repeats with their
    analytic null; the repeat-distance factor spectrum; a point-process
    battery for event positions (CV, Fano factor, gap tests); the
    insertion-versus-occupation test for events in variable-length units.
14. **Small single-file wins** listed in the 2026-08 survey: conditional
    bigram entropy; compression against shuffled surrogates; mutual
    information at lags with the shuffle-bias baseline; bigram antisymmetry
    chi-square; the copy-versus-shared-key delta-mixture discriminator;
    a positional-crib dictionary matcher.
15. **A cipher zoo** of reference encryptors for simulation: Chaocipher-N,
    Gromark, Hill with rejection, Mealy machines, the progressive
    related-alphabet family, keyed-tableau autokey in its six modes, the
    accumulator autokey. Each should arrive with the experiment that needs
    it.

## Judged and not taken

- **Analytic multiple-testing corrections** (Bonferroni, Sidak, expected
  maximum z, a multiplicity budget). The project's own record is that scan
  maxima need surrogate nulls: `stats.family_pvalue` resamples the maximum
  and is the path to keep easy. Add the analytic forms only if a scan is
  too expensive to resample.
- **The fingerprint battery as a library object.** The branch's version had
  three cells; the experiments' has twenty and changes with the research.
  `monte_carlo_map` already compares a vector of statistics against a null.
- **Four-point coincidence.** `analysis.joint_coincidence` counts pairs of
  lag matches at a separation, which is the same statistic.
- **A histogram of modular symbol differences inside words.** Assumes an
  additive alphabet structure.
- **A word cutter from a length distribution.** The experiments cut to the
  book's own length sequence, which `analysis.recut_words` does.

## Standing defects the surveys found

- Scripts print conclusions as fixed strings that do not follow their own
  numbers.
- Constants copied from another script's output and typed in
  (`PROSE_D5 = 0.0550`, `MONOGRAPH_LR = 265.0`, `ENGLISH_FINAL = 1.19`).
- Figures quoted without a spread that move on the random seed alone.
- `random_isomorph_statistics` in `stats/isomorphs.py` uses a uniform
  null, which is the wrong null for doublet-suppressed text.
