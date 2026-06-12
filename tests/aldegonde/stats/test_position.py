"""Tests for the position-conditioned frequency chi-square test."""

import pytest

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.stats.position import PositionChiSquare, position_frequency_chi2


def test_position_dependence_detected() -> None:
    """When position 0 is always A and position 1 always B, both reject."""
    result = position_frequency_chi2(["AB"] * 100)
    assert len(result) == 2
    assert all(isinstance(r, PositionChiSquare) for r in result)
    assert result[0].chi2 == pytest.approx(100.0)
    assert result[0].pvalue < 1e-6
    assert result[1].pvalue < 1e-6


def test_no_position_dependence() -> None:
    """A symbol balanced across positions matches the marginal: chi2 ~ 0."""
    result = position_frequency_chi2(["AB", "BA"] * 50)
    assert len(result) == 2
    for r in result:
        assert r.chi2 == pytest.approx(0.0, abs=1e-9)
        assert r.pvalue == pytest.approx(1.0)


def test_min_count_skips_short_positions() -> None:
    """Positions with fewer than min_count symbols are omitted."""
    assert position_frequency_chi2(["AB", "AB"]) == []
    result = position_frequency_chi2(["AB", "AB"], min_count=1)
    assert len(result) == 2


def test_from_end_alignment() -> None:
    """from_start=False indexes positions from the end of each token."""
    result = position_frequency_chi2(
        ["XYB", "ZB"],
        from_start=False,
        min_count=1,
    )
    assert [r.position for r in result] == [0, 1, 2]
    assert result[0].n == 2  # both tokens end in B
    assert result[2].n == 1  # only the longer token reaches position 2


def test_max_position_caps_positions() -> None:
    """max_position limits how many positions are examined."""
    result = position_frequency_chi2(["ABCDE"] * 60, max_position=2)
    assert [r.position for r in result] == [0, 1]


def test_empty_tokens_raises() -> None:
    """No tokens means no data to analyze."""
    with pytest.raises(InsufficientDataError):
        position_frequency_chi2([])


def test_invalid_min_count_raises() -> None:
    """A non-positive min_count is rejected."""
    with pytest.raises(InvalidInputError):
        position_frequency_chi2(["AB", "AB"], min_count=0)
