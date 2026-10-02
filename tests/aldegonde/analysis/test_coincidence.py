"""Tests for the higher-order coincidence statistic."""

import random

import pytest

from aldegonde.analysis.coincidence import (
    BoundaryCoincidence,
    BucketCoincidence,
    JointCount,
    WithinWordRate,
    boundary_coincidence,
    boundary_permutation_test,
    bucket_coincidence,
    joint_coincidence,
    match_indicator,
    match_separations,
    recut_words,
    within_word_match_rate,
    word_index_map,
)
from aldegonde.exceptions import InsufficientDataError, InvalidInputError


def test_within_word_match_rate_counts_only_inside_words() -> None:
    """Pairs are taken inside each word; the doublet in word 0 is the only match."""
    words = [[1, 1, 2], [3, 4]]
    result = within_word_match_rate(words, lag=1)
    assert result == WithinWordRate(matches=1, pairs=3, rate=1 / 3)


def test_within_word_match_rate_larger_lag_skips_short_words() -> None:
    """A word shorter than lag+1 offers no pair, so it never contributes."""
    words = [[5, 6, 5], [7, 8]]
    result = within_word_match_rate(words, lag=2)
    assert result == WithinWordRate(matches=1, pairs=1, rate=1.0)


def test_within_word_match_rate_no_pairs_is_zero() -> None:
    """With no available pair the rate is 0, not a division error."""
    assert within_word_match_rate([[1], [2]], lag=1) == WithinWordRate(0, 0, 0.0)


def test_within_word_match_rate_word_shorter_than_lag_adds_no_pairs() -> None:
    """A word shorter than the lag contributes zero pairs, never a negative count."""
    result = within_word_match_rate([[1, 2, 2, 1], [3]], lag=3)
    assert result == WithinWordRate(matches=1, pairs=1, rate=1.0)


def test_match_indicator_basic() -> None:
    """M[i] is True where a symbol repeats at the given lag."""
    assert match_indicator("ABCABC", 3) == [True, True, True]
    assert match_indicator("ABCD", 1) == [False, False, False]
    assert match_indicator("AAAA", 1) == [True, True, True]


def test_joint_coincidence_all_match() -> None:
    """In a constant stream every lag-1 match is adjacent to the next.

    The indicator is all True, so the match rate is 1 and the expected count
    equals the number of available pairs, matching the observed count.
    """
    assert joint_coincidence("AAAA", 1, [1, 2]) == {
        1: JointCount(observed=2, expected=2.0),
        2: JointCount(observed=1, expected=1.0),
    }


def test_joint_coincidence_isolated_matches() -> None:
    """Matches that never sit at separation 1 contribute zero observed there.

    For "AABBA" at lag 1 the indicator is [True, False, True, False]: length
    4, two matches, match rate 0.5. No two matches are adjacent, so observed
    at separation 1 is 0 against an expectation of 3 * 0.25 = 0.75. At
    separation 2 the two matches pair up, giving observed 1 against 2 * 0.25.
    """
    assert joint_coincidence("AABBA", 1, [1, 2]) == {
        1: JointCount(observed=0, expected=0.75),
        2: JointCount(observed=1, expected=0.5),
    }


def test_separation_beyond_indicator_is_zero() -> None:
    """A separation wider than the match stream has no available pairs."""
    assert joint_coincidence("AAAA", 1, [10]) == {
        10: JointCount(observed=0, expected=0.0),
    }


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


def test_word_index_map() -> None:
    """Every stream position is labeled with the index of its word."""
    assert word_index_map(["AB", "C", "DEF"]) == [0, 0, 1, 2, 2, 2]
    assert word_index_map([]) == []


def test_recut_words_roundtrip() -> None:
    """Cutting a concatenation at the original lengths restores the words."""
    words = [list("ABA"), list("C"), list("DE")]
    stream = [symbol for word in words for symbol in word]
    assert recut_words(stream, [3, 1, 2]) == words


def test_recut_words_rejects_bad_lengths() -> None:
    """Non-positive lengths and length-sum mismatches are invalid input."""
    with pytest.raises(InvalidInputError):
        recut_words("ABC", [3, 0])
    with pytest.raises(InvalidInputError):
        recut_words("ABC", [2, 2])


def test_boundary_coincidence_split() -> None:
    """Matches are classified by whether both positions share a word.

    For words ["ABA", "AB"] at lag 2 the stream is ABAAB with pairs
    (0,2) A=A inside the first word, (1,3) B/A and (2,4) A/B across the
    boundary. Only the first word is long enough to hold a lag-2 pair.
    """
    assert boundary_coincidence(["ABA", "AB"], 2) == BoundaryCoincidence(
        within_observed=1,
        within_pairs=1,
        across_observed=0,
        across_pairs=2,
    )


