"""Tests for rune frequency suppression analysis."""

import math

import pytest

from aldegonde.analysis.rune_frequency import (
    FrequencyProfile,
    find_best_suppression,
    matrix_mapping,
    natural_mapping,
    scan_state_spaces,
    truncated_byte_mapping,
)


class TestNaturalMapping:
    """Tests for the natural sequential mapping."""

    def test_perfect_division(self) -> None:
        """When total_states is a multiple of alphabet_size, all equal."""
        profile = natural_mapping(29 * 5, 29)
        assert all(v == 5 for v in profile.mapping.values())
        assert profile.suppressed_symbols == []

    def test_remainder_distributes_extras(self) -> None:
        """First `remainder` symbols get one extra pre-image."""
        # 169 = 5*29 + 24. Symbols 0-23 get 6, symbols 24-28 get 5.
        profile = natural_mapping(169, 29)
        assert profile.total_states == 169
        for s in range(24):
            assert profile.mapping[s] == 6
        for s in range(24, 29):
            assert profile.mapping[s] == 5

    def test_suppressed_symbols_are_tail(self) -> None:
        """In natural mapping, suppressed symbols are the last ones."""
        profile = natural_mapping(169, 29)
        assert profile.suppressed_symbols == [24, 25, 26, 27, 28]

    def test_256_to_29(self) -> None:
        """256 = 8*29 + 24. Symbols 0-23 get 9, symbols 24-28 get 8."""
        profile = natural_mapping(256, 29)
        for s in range(24):
            assert profile.mapping[s] == 9
        for s in range(24, 29):
            assert profile.mapping[s] == 8

    def test_symbol_0_not_suppressed_naturally_169(self) -> None:
        """In natural mapping of 169, symbol 0 is NOT suppressed."""
        profile = natural_mapping(169, 29)
        assert 0 not in profile.suppressed_symbols

    def test_symbol_0_not_suppressed_naturally_256(self) -> None:
        """In natural mapping of 256, symbol 0 is NOT suppressed."""
        profile = natural_mapping(256, 29)
        assert 0 not in profile.suppressed_symbols

    def test_states_sum(self) -> None:
        """Total pre-images must equal total_states."""
        for n in [100, 169, 256, 512, 841]:
            profile = natural_mapping(n, 29)
            assert sum(profile.mapping.values()) == n

    def test_invalid_alphabet(self) -> None:
        """Alphabet size must be >= 2."""
        with pytest.raises(ValueError, match="alphabet_size"):
            natural_mapping(100, 1)

    def test_invalid_states(self) -> None:
        """Total states must be >= 1."""
        with pytest.raises(ValueError, match="total_states"):
            natural_mapping(0, 29)


class TestMatrixMapping:
    """Tests for matrix_mapping."""

    def test_13x13_natural(self) -> None:
        """Default matrix_mapping uses natural mapping."""
        profile = matrix_mapping(13, 29)
        natural = natural_mapping(169, 29)
        assert profile.mapping == natural.mapping

    def test_all_states_assigned(self) -> None:
        """All states must be assigned to symbols."""
        for n in range(2, 15):
            profile = matrix_mapping(n, 29)
            assert sum(profile.mapping.values()) == n * n

    def test_explicit_suppression(self) -> None:
        """Custom suppressed_count is respected."""
        profile = matrix_mapping(13, 29, suppressed_symbol=0, suppressed_count=3)
        assert profile.mapping[0] == 3
        assert sum(profile.mapping.values()) == 169

    def test_suppressed_count_zero(self) -> None:
        """Symbol can be completely eliminated."""
        profile = matrix_mapping(13, 29, suppressed_symbol=0, suppressed_count=0)
        assert profile.mapping[0] == 0
        assert profile.expected_frequencies[0] == 0.0

    def test_invalid_alphabet_size(self) -> None:
        with pytest.raises(ValueError, match="alphabet_size"):
            matrix_mapping(13, 1)

    def test_invalid_suppressed_symbol(self) -> None:
        with pytest.raises(ValueError, match="suppressed_symbol"):
            matrix_mapping(13, 29, suppressed_symbol=30)


