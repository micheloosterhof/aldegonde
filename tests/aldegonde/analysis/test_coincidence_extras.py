import pytest

from aldegonde.analysis.coincidence import (
    boundary_coincidence,
    bucket_coincidence,
    match_separations,
    within_delta_histogram,
)
from aldegonde.exceptions import InvalidInputError


def test_boundary_coincidence_digraph_counts_xyxy() -> None:
    # one word containing AB..AB at distance 3
    words = [list("ABXAB")]
    result = boundary_coincidence(words, 3, length=2)
    assert result.within_observed == 1
    assert result.within_pairs == 1
    assert result.across_pairs == 0


def test_boundary_coincidence_digraph_spanning_boundary_is_across() -> None:
    # the second AB spans the word boundary, so the pair is across-word
    words = [list("ABXA"), list("BY")]
    result = boundary_coincidence(words, 3, length=2)
    assert result.within_observed == 0
    assert result.within_pairs == 0
    assert result.across_observed == 1
    assert result.across_pairs == 2


def test_boundary_coincidence_length_one_unchanged() -> None:
    words = [list("ABA"), list("CAB")]
    a = boundary_coincidence(words, 2)
    b = boundary_coincidence(words, 2, length=1)
    assert a == b
    assert a.within_pairs + a.across_pairs == 4


def test_boundary_coincidence_invalid_length() -> None:
    with pytest.raises(InvalidInputError):
        boundary_coincidence([list("ABC")], 1, length=0)


def test_match_separations_histogram() -> None:
    # lag-1 matches (doublets) at indicator positions 0, 3, 4
    separations = match_separations("AAXBBBY", 1)
    assert separations == {3: 1, 1: 1}


def test_match_separations_respects_maximum() -> None:
    separations = match_separations("AAXBBBY", 1, max_separation=2)
    assert separations == {1: 1}


def test_match_separations_no_matches() -> None:
    assert match_separations("ABCDEF", 1) == {}


def test_within_delta_histogram_counts_by_delta() -> None:
    words = [list("ABA"), list("CAB"), list("ABA")]
    histogram = within_delta_histogram(words, "ABC", 1)
    # within-word lag-1 pairs: AB(+1) BA(+2) CA(+1) AB(+1) AB(+1) BA(+2)
    assert histogram == [0, 4, 2]


def test_within_delta_histogram_bin_zero_is_coincidences() -> None:
    words = [list("AAB"), list("CC")]
    histogram = within_delta_histogram(words, "ABC", 1)
    assert histogram[0] == 2


def test_within_delta_histogram_unknown_symbol_raises() -> None:
    with pytest.raises(InvalidInputError):
        within_delta_histogram([list("AX")], "AB", 1)


def test_bucket_coincidence_shared_key_positions_match() -> None:
    # positions with the same label always hold the same symbol
    result = bucket_coincidence("ABABAB", [0, 1, 0, 1, 0, 1])
    assert result.rate == 1.0
    assert result.pairs == 6


def test_bucket_coincidence_counts_pairs_correctly() -> None:
    # one bucket of 4 positions holding AABC: pairs C(4,2)=6, matches 1
    result = bucket_coincidence("AABC", [0, 0, 0, 0])
    assert result.pairs == 6
    assert result.observed == 1
    assert result.rate == pytest.approx(1 / 6)


def test_bucket_coincidence_singleton_buckets_have_no_pairs() -> None:
    result = bucket_coincidence("ABCD", [0, 1, 2, 3])
    assert result.pairs == 0
    assert result.rate == 0.0


def test_bucket_coincidence_length_mismatch_raises() -> None:
    with pytest.raises(InvalidInputError):
        bucket_coincidence("ABC", [0, 1])
