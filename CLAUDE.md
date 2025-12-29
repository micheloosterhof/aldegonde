# CLAUDE.md - AI Assistant Guide for Aldegonde

## Project Overview

**Aldegonde** is a Python library for classical cryptography and cryptanalysis. It is designed to accommodate non-standard alphabets (not limited to A-Z), making it particularly useful for analyzing cipher systems with custom character sets like runes.

The library includes:
- Classical cipher implementations (monoalphabetic, polyalphabetic, autokey)
- Statistical analysis tools for cryptanalysis
- Specialized support for Cicada 3301 / Liber Primus analysis
- Mathematical utilities for cryptographic operations

## Repository Structure

```
aldegonde/
├── src/aldegonde/           # Main library source code
│   ├── __init__.py
│   ├── py.typed             # PEP 561 typed package marker
│   ├── masc.py              # Monoalphabetic substitution ciphers
│   ├── pasc.py              # Polyalphabetic substitution ciphers
│   ├── pgsc.py              # Polygraphic substitution ciphers
│   ├── auto.py              # Autokey ciphers
│   ├── trns.py              # Transposition ciphers
│   ├── disk.py              # Cipher disk operations
│   ├── column.py            # Columnar operations
│   ├── c3301.py             # Cicada 3301 specific functions
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── validation.py        # Input validation utilities
│   ├── analysis/            # Cryptanalysis algorithms
│   │   ├── __init__.py      # Exports: friedman_test, bigram_break_pasc, twist, etc.
│   │   ├── friedman.py      # Friedman test for period detection
│   │   ├── guballa.py       # Guballa attack
│   │   ├── twist.py         # Twist analysis
│   │   └── split.py         # Text splitting utilities
│   ├── stats/               # Statistical analysis
│   │   ├── __init__.py      # Exports: ioc, kappa, ngrams, entropy, etc.
│   │   ├── ioc.py           # Index of Coincidence
│   │   ├── kappa.py         # Kappa test
│   │   ├── ngrams.py        # N-gram analysis
│   │   ├── entropy.py       # Entropy calculations
│   │   ├── hamming.py       # Hamming distance
│   │   └── ...
│   ├── maths/               # Mathematical utilities
│   │   ├── __init__.py      # Exports: primes, factor_pairs, gcd, etc.
│   │   ├── primes.py        # Prime number operations
│   │   ├── factor.py        # Factorization
│   │   ├── modular.py       # Modular arithmetic
│   │   ├── totient.py       # Euler's totient
│   │   └── moebius.py       # Moebius function
│   ├── grams/               # N-gram visualization
│   │   ├── bigram_diagram.py
│   │   └── color.py
│   ├── data/                # Data files and n-gram tables
│   │   └── ngrams/
│   │       ├── english/
│   │       └── runeglish/
│   └── fitness/             # Fitness functions for optimization
├── tests/aldegonde/         # Test suite (mirrors src structure)
│   └── test_hypothesis.py   # Property-based tests with Hypothesis
├── examples/                # Example scripts
│   └── lp_analysis.py       # Liber Primus analysis script
├── data/                    # External data files (Liber Primus, etc.)
├── docs/                    # Documentation
└── lp_section_data.py       # Liber Primus section metadata
```

## Development Workflow

### Setup

```bash
# Install package with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with pytest
pytest tests/aldegonde -v

# Run with coverage
pytest --cov=aldegonde tests/aldegonde

# Run full test suite with tox (multiple Python versions)
tox

# Run specific test environment
tox -e py310      # Python 3.10 tests
tox -e lint       # Linting only
tox -e typing     # Type checking only
```

### Linting

```bash
# Run ruff linter
ruff check src/

# Auto-fix issues
ruff check src/ --fix
```

### Type Checking

```bash
# Run mypy (strict mode configured in pyproject.toml)
mypy src/
```

### Code Formatting

```bash
# Format with ruff
ruff format src/ tests/
```

## Code Conventions

### Type Annotations

The project uses **strict mypy configuration** and is a PEP 561 typed package (`py.typed`). All functions require:
- Full type annotations for parameters and return types
- Generic type parameters using `TypeVar`
- Use `Sequence[T]` for read-only sequences, `list[T]` for mutable

```python
from typing import TypeVar
from collections.abc import Sequence, Generator

T = TypeVar("T")

def example(text: Sequence[T], key: dict[T, T]) -> Generator[T, None, None]:
    ...
```

### Exception Handling

Use the custom exception hierarchy defined in `src/aldegonde/exceptions.py`:

- `AldegondeError` - Base exception for all library errors
- `CipherError` - Cipher operation failures
- `AldegondeKeyError` - Invalid encryption/decryption keys
- `AlphabetError` - Invalid alphabet configurations
- `InvalidInputError` - General invalid input
- `StatisticalAnalysisError` - Statistical analysis failures
- `InsufficientDataError` - Not enough data for analysis
- `MathematicalError` - Mathematical computation errors

### Input Validation

Use validation functions from `src/aldegonde/validation.py`:

```python
from aldegonde.validation import (
    validate_alphabet,
    validate_text_sequence,
    validate_key_length,
    validate_positive_integer,
)
```

### Generator Pattern

Cipher functions typically use generators for memory efficiency:

