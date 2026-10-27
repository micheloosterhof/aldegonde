# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `alphabet.Alphabet`, a codec between symbols and integer indices, and
  `c3301.RUNES`, `c3301.encode_english`, `c3301.decode_english` for the
  Liber Primus
- `c3301.tokenize`, the one tokenizer for the transcription: rune indices with
  word, line, page and section ids and the mark that closed each word
- `maths.permutation`: compose, inverse, power, order, cycles, cycle type,
  parity, conjugation, random permutations, conversion to and from
  substitution keys
- `stats.binomial_z`, `stats.wilson_interval`, `stats.two_proportion_z`
- `stats.pair_counts`, `stats.relation_rate`, `stats.extremal_relation_rate`
- `stats.uniformity`, `stats.goodness_of_fit`, `stats.rate_uniformity`,
  `stats.independence`: chi-square tests that carry df, p and a normal-scale z
- `stats.kappa_spectrum` against the frequency-matched rate
- `stats.MarkovModel`, `stats.fit_markov`, and the generative null models
  `stats.markov_null`, `stats.fitted_markov`, `stats.doublet_markov`,
  `c3301.low_doublet_markov_null`
- `analysis.within_word_match_rate`, `analysis.bucket_coincidence`,
  `analysis.match_separations`
- `random_isomorph_statistics` takes a `null` model, so rune text can be
  scored against a doublet-suppressed null instead of a uniform one

### Changed
- Type checking moved from mypy to ty
- Python 3.10 dropped; 3.11 is the floor
- Development dependencies pinned to their current releases

### Removed
- `setup.py` and its mypyc build; the package builds from `pyproject.toml`
- `lp.py`, an unmaintained driver superseded by `examples/lp_analysis.py`
- `IMPROVEMENTS_TODO.md`, `REVIEW.md` and `TODO`; the one planning document is
  `docs/library-candidates.md`
- Sample texts moved from the repository root to `data/samples/`

### Earlier, also unreleased

### Added
- Comprehensive error handling hierarchy with structured exception classes
  - `AldegondeError` as base exception class for all library errors
  - `CipherError` for cipher-specific operations with cipher type context
  - `AldegondeKeyError` for key-related validation failures
  - `AlphabetError` for alphabet validation and compatibility issues
  - `InvalidInputError` for general input validation failures
  - `StatisticalAnalysisError` for statistical analysis operations
  - `InsufficientDataError` for operations requiring minimum data lengths
  - `MathematicalError` for mathematical computation failures
- Input validation framework across all cipher modules
  - Alphabet validation with duplicate detection
  - Text sequence validation with minimum length requirements
  - Key length validation for cipher operations
  - Tabula recta structure validation
  - Positive integer validation for mathematical functions
- Error handling integration in all cipher implementations:
  - Polyalphabetic substitution ciphers (pasc.py)
  - Monoalphabetic substitution ciphers (masc.py)
  - Autokey cipher variations (auto.py)
  - Transposition ciphers (trns.py)
  - Polygraphic substitution ciphers (pgsc.py)
  - Cipher disk implementations (disk.py)
  - Columnar transposition (column.py)
- Comprehensive test suite for error handling (48 new tests)

### Fixed
- Scytale cipher implementation now properly handles encryption/decryption operations
- All cipher modules now provide meaningful error messages instead of silent failures
- Input validation prevents invalid operations that could cause undefined behavior

### Changed
- Enhanced error reporting across all cryptographic functions
- Improved input validation with descriptive error messages
- Better handling of edge cases in cipher operations

## [Previous Releases]

This changelog was introduced with the error handling improvements. For previous release history, please refer to the git commit history.