class TestTruncatedByteMapping:
    """Tests for truncated_byte_mapping."""

    def test_uniform_truncated(self) -> None:
        """Default gives uniform distribution via rejection."""
        profile = truncated_byte_mapping(29)
        assert profile.total_states == 232  # 8 * 29
        assert all(v == 8 for v in profile.mapping.values())

    def test_uniform_zero_chi_square(self) -> None:
        """Uniform distribution has chi-square of 0."""
        profile = truncated_byte_mapping(29)
        assert profile.chi_square == pytest.approx(0.0, abs=1e-10)

    def test_suppressed_uses_all_states(self) -> None:
        """With explicit suppression, all 256 states are used."""
        profile = truncated_byte_mapping(29, suppressed_count=4)
        assert profile.mapping[0] == 4
        assert sum(profile.mapping.values()) == 256

    def test_custom_byte_size(self) -> None:
        profile = truncated_byte_mapping(29, byte_size=512)
        assert profile.total_states == (512 // 29) * 29


class TestFrequencyProfile:
    """Tests for FrequencyProfile properties."""

    def test_frequencies_sum_to_one(self) -> None:
        for n in [100, 169, 256]:
            profile = natural_mapping(n, 29)
            total = sum(profile.expected_frequencies.values())
            assert total == pytest.approx(1.0, abs=1e-10)

    def test_max_entropy_for_uniform(self) -> None:
        """Uniform distribution achieves maximum entropy."""
        profile = truncated_byte_mapping(29)
        assert profile.entropy == pytest.approx(math.log2(29), abs=1e-10)

    def test_suppression_ratio(self) -> None:
        """Suppressed symbols have ratio < 1, boosted have ratio > 1."""
        profile = natural_mapping(169, 29)
        for s in profile.suppressed_symbols:
            assert profile.suppression_ratio[s] < 1.0
        for s in range(29):
            if s not in profile.suppressed_symbols:
                assert profile.suppression_ratio[s] >= 1.0


class TestScanStateSpaces:
    """Tests for scan_state_spaces."""

    def test_finds_suppression_points(self) -> None:
        """Should find state space sizes where symbol 0 is suppressed."""
        results = scan_state_spaces(29, max_states=100, target_symbol=0)
        # Symbol 0 is suppressed when remainder is 0 (perfect division,
        # all equal, no suppression) -- actually when remainder < alphabet
        # such that symbol 0 is NOT in the first `remainder` symbols.
        # Symbol 0 is suppressed when remainder == 0 (no symbols suppressed)
        # is NOT the case. Symbol 0 is suppressed when remainder == 0 means
        # all symbols equal so none suppressed. Symbol 0 is suppressed only
        # when it's NOT among first `remainder` symbols, i.e., never in
        # natural mapping since 0 < remainder for remainder > 0.
        # Actually symbol 0 is suppressed only when remainder == 0 (none
        # suppressed, so suppressed_symbols is empty and 0 is not in it).
        # Wait: suppressed means fewer than max. When remainder > 0,
        # symbols 0..remainder-1 get base+1, rest get base. So symbol 0
        # always gets the max (base+1) when remainder > 0. When remainder=0
        # all get base, suppressed_symbols=[], symbol 0 not suppressed.
        # So symbol 0 is NEVER suppressed in natural mapping!
        assert len(results) == 0

    def test_finds_high_symbol_suppression(self) -> None:
        """Symbol 28 should be frequently suppressed (last in sequence)."""
        results = scan_state_spaces(29, max_states=100, target_symbol=28)
        assert len(results) > 0
        # Symbol 28 is suppressed when remainder < 29 and remainder <= 28,
        # i.e., when remainder is 0..28 but 28 needs remainder <= 28.
        # Actually: symbol 28 gets base+1 only when 28 < remainder.
        # So suppressed when remainder <= 28, which is always (remainder
        # is 0..28). Except when remainder > 28, impossible for mod 29.
        # Symbol 28 is suppressed when remainder <= 28 AND remainder > 0.
        # When remainder=0, no suppression. When remainder=1..28, symbol 28
        # gets base (suppressed) unless remainder > 28 (impossible).
        # So symbol 28 is suppressed whenever remainder is 1..28.
        for total, remainder, ratio, suppressed in results:
            assert 28 in suppressed
            assert ratio < 1.0


class TestFindBestSuppression:
    """Tests for find_best_suppression."""

    def test_matches_known_frequency(self) -> None:
        """Should find count that matches a target frequency."""
        # Simulate observed: symbol 0 at 2% (below uniform ~3.45%)
        observed = {i: 1.0 / 29 for i in range(29)}
        observed[0] = 0.02
        total = sum(observed.values())
        observed = {k: v / total for k, v in observed.items()}

        count, profile = find_best_suppression(observed, 13, 29, 0)
        predicted = profile.expected_frequencies[0]
        assert abs(predicted - observed[0]) < 0.01

    def test_returns_valid_profile(self) -> None:
        observed = {i: 1.0 / 29 for i in range(29)}
        observed[0] = 0.01
        count, profile = find_best_suppression(observed, 13, 29, 0)
        assert sum(profile.mapping.values()) == 169
        assert profile.mapping[0] == count
