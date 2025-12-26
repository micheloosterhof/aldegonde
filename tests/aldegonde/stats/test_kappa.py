"""Tests for kappa analysis including multigraphic kappa."""

from aldegonde.stats.kappa import doublets, kappa, kappa2, kappa3, kappa4, triplets


def test_kappa() -> None:
    assert kappa("ABCDEFGHIJKLMNOPQRSTUVWXYZ", skip=1) == 0.0
    assert kappa("ABCABC", skip=1) == 0.0
    assert kappa("ABCABC", skip=2) == 0.0
    assert kappa("ABCABC", skip=3) == 1.0
    assert kappa("ABCABCABC", skip=3) == 1.0
    assert kappa("ABCABCABCXXX", skip=3) == 2 / 3


uniq = "ABCDEFGH"
dobl = "AABBCCDDEEFFGGHH"
trpl = "AAABBBCCCDDDEEEFFFGGGHHH"


def test_doublets() -> None:
    assert doublets(uniq) == ([], 8 - 1)
    assert doublets(dobl) == ([0, 2, 4, 6, 8, 10, 12, 14], 16 - 1)
    assert doublets(trpl) == (
        [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22],
        24 - 1,
    )


def test_triplets() -> None:
    assert triplets(dobl) == 0
    assert triplets(uniq) == 0
    assert triplets(trpl) == 8


# Multigraphic kappa tests


def test_kappa_digraphic() -> None:
    """Test digraphic kappa (length=2) - detects repeated digraphs."""
    # "ABAB" has digraph "AB" at position 0 and 2, skip=2 should match
    assert kappa("ABAB", skip=2, length=2) == 1.0
    # "ABCD" has no repeated digraphs at any skip
    assert kappa("ABCD", skip=1, length=2) == 0.0
    assert kappa("ABCD", skip=2, length=2) == 0.0
    # "ABCABC" - digraph "AB" at 0,3 and "BC" at 1,4 and "CA" at 2 (no match)
    # At skip=3: AB...AB, BC...BC = 2 matches out of 2 comparisons
    assert kappa("ABCABC", skip=3, length=2) == 1.0
    # "ABABAB" at skip=2: comparisons at pos 0,1,2
    # pos 0: AB vs AB (match), pos 1: BA vs BA (match), pos 2: AB vs AB (match)
    assert kappa("ABABAB", skip=2, length=2) == 1.0
    # "ABCDAB" at skip=4, length=2: only 1 comparison (AB vs AB)
    assert kappa("ABCDAB", skip=4, length=2) == 1.0
    # "ABCDEF" at skip=2, length=2: AB vs CD (no), BC vs DE (no), CD vs EF (no)
    assert kappa("ABCDEF", skip=2, length=2) == 0.0


def test_kappa_trigraphic() -> None:
    """Test trigraphic kappa (length=3) - detects repeated trigraphs."""
    # "ABCABC" - trigraph "ABC" at 0 and 3
    assert kappa("ABCABC", skip=3, length=3) == 1.0
    # No repeated trigraphs at skip=1 or 2
    assert kappa("ABCABC", skip=1, length=3) == 0.0
    assert kappa("ABCABC", skip=2, length=3) == 0.0
    # "ABCDEFABCDEF" at skip=6
    assert kappa("ABCDEFABCDEF", skip=6, length=3) == 1.0


def test_kappa_tetragraphic() -> None:
    """Test tetragraphic kappa (length=4) - detects repeated tetragraphs."""
    # "ABCDABCD" - tetragraph "ABCD" at 0 and 4
    assert kappa("ABCDABCD", skip=4, length=4) == 1.0
    # No match at other skips
    assert kappa("ABCDABCD", skip=1, length=4) == 0.0
    assert kappa("ABCDABCD", skip=2, length=4) == 0.0
    assert kappa("ABCDABCD", skip=3, length=4) == 0.0


def test_doublets_multigraphic() -> None:
    """Test doublets function with length parameter."""
    # "ABAB" with length=2, skip=2: compare AB at 0 with AB at 2
    # Only 1 comparison possible: n - skip - length + 1 = 4 - 2 - 2 + 1 = 1
    positions, count = doublets("ABAB", skip=2, length=2)
    assert positions == [0]
    assert count == 1

    # "ABCABC" with length=2, skip=3:
    # Comparisons: AB vs AB (pos 0), BC vs BC (pos 1)
    # n - skip - length + 1 = 6 - 3 - 2 + 1 = 2
    positions, count = doublets("ABCABC", skip=3, length=2)
    assert positions == [0, 1]
    assert count == 2

    # Edge case: text too short
    positions, count = doublets("AB", skip=2, length=2)
    assert positions == []
    assert count == 0


def test_kappa_convenience_functions() -> None:
    """Test kappa2, kappa3, kappa4 convenience functions."""
    text = "ABCABCABC"

    # kappa2 should equal kappa with length=2
    assert kappa2(text, skip=3) == kappa(text, skip=3, length=2)

    # kappa3 should equal kappa with length=3
    assert kappa3(text, skip=3) == kappa(text, skip=3, length=3)

    # kappa4 should equal kappa with length=4
    assert kappa4(text, skip=3) == kappa(text, skip=3, length=4)


def test_kappa_multigraphic_period_detection() -> None:
    """Test that multigraphic kappa can detect periods in polyalphabetic ciphers."""
    # Simulated Vigenere-like pattern with period 5
    # When period divides skip, we expect higher kappa
    text = "ABCDEABCDEABCDEABCDE"  # period 5, length 20

    # Monographic kappa at skip=5 should be 1.0 (all chars repeat)
    assert kappa(text, skip=5, length=1) == 1.0

    # Digraphic kappa at skip=5 should also be 1.0
    assert kappa(text, skip=5, length=2) == 1.0

    # Trigraphic kappa at skip=5 should also be 1.0
    assert kappa(text, skip=5, length=3) == 1.0

    # At skip=4, nothing should match (not a multiple of period)
    assert kappa(text, skip=4, length=1) == 0.0


def test_kappa_empty_and_short_texts() -> None:
    """Test edge cases with empty or very short texts."""
    # Empty text
    assert kappa("", skip=1, length=1) == 0.0
    assert kappa("", skip=1, length=2) == 0.0

    # Single character
    assert kappa("A", skip=1, length=1) == 0.0

    # Text shorter than skip + length
    assert kappa("AB", skip=3, length=1) == 0.0
    assert kappa("ABC", skip=2, length=2) == 0.0
