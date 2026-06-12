"""Tests for the higher-order coincidence statistic."""

import pytest

from aldegonde.analysis.coincidence import joint_coincidence, match_indicator
from aldegonde.exceptions import InsufficientDataError, InvalidInputError


def test_match_indicator_basic() -> None:
    """M[i] is True where a symbol repeats at the given lag."""
    assert match_indicator("ABCABC", 3) == [True, True, True]
    assert match_indicator("ABCD", 1) == [False, False, False]
    assert match_indicator("AAAA", 1) == [True, True, True]


def test_joint_coincidence_all_match() -> None:
    """In a constant stream every lag-1 match is adjacent to the next."""
    assert joint_coincidence("AAAA", 1, [1, 2]) == {1: 2, 2: 1}


def test_joint_coincidence_isolated_matches() -> None:
    """Matches that never sit at separation 1 contribute zero there."""
    assert joint_coincidence("AABBA", 1, [1, 2]) == {1: 0, 2: 1}


def test_separation_beyond_indicator_is_zero() -> None:
    """A separation wider than the match stream yields zero, not an error."""
    assert joint_coincidence("AAAA", 1, [10]) == {10: 0}


def test_match_indicator_invalid_lag_raises() -> None:
    """A non-positive lag is rejected."""
    with pytest.raises(InvalidInputError):
        match_indicator("AAAA", 0)


def test_match_indicator_short_text_raises() -> None:
    """Text no longer than the lag has no comparable pairs."""
    with pytest.raises(InsufficientDataError):
        match_indicator("AB", 3)


def test_joint_invalid_separation_raises() -> None:
    """A non-positive separation is rejected."""
    with pytest.raises(InvalidInputError):
        joint_coincidence("AAAA", 1, [0])
