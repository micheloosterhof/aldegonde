# Extraction candidates: `experiments/` → `src/aldegonde`

A survey of the ~120 scripts in `experiments/` looking for reusable,
generalizable cryptanalysis primitives worth promoting into the library.
Every candidate below is alphabet-agnostic (works for any symbol set, not
just A–Z or the 29-rune Cicada alphabet) and is judged by two signals:
how often it is re-implemented inline across experiment files
(duplication pressure), and whether it answers a question that recurs
outside the Liber Primus context.

Survey date: 2026-08-02.

**Status:** slice 1 (items 1–4 below) is extracted: `stats.nulls`
gained `markov_model`/`fitted_markov`/`doublet_markov` (with
`c3301.low_doublet_markov_null` as the LP-tuned wrapper),
`stats.chisq` and `stats.multitest` are new, `stats.kappa_spectrum`
covers the frequency-matched z-spectrum, `analysis.coincidence` gained
n-gram boundary coincidence, `match_separations`,
`within_delta_histogram`, and `bucket_coincidence`,
`analysis.relations` covers the linear/positional scans,
`analysis.bounds` the assignment doublet floor, and `aldegonde.perm`
the permutation algebra. Slice 2 (item 5) is extracted: `aldegonde.search`
holds the generic hill climber (`hill_climb`, `multi_start`, the
`swap`/`conjugation` neighborhoods) and the `filter_cascade` funnel, and
`analysis.autokey_repeat` holds the key-independent ciphertext-autokey
repeat constraint (`forced_equal_positions`, `count_violations`).
Experiment-file migration is still pending.

## Meta-findings

**Discoverability is half the problem.** `ioc`/`nioc` is re-implemented
inline in ~15 files, a prime `sieve()` in 4 (`lp_battery9.py:10`,
`lp_battery13.py:17`, `lp_battery14.py:18`, `lp_cryptodiagnostics.py:164`),
and keyword-mixed-alphabet construction in 3 — all of which already exist
in the library (`stats/ioc.py`, `maths/primes.py`, `masc.mixedalphabet`).
Extraction alone will not fix this; the library API needs to be the path
of least resistance from an experiment script.

**Extraction demonstrably works.** The newest experiments
(`lag11_depletion.py`, `lag5_word_boundary.py`) import
`analysis.coincidence.{boundary_coincidence, boundary_permutation_test,
joint_coincidence, match_indicator}`, `stats.nulls.doublet_shuffle`, and
`stats.resample.{monte_carlo_map, family_pvalue}` from previous extraction
rounds, and are markedly shorter and more legible than the older files
that hand-roll the same machinery.

**The "wrong null" lesson recurs and should be institutionalized.** Two
files independently document that a uniform-random null fabricates 4–5σ
artifacts that vanish under a doublet-rate-matched null:
`missed_tests.py:229` (isomorph excess) and `word_transform_census.py:162`
(transform-pair census). Any new scan API should make the correct null the
default and the look-elsewhere correction unavoidable.

---

## Tier 1 — highest duplication pressure, clearly general

### 1. Generative Markov surrogate null (constrained transitions)

**Copies (~10):** `delta5_generalization.py:80` (`surrogates`, batched
numpy), `aligned_kappa_nulls.py:90` (`gen_doublet_suppressed`),
`lag5_digraph_chase.py:93`, `lag5_freshlook.py:132`,
`isomorph_corrected.py:53` (`markov_sample`), `missed_tests.py:233`
(`gen_suppressed`), `phrase_repeats.py:82`, `word_transform_census.py:162`,
`transposition_link.py:114`, `depth_search.py:91`.

The single most-copied piece of code in `experiments/`. Every copy is the
LP-motivated special case (pin the self-transition probability to a
suppressed doublet rate), but the primitive to extract is the general
surrogate-data method: **generate sequences from a first-order Markov
model whose transition structure carries a known second-order nuisance
property**, so that downstream statistics are not credited for structure
the null already contains. Two constructors cover every use seen here:

- `markov_null(transitions)` — surrogates from a full transition matrix,
  typically fitted from the observed sequence (the order-1 surrogate
  standard in time-series analysis);
- a constrained variant that pins only the diagonal (self-transition)
  rate and leaves the rest uniform — the doublet case, one line on top.