def test_boundary_coincidence_matches_plain_indicator() -> None:
    """Within plus across equals the plain lag-L match count."""
    words = ["ABCAB", "CA", "BCABC", "A"]
    stream = "".join(words)
    split = boundary_coincidence(words, 3)
    assert split.within_observed + split.across_observed == sum(
        match_indicator(stream, 3),
    )
    assert split.within_pairs + split.across_pairs == len(stream) - 3


def test_boundary_permutation_detects_word_aware_matches() -> None:
    """Planted within-word repeats are flagged as boundary-aware.

    The corpus is one section of 60 words: 30 words "XY123XY45" whose only
    lag-5 matches sit inside the word, alternating with 30 filler words
    chosen so that no other lag-5 match exists anywhere. Shuffling the
    word lengths destroys the alignment, so the observed count must sit
    far above the null.
    """
    section = ["XY123XY45", "678"] * 30
    result = boundary_permutation_test(
        [section], lag=5, permutations=200, rng=random.Random(1)
    )
    assert result.observed == 60
    assert result.observed > result.null_mean + 3 * result.null_sd
    assert result.p_value < 0.01


def test_boundary_permutation_blind_matches_are_not_flagged() -> None:
    """A periodic stream matches everywhere, so boundaries carry no signal.

    Every position of the stream is a lag-5 match, hence the within-word
    count depends only on the multiset of word lengths, which the shuffle
    preserves exactly: the null distribution is a point mass at the
    observed value and the p-value is 1.
    """
    stream = "ABCDE" * 24
    words = recut_words(stream, [7, 3, 5, 9, 6, 4, 8, 2, 11, 5, 60])
    result = boundary_permutation_test(
        [words], lag=5, permutations=100, rng=random.Random(2)
    )
    assert result.null_sd == 0.0
    assert result.observed == result.null_mean
    assert result.p_value == 1.0


def test_within_word_match_rate_counts_ngram_repeats() -> None:
    """Digraph XY..XY at lag 5 inside one word: 7 runes give one eligible pair."""
    word = [1, 2, 3, 4, 5, 1, 2]
    assert within_word_match_rate([word], lag=5, length=2) == WithinWordRate(1, 1, 1.0)
    assert within_word_match_rate([word], lag=5, length=3) == WithinWordRate(0, 0, 0.0)
    assert within_word_match_rate([word], lag=5) == WithinWordRate(2, 2, 1.0)


def test_within_word_match_rate_ngram_pairs_stay_inside_the_word() -> None:
    """The digraph straddling the boundary of two words is not a pair."""
    words = [[1, 2, 3], [1, 2, 3]]
    assert within_word_match_rate(words, lag=3, length=2).pairs == 0
    assert within_word_match_rate([[1, 2, 3, 1, 2, 3]], lag=3, length=2).pairs == 2


def test_within_word_match_rate_rejects_a_bad_length() -> None:
    with pytest.raises(InvalidInputError):
        within_word_match_rate([[1, 2, 3]], lag=1, length=0)


def test_bucket_coincidence_compares_positions_with_the_same_label() -> None:
    """Labels 'a' hold symbols 1,1,2 (one matching pair of three), 'b' holds 3,3."""
    result = bucket_coincidence([1, 1, 2, 3, 3], ["a", "a", "a", "b", "b"])
    assert result == BucketCoincidence(observed=2, pairs=4, rate=0.5)


def test_bucket_coincidence_with_one_label_is_the_pair_count_of_the_stream() -> None:
    stream = [1, 2, 1, 2, 1]
    result = bucket_coincidence(stream, [0] * 5)
    assert result.pairs == 10
    assert result.observed == 3 + 1  # three pairs of 1s, one pair of 2s


def test_bucket_coincidence_with_no_pairs_has_zero_rate() -> None:
    assert bucket_coincidence([1, 2], ["a", "b"]) == BucketCoincidence(0, 0, 0.0)


def test_bucket_coincidence_rejects_mismatched_labels() -> None:
    with pytest.raises(InvalidInputError):
        bucket_coincidence([1, 2, 3], ["a", "b"])


def test_match_separations_histograms_gaps_between_matches() -> None:
    """Lag-1 matches at positions 0, 1 and 4: gaps 1 and 3."""
    text = [7, 7, 7, 8, 9, 9]
    assert match_separations(text, lag=1) == {1: 1, 3: 1}


def test_match_separations_respects_max_separation() -> None:
    text = [7, 7, 7, 8, 9, 9]
    assert match_separations(text, lag=1, max_separation=2) == {1: 1}


def test_match_separations_with_fewer_than_two_matches_is_empty() -> None:
    assert match_separations([1, 2, 3, 4], lag=1) == {}
