"""Tests for the in-depth (key-reuse) alignment coincidence test."""

import pytest

from aldegonde.analysis.indepth import AlignmentResult, alignment_coincidence
from aldegonde.exceptions import InsufficientDataError, InvalidInputError

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_identical_units_all_coincide() -> None:
    """Two identical units coincide in every column with a large positive z."""
    result = alignment_coincidence(["ABCDE", "ABCDE"], alphabetsize=26)
    assert isinstance(result, AlignmentResult)
    assert result.opportunities == 5
    assert result.hits == 5
    assert result.expected == pytest.approx(5 / 26)
    assert result.z_score > 5


def test_left_alignment_compares_prefixes() -> None:
    """Left alignment compares from the start; a shared suffix does not count."""
    result = alignment_coincidence(["ABC", "ZZABC"], alphabetsize=26, align="left")
    assert result.opportunities == 3
    assert result.hits == 0


def test_right_alignment_compares_suffixes() -> None:
    """Right alignment compares from the end; a shared suffix coincides fully."""
    result = alignment_coincidence(["ABC", "ZZABC"], alphabetsize=26, align="right")
    assert result.opportunities == 3
    assert result.hits == 3


def test_no_coincidence_gives_negative_z() -> None:
    """Disjoint units sit below the chance expectation."""
    result = alignment_coincidence(["AB", "CD"], alphabetsize=26)
    assert result.hits == 0
    assert result.z_score < 0


def test_alphabetsize_autodetect() -> None:
    """alphabetsize=0 infers the alphabet from the units."""
    result = alignment_coincidence(["AB", "AB"], alphabetsize=0)
    assert result.expected == pytest.approx(1.0)  # opp=2, two symbols


def test_min_length_filters_short_units() -> None:
    """Units shorter than min_length are dropped before pairing."""
    result = alignment_coincidence(
        ["A", "ABCDE", "ABCDE"],
        alphabetsize=26,
        min_length=2,
    )
    assert result.opportunities == 5
    assert result.hits == 5


def test_three_units_pool_all_pairs() -> None:
    """Opportunities pool over every pair of units."""
    result = alignment_coincidence(["AB", "AB", "AB"], alphabetsize=26)
    assert result.opportunities == 6  # three pairs, two columns each
    assert result.hits == 6


def test_fewer_than_two_units_raises() -> None:
    """A single qualifying unit cannot form a pair."""
    with pytest.raises(InsufficientDataError):
        alignment_coincidence(["ABCDE"], alphabetsize=26)


def test_invalid_align_raises() -> None:
    """An unknown alignment is rejected."""
    with pytest.raises(InvalidInputError):
        alignment_coincidence(["AB", "AB"], alphabetsize=26, align="middle")