Beyond 3301 this is the right null wherever a corpus has a known
bigram-level anomaly: Playfair-prepared plaintext (doubles split by a
filler), languages with different gemination rates, machine ciphers with
anti-repetition mechanisms. It is **not** the same as the existing
`stats/nulls.doublet_shuffle`, which is frequency-exact and
shuffle-based; these files need the *generative* form, plus a batched
`(n_surrogates, length)` vectorized variant for Monte Carlo loops.

**Home:** the general infrastructure — `markov_null(transitions)` and the
constrained-diagonal constructor — goes in `stats/nulls.py`. The
low-doublet specialization (the null pre-tuned to LP's suppressed doublet
rate) is 3301-specific and lives with the 3301 code
(`c3301.py` / the `c3301*` analysis modules), built on the general
constructor rather than beside it.

Companion nulls worth adding at the same time in `stats/nulls.py`:
the **within-segment shuffle** (`plaintext_lag5_pairing.py:93` — preserves
word length and composition, destroys morphology) and the analytic
pattern-class expectation under the Markov null (`pattern_census.py:62`,
falling-factorial labeling count).

### 2. Segment-aware coincidence statistics + boundary permutation null

**Copies (~10):** `within_word_d5.py:62`, `within_word_delta_mixture.py:76`,
`within_word_match_anatomy.py:69`, `within_word_phase_profile.py:81`,
`within_word_position_decomposition.py:71`, `d5_partial_leak.py:62`,
`solved_section_control.py:63`, `rune_s_lag5.py:75`,
`plaintext_control_corpus.py:116`, `word_lattice.py:34` (`bucket_kappa`).

Every file re-derives the same loops over a `(stream, word_id)` pair:

- within-segment lag-d match rate, and the within/cross-boundary split
- per-segment-length breakdown with exact binomial or Wilson intervals
- delta histogram at lag d (the full N-bin `Q` vector)
- digraph-repeats-at-distance-d (the XY..XY statistic)
- separation histogram of consecutive lag-d matches
  (`plaintext_lag5_pairing.py:38`, `thirty_symbol_battery.py:38` — a
  fourth-order statistic nothing in the library computes)
- pooled within-bucket coincidence for an arbitrary bucketing function
  (`word_lattice.py:34` — the general "do these positions share key?" test)

**Companion nulls:** the boundary (word-length) permutation null — keep
the symbol stream byte-identical, shuffle only the length sequence, re-cut
— exists in three independent copies (`within_word_d5.py:96`,
`within_word_delta_mixture.py:176`, `within_word_phase_profile.py:95`),
with the best, section-local version at `lag5_word_boundary.py:161`
(never moves matches across section seams). A closed-form analytic mean
for the within-segment distance-d null is at `rune_s_lag5.py:62`.

**Home:** extend `analysis/coincidence.py` around a `SegmentedSequence`
(stream + boundary index) abstraction; the null goes in `stats/nulls.py`.
Generalizes to any segmentation: words, lines, columns, messages.

### 3. Scan statistics and multiple-comparison discipline

A cluster of small, constantly re-derived pieces that belong together:

- **Kappa z-spectrum over all lags with a frequency-matched null**
  (`lag11_depletion.py:85` — uses p = Σf², strictly better than the 1/N
  null used elsewhere; also `obs_kappa_spectrum.py:12`,
  `gap_audit.py:78`, `jstream_battery.py:49`, `gf29_battery.py:57`).
- **Multiple-testing helpers** — every scan re-derives its own
  correction, and they belong in one small module:
  **Bonferroni** thresholds and budgets
  (`recurrence_scan.py:43` — `chi2.isf(alpha/ntests, df)` over the
  coefficient×lag grid; `lp_battery14.py:72` explicit test-count budget;
  `gf29_battery.py:94` lagged-Fibonacci scan; `jstream_battery.py:117`),
  **Šidák** correction (`lag11_depletion.py:202`), the
  **√(2 ln n) expected-max threshold** for z-spectra (4 verbatim copies:
  `jstream_battery.py`, `gf29_battery.py`, `pattern_census.py:81`,
  `residual_tests.py:97`), and the
  "observed vs expected count of |z| ≥ t" **multiplicity budget**
  (`lag11_depletion.py:119`). These are the analytic complements to the
  empirical family-wise `stats/resample.family_pvalue` that already
  exists: Bonferroni/Šidák when trials are cheap and the null is known,
  the resampled max when it is not.