```python
def masc_encrypt(plaintext: Iterable[T], key: dict[T, T]) -> Generator[T, None, None]:
    for e in plaintext:
        yield key[e]

# Usage
ciphertext = list(masc_encrypt(plaintext, key))
# or
ciphertext = "".join(masc_encrypt(plaintext, key))  # for strings
```

### Tabula Recta (TR)

Polyalphabetic ciphers use a tabula recta structure:

```python
TR = dict[T, dict[T, T]]  # TR[key_char][plaintext_char] = ciphertext_char
```

### Docstrings

Use Google-style docstrings with Args, Returns, Raises sections:

```python
def function(param: int) -> str:
    """Short description.

    Longer description if needed.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        SomeError: When this error occurs
    """
```

## Key Modules

### masc.py - Monoalphabetic Substitution

- `masc_encrypt()` / `masc_decrypt()` - Core encryption/decryption
- `shiftedkey()` - Caesar/ROT13 cipher keys
- `affinekey()` - Affine cipher keys
- `atbashkey()` - Atbash cipher keys
- `randomkey()` - Random substitution keys
- `mixedalphabet()` - Keyword-based alphabet mixing

### pasc.py - Polyalphabetic Substitution

- `pasc_encrypt()` / `pasc_decrypt()` - Core functions
- `vigenere_tr()` - Vigenere cipher tabula recta
- `beaufort_tr()` - Beaufort cipher tabula recta
- `quagmire1_tr()` through `quagmire4_tr()` - Quagmire variants

### c3301.py - Cicada 3301 Support

- `CICADA_ALPHABET` - 29 Elder Futhark runes
- `CICADA_ENGLISH_ALPHABET` - English letter mappings
- `r2i()`, `i2r()`, `r2v()`, `v2r()` - Rune/index/value conversions
- N-gram scorers for runeglish text

### stats/ - Statistical Analysis

Import directly from the package: `from aldegonde.stats import ioc, kappa, ngrams`

- `ioc` - Index of Coincidence calculations
- `kappa` - Kappa test for period detection
- `ngrams`, `bigrams`, `trigrams` - N-gram analysis
- `shannon_entropy` - Shannon entropy
- `hamming_distance` - Hamming distance calculations
- `repeat_positions`, `repeat_distribution` - Repeated sequence analysis

### analysis/ - Cryptanalysis

Import directly from the package: `from aldegonde.analysis import friedman_test`

- `friedman_test` - Friedman test for determining cipher key length
- `bigram_break_pasc` - Guballa's attack on polyalphabetic ciphers
- `twist`, `twist_test` - Twist analysis for detecting patterns

### maths/ - Mathematical Utilities

Import directly from the package: `from aldegonde.maths import primes, prime_factors`

- `primes` - Prime number generation
- `prime_factors`, `factor_pairs` - Factorization
- `gcd`, `is_coprime`, `phi_func` - Number theory functions

## Testing Patterns

Tests mirror the source structure under `tests/aldegonde/`. The project uses **Hypothesis** for property-based testing:

```python
# tests/aldegonde/test_hypothesis.py
from hypothesis import given
from hypothesis import strategies as st
from aldegonde import masc

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

@given(st.text(alphabet=ABC, min_size=1, max_size=100))
def test_caesar_roundtrip(plaintext: str) -> None:
    """Test that Caesar cipher encryption and decryption are inverse operations."""
    key = masc.shiftedkey(ABC, shift=3)
    ciphertext = list(masc.masc_encrypt(plaintext, key=key))
    decrypted = list(masc.masc_decrypt(ciphertext, key=key))
    assert list(plaintext) == decrypted
```

## CI/CD

GitHub Actions workflow (`.github/workflows/tox.yml`) runs on push/PR:
- Tests against Python 3.10, 3.11, 3.12, 3.13
- Linting with ruff (Python 3.10)
- Type checking with mypy (Python 3.10)

## Common Commands Quick Reference

```bash
# Setup
pip install -e ".[dev]"            # Install with dev dependencies

# Testing
pytest tests/aldegonde -v          # Run tests
pytest --cov=aldegonde             # Run with coverage
tox                                # Full test matrix

# Code quality
ruff check src/                    # Lint
ruff check src/ --fix              # Lint + autofix
mypy src/                          # Type check
ruff format src/ tests/             # Format

# Examples
python examples/lp_analysis.py     # Run Liber Primus analysis
```

## Important Notes for AI Assistants

1. **Alphabet Independence**: The library is designed for arbitrary alphabets. Don't assume 26-letter English alphabet.

2. **Generator Usage**: Many functions return generators, not lists. Convert with `list()` or `"".join()` when needed.

3. **Type Safety**: Maintain strict type annotations. The mypy config is strict. The package is PEP 561 typed.

4. **Exception Handling**: Use the custom exception hierarchy. Don't use bare `ValueError` or `KeyError`.

5. **Validation**: Validate inputs using functions in `validation.py` before processing.

6. **Rune Support**: When working with Cicada 3301 content, use `c3301.CICADA_ALPHABET` (29 runes).

7. **Performance**: N-gram scoring and statistical analysis can be expensive. Consider caching for repeated operations.

8. **Test Coverage**: Maintain comprehensive tests. The project uses Hypothesis for property-based testing.

9. **Module Imports**: Use package-level imports when possible: `from aldegonde.stats import ioc` instead of `from aldegonde.stats.ioc import ioc`.
