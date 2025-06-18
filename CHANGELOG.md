# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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