- **Wilson-Hilferty chi²→z→p helper** — 4 verbatim copies
  (`obs_flat_ioc.py:17`, `obs_bigram_ioc.py:22`, `obs_dependence.py:12`,
  `obs_line_initial.py:18`).
- **Off-diagonal-masked chi²** — 3 copies (`alignment_scan.py:174`,
  `fourth_order_ciphers.py:79`, `obs_bigram_ioc.py:19`). Essential
  whenever the diagonal is contaminated by doublet suppression.
- **Exposure-weighted rate-uniformity chi²**
  (`doublet_placement.py:23` `chi2_uniform_rate`; hand-rolled again in
  `doublet_word_position.py:156` and `doublet_insertion_test.py:44`) —
  "do events cluster on axis X?" with unequal exposure per bin. Distinct
  from the existing `stats/position.py`, which tests frequencies, not
  rates.
- **Full N×N lag-contingency chi² scan** (`dependence_scan.py:30`,
  `obs_dependence.py:12`, `missed_tests.py:80`) — the omnibus dependence
  test that kappa (equality-only) cannot see, with the diagonal /
  off-diagonal split as an option.
- **Linear/affine functional uniformity scan** over
  `(C[i+d] + a·C[i]) mod N` and `(C[i] + a·i) mod N`
  (`dependence_scan.py:52`, `jstream_battery.py:117`,
  `gf29_battery.py:76`), and the 3-term lagged-Fibonacci /
  linear-recurrence scan with Bonferroni thresholds
  (`recurrence_scan.py:43`, `gf29_battery.py:94`) — the canonical
  LFSR / lagged-Fibonacci / affine-relation detector for any modulus.

**Home:** a new `stats/multitest.py` (Bonferroni, Šidák, expected-max,
multiplicity budget), a new `stats/chisq.py`, additions to
`stats/kappa.py`, and a new `analysis/relations.py` for the functional
scans.

### 4. Permutation algebra + doublet-rate bounds

**Copies (6 files, two dialects):** `walk_verifier.py:51`
(`compose`/`ppow`/`order` and `parity` at `:145`), `stay_slot_cipher.py:87`
(`perm_from_cycles`/`conj_swap`/`tune`), `two_gear_cipher.py:105`,
`length_clocked_cipher.py:23`, `mealy_cipher.py:33`
(derangements, Latin squares), `advance_doublet_floor.py:53`
(`cycle_structure`/`cycles_to_perm`).

The library (`masc.py`) has `cycles` and `mixedalphabet` but no
composition, inversion, powers, order, parity, cycle-type construction,
conjugate-swap mutation, derangements, or Latin squares — all needed for
any rotor/gear/progressive-cipher work.

The jewel on top: **the provable min/max doublet rate over all
substitutions for a given bigram matrix**, via Hungarian assignment
(`advance_doublet_floor.py:123` and `:130`; independently at
`related_alphabet_cipher.py:112` and `two_gear_cipher.py:216`), plus the
cycle-type-constrained variant by annealing
(`advance_doublet_floor.py:82`). This is a cipher-independent bound for
refuting whole mechanism classes ("no monoalphabetic step can produce a
doublet rate this low for this language"). Stated generally: given any
pair-weight matrix, the extremal diagonal mass over all permutations —
the same assignment bound answers "can a substitution step explain this
self-map rate?" for any language and any adjacency statistic, not just
LP's suppressed doublets. The inverse operation — tune a
permutation so a diagonal rate *hits a target* — is at
`final_orbit_walk.py:42` and `mechanism_discriminator.py:99`.
`parity` also enables an O(1) necessary-condition pre-filter for state
return (`walk_verifier.py:162`).

**Home:** new `aldegonde/perm.py` (pure algebra) with the bigram-bound
functions in `analysis/` (they need a bigram matrix, optionally scipy).

### 5. Hill-climbing solver framework

**Copies (3 near-identical + 1 variant):** `quagmire_hillclimber.py:119`,
`quagmire_az_hillclimber.py:152`, `quagmire_repeat_attack.py:204` — all
implement (injected score function, swap-two neighborhood, best-tracking,
stagnation counter, random restarts) plus a `multiprocessing.Pool`
job-grid driver. A fourth dialect (`tune`/`conj_swap` hill-climb over
permutations under a fixed cycle type) lives in `stay_slot_cipher.py:106`
and is imported by `mechanism_discriminator.py`, `final_orbit_walk.py`,
and `phase_absorbing_walk.py`. The library has **no** solver module.

Proven companions worth extracting with it:

- **Repeat-consistency structural constraint for autokey ciphers**
  (`quagmire_repeat_attack.py:42,55,129`): for ciphertext autokey,
  identical ciphertext runs must decrypt to identical plaintext tails
  from position 2 on, regardless of the preceding symbol — a
  key-independent validity check, and occurrences with differing
  predecessors yield alphabet constraint pairs. Composite scorer
  "n-gram fitness − structural-violation penalty" at `:177`.
- **Cheap→expensive filter cascade with round-trip self-test**
  (`walk_verifier.py:129,162,176,187,284`): parity pre-filter →
  state-return hard filter → diagonal score → n-gram hill-climb, with a
  self-test that plants a known key, confirms the cascade accepts it and
  rejects random keys. The self-test idiom should be a library
  convention for any keyspace search.
- **Allocation-free fast IoC scorer** for inner loops
  (`quagmire_hillclimber.py:94` `score_ioc_fast`) — genuinely missing;
  the current `stats/ioc.py` allocates per call.

**Home:** new `aldegonde/search/` subpackage.

---

## Tier 2 — strong, 2–6 occurrences

### 6. Fingerprint battery / mechanism kill-table

**Copies (6+):** `mechanism_fingerprint.py:375`, `lp_battery11.py:34`,
`stay_slot_cipher.py:188` (`battery`), `two_gear_cipher.py:174`,
`product_form_ciphers.py:136`, `inner_layer_sim.py:152` (`j_stats`),
`period5_quagmire_sim.py:122`, `mechanism_discriminator.py:66`
(`profile`), `fourth_order_ciphers.py:65`.

One call computing a named vector of discriminating statistics — nIoC,
doublet/triplet rates, kappa spectrum, within-segment coincidence profile
d=1..k, column IoCs, paired-match counts, delta chi² — plus a
comparison-table printer. Turns "is my ciphertext consistent with
mechanism X?" into: simulate X, fingerprint both, compare. The
weighted-distance scoring + parameter grid search variant is at
`five_block_simulator.py:113`.

**Home:** `analysis/fingerprint.py`, built on the Tier-1 statistics.

### 7. Keystream attack toolkit

Spread over ~8 files:

- **Integer-sequence keystream catalogue mod N** — primes, prime gaps,
  totient, Möbius, divisor sums, Fibonacci/Lucas/tribonacci, figurate
  numbers, π/e digits, 2^i (`lp_battery13.py:44` `STREAMS`,
  `number_sequence_keys.py:61`, `lp_battery14.py:37`,
  `lp_battery9.py:36`). Natural extension of `aldegonde/maths/`.
- **Keystream-strip scan** over {sequence × offset × sign} scored by
  IoC/log-likelihood with an empirical Monte-Carlo null and
  multiple-comparison threshold (`totient_strip.py:57`,
  `lp_battery14.py:53`). The **self-calibrating empirical null** — derive
  z from the distribution of wrong-offset scores instead of modeling the
  null analytically (`lp_battery14.py:62`) — is the reusable trick, and
  applies to every brute-force scan in the repository. Positive-control
  sanity check on a known-solved input at `lp_battery14.py:75`.
- **Interrupter/drift-tolerant keystream decryption** — exact Viterbi DP
  over a monotone non-decreasing key-index drift with skip penalty
  (`lp_battery9.py:80`), beam-search fallback for non-monotone interrupts
  (`lp_attack_battery.py:78`), and the event-driven key-index map
  abstraction (`lp_battery13.py:56` `key_indices`).
- **Key-index framing enumerator** — reset per word / per section / never
  (`number_sequence_keys.py:143`) — orthogonal to the sequence choice,
  applies to any running-key attack.
- **Crib drag that tests the implied key fragment** for structure
  (constant, arithmetic, low-entropy) instead of scoring plaintext,
  with length-matched random-fragment nulls (`lp_battery15.py:61,85,98`).
- **Autokey depth-split detector** — partition positions by the symbol at
  lag L, pool per-group nIoC with numerator/denominator accumulation
  (3 copies: `gap_audit.py:53` `split_depth` ≡ `lag5_digraph_chase.py:79`
  `split_test`; `autokey_test.py:31`; generalized to arbitrary
  conditioning tuples in `lp_cryptodiagnostics.py:588`). The **joint
  multi-tap split test** (`product_form_ciphers.py:165`) — group C(n) by
  a tuple of history taps and take the weighted mean group nIoC — is the
  strongest form: one number falsifies the entire class of deterministic
  `C(n) = f(P(n), history)` ciphers injective in P(n).
- **Difference-stream depth search** with the analytic nIoC standard
  deviation `sd = √(2(N−1)/(n(n−1)))` (scales as 1/n, easy to get wrong)
  and the expected IoC of a difference of two texts
  (`depth_search.py:31–64`).

**Home:** new `analysis/keystream.py` + `maths/sequences.py`.

### 8. Simulation kit: Markov corpus generator + cipher zoo

- **Markov plaintext generator from n-gram tables** — 4+ copies
  (`inner_layer_sim.py:36` order-2/3 with smoothing,
  `mechanism_fingerprint.py:79`, `lp_battery11.py:18`,
  `period5_quagmire_sim.py:44`, `stay_slot_cipher.py:45`). The library
  ships `data/ngrams/*` but has no sampler.
- **Word cutter from an empirical length distribution** — 4 copies
  (`period5_quagmire_sim.py:75`, `stay_slot_cipher.py:71`, others).
- **Greedy longest-match multigraph transliterator** (English → target
  alphabet with digraph/trigraph rules) — appears in **8 files**
  (`runeglish_frequency.py:71`, `plaintext_control_corpus.py:209`,
  `quagmire_bigram_test.py:30`, `lp_attack_battery.py:116`,
  `lp_battery15.py:28`, `product_form_ciphers.py:54`, …).
- **Cipher zoo** — reference encryptors the library lacks entirely,
  useful as null/comparison mechanisms: Chaocipher-N
  (`lp_battery11.py:139`), Gromark chain-addition (`lp_battery11.py`),
  Hill with internal rejection (`group_size_tests.py:145`), Mealy /
  state-machine ciphers (`mealy_cipher.py:137`), bit-fractionation for
  prime alphabets (`mechanism_fingerprint.py:188`), GF(N²) seriation
  (`mechanism_fingerprint.py:216`), Lorenz-style wheel machine
  (`mechanism_fingerprint.py:262`), progressive related-alphabet family
  `A_φ = base ∘ g^φ` (`related_alphabet_cipher.py:133`,
  `phase_absorbing_walk.py:40`), keyed-tableau (Quagmire III) autokey
  (`custom_autokey_analysis.py:36`, `verify_quagmire_hypothesis.py:75`,
  `quagmire_hillclimber.py:38` — mode {vigenère, beaufort, variant} ×
  feedback {ciphertext, plaintext}), accumulator/running-sum autokey
  (`accumulator_autokey_test.py:35`), homophonic-with-cycling and
  keystream-rewind (`fourth_order_ciphers.py:97,136`), length-clocked
  progressive substitution (`length_clocked_cipher.py:43`).

**Home:** new `aldegonde/sim/` for generation; the cipher variants that
are real ciphers (Chaocipher, Gromark, keyed-tableau autokey,
accumulator autokey) belong in `auto.py`/`pasc.py`/new modules with
round-trip tests.

### 9. Higher-order and spectral detectors

Each appears only once or twice but fills a structural blind spot:

- **4-point statistic family P/V/X with closed-form expectations and a
  global max-z look-elsewhere null** (`fourpoint_dragnet.py:64–104`,
  null at `:117`; the P(L,1) scan reappears at
  `fourth_order_ciphers.py:85`). Pure symbol-equality templates over any
  alphabet; the statistic class relevant to Zodiac-340-style
  transposition+homophonic ciphers, invisible to everything currently in
  the library.
- **FFT one-hot cross-correlation** — O(n log n) coincidence between two
  streams at *every* alignment (`deep_scan.py:114`) — the general
  keystream/pad-reuse detector; companion to `analysis/indepth.py`,
  which only handles boundary-aligned units.
- **Multiplier DFT scan** — for each multiplier m, FFT of
  `exp(2πi·m·C/N)` with the Exp(1) per-bin null and max-order-statistic
  threshold (`spectral_scan.py:38`) — detects additive periodic
  structure at non-integer periods that Kasiski and integer-lag kappa
  miss.
- **Family-blind (lag × separation) pair-count grid** with an honest
  "does *any* lag carry two cells ≥ observed" Monte Carlo
  (`lag5_freshlook.py:116,130`); the chosen-family variant
  `joint_t` is at `lag5_digraph_chase.py:57`.
  `analysis/coincidence.joint_coincidence` covers only the chosen-family
  case today.
- **Discrete-log toolkit for prime-field alphabets**
  (`gf29_battery.py:39–130`): dlog table from a primitive root,
  power-residue character projections, character DFT — converts
  multiplicative cipher hypotheses into additive ones the existing
  tooling can already attack. Pairs with GF(p) `inv`/`safe_div`
  (`gf29_mult_autokey.py:36`).

### 10. Repeats and point-process upgrades

- **Mismatch-tolerant seed-and-extend maximal repeats** with the
  analytic null `pairs·C(L−1,k)·p^(L−k)·q^k`
  (`sentence_forensics.py:183,226,243`); exact-maximal-repeat classes
  with `expected_by_chance(n,k) = n²/(2·N^k)`
  (`ciphertext_collisions.py:37,71`); bidirectional extension with
  word-boundary-pattern agreement (`anchored_repeats.py:34`).
  `stats/repeats.py` and `analysis/kasiski.py` only handle exact repeats
  and distances.
- **Repeat-distance factor spectrum with excess-over-1/f ranking**
  (`lp_repeat_analysis.py:158`) — a quantitative Kasiski presentation.
- **Point-process battery for event positions** (doublets, marks,
  match clusters): CV, Fano factor over several bin widths,
  KS-vs-exponential gaps, DFT peak ratio vs ln(n/2), GCD-of-gaps lattice
  test, gaps mod N (`doublet_spacing.py:52–115`,
  `mark_forensics.py:102–191`, `lp_cryptodiagnostics.py:474`).
- **Context chi² around events** vs corpus (not uniform) frequency —
  4 copies (`group_size_tests.py:50` `cat_test`,
  `mark_thirty_symbol.py:46`, `lp_cryptodiagnostics.py:441`,
  `lp_deep_analysis.py:70`).
- **Insertion-vs-occupation test** for events in variable-length units
  (length-weighted host-selection Monte Carlo,
  `doublet_insertion_test.py:58`).

---

## Small clean wins (low effort, single-file but general)

- Wilson score confidence interval, dependency-free
  (`within_word_position_decomposition.py:59`), and the bucketed-rate
  homogeneity reporter with FLAT/STRUCTURE verdict (`:81,93`).
- Two-proportion z for "does the effect respect boundaries?"
  (`obs_doublet_suppression.py:37`).
- Conditional bigram entropy H(X₂|X₁) (`obs_entropy.py:19`) and the
  compression-vs-shuffled-surrogate z across zlib/bz2/lzma
  (`obs_entropy.py:36`, `lp_cryptodiagnostics.py:538`).
- Mutual information at lags with the shuffle bias baseline
  (`lp_cryptodiagnostics.py:557`) — finite-sample MI bias is non-zero,
  the shuffle baseline is the correction.
- Expressible-set / numerical-semigroup DP, 2 copies
  (`boundary_tiling.py:52`, `cotiling_test.py:46`), plus the
  inter-family grid-consistency test (`cotiling_test.py:56`).
- Bigram antisymmetry chi² — count(a,b) vs count(b,a)
  (`deep_scan.py:125`, `lp_cryptodiagnostics.py:487`).
- Best shift×flip (atbash) distribution fit vs a reference, with an MC
  null that accounts for minimizing over 2N transforms
  (`covert_channels.py:64`).
- Affine-normalized n-gram canonical signature — repeats invariant under
  `y = m·x mod N` (`covert_channels.py:96`); modular sibling of
  `stats/isomorph.py`.
- Prev-occurrence-distance isomorph encoding, windowed
  (`isomorph_corrected.py:26`) — and note `random_isomorph_statistics`
  in `stats/isomorph.py` uses a uniform null, which `missed_tests.py`
  shows is the wrong null for doublet-suppressed text.
- Copy-vs-key-sharing delta-mixture discriminator: two one-parameter ML
  models, an orthogonal projection statistic, pinned-parameter rejection,
  and a bootstrap power calculation
  (`within_word_delta_mixture.py:88–227`) — the template for "is this
  coincidence excess a literal copy or a shared key?".
- Positional-crib dictionary matcher — index a lexicon by
  (length, fixed-symbol positions) (`ea_crib.py:72`).
- Grid-built order-k permutation from a keyword (`enumerate_keys.py:67`),
  mirror/palindrome+atbash symmetry z (`anomaly_scan.py:261`),
  shortest-window-containing-all-symbols with MC null
  (`deep_scan.py:204`), circular mean-resultant concentration of deltas
  (`deep_scan.py:168`), block untransposition helper
  (`transposition_link.py:85`).

## Explicitly not worth extracting

- LP corpus loaders and the `%`/`$` parsing idiom (~12 files): they
  encode transcription conventions, not cryptanalysis. They should
  collapse into **one** shared experiments-local module, not into
  `src/aldegonde`.
- `ocr_verify.py`: an excellent forced-alignment transcription-QA
  pipeline, but out of scope for a cryptanalysis library.
- Retracted or purely narrative files (`lag5_two_faces.py`,
  `lp_bigram_compare.py`), and Gematria-Primus-specific hypothesis code.
- Anything already in the library: inline `ioc`/`nioc`, sieves, totient,
  `mixedalphabet` duplicates — migrate the experiments to the library
  API instead.

## Discoverability plan

Extraction only pays off if the next experiment script — usually written
by an AI agent — reaches for the library instead of re-deriving the
primitive. The ~15 inline `ioc` copies happened *while the library
already had it*, so this needs explicit mechanisms:

1. **Directory-scoped agent guide** (done): `experiments/CLAUDE.md`
   carries a question → API lookup table for everything the library
   provides today, the corpus-loading conventions, and the standing
   rules (multiple-comparison discipline, correct-null discipline,
   self-test-your-attack). Agents working in `experiments/` load it
   automatically. **It must be updated in the same commit as every
   extraction slice** — a primitive that isn't in the table doesn't
   exist, as far as agents are concerned.
2. **Root `CLAUDE.md` pointer**: the project guide directs anyone
   writing analysis code to the lookup table before implementing
   helpers.
3. **Migrate experiments as each slice lands.** Agents pattern-match
   from neighboring files far more than from documentation; a directory
   where `lag11_depletion.py`-style library-importing scripts are the
   norm teaches the right habit by example. Migration doubles as the
   regression test for the extracted API.
4. **Question-oriented naming and docstrings.** Name functions after the
   question they answer (`boundary_coincidence`, `family_pvalue`), and
   put the recurring question in the first docstring line so grep and
   semantic search both land on it.
5. **Keep package-level exports complete.** Everything importable as
   `from aldegonde.stats import X` with `X` in `__all__`; sub-module
   paths (`aldegonde.stats.ioc.ioc`) are where discoverability goes to
   die.
6. **Optional CI tripwire**: a lint step that greps `experiments/` for
   definitions shadowing known library primitives (`def ioc`,
   `def nioc`, `def sieve`, `def mixedalphabet`, `def hill_climb`, …)
   and fails with a pointer to the lookup table.

## Suggested sequencing

1. **Core stats slice** (items 1–4): generative doublet-rate null,
   segment-aware coincidence + boundary-permutation null, chi²/scan
   discipline, permutation algebra + Hungarian doublet-floor bound.
   Highest duplication counts, pure statistics/algebra, zero 3301
   content, fits the existing `stats`/`analysis` architecture.
2. **Solver framework** (item 5): a new subsystem deserving its own
   design pass.
3. **Keystream toolkit + simulation kit** (items 6–8).
4. **Higher-order detectors and the small wins** (items 9–10), as needed
   by live investigations.

After each slice, migrate the experiment files that duplicate it — the
migration is both the regression test and the proof the API is usable.
