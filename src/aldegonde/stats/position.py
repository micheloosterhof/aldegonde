"""Position-conditioned frequency test.

Tests whether the symbol distribution at a fixed position within a token
(word, line, group) differs from the overall distribution of symbols. A
significant deviation means a symbol's likelihood depends on where it sits in
the token, which betrays position-keyed enciphering, padding, or structural
markers at word starts or ends.

For each position the observed symbol counts are compared against the counts
expected from the pooled marginal distribution using Pearson's chi-square
goodness-of-fit test. Positions seen too few times to be reliable are skipped.

All functions work on arbitrary alphabets (runes, integers, letters).
"""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

from scipy.stats import chisquare

from aldegonde.exceptions import InsufficientDataError
from aldegonde.validation import validate_positive_integer

T = TypeVar("T")


@dataclass(frozen=True)
class PositionChiSquare:
    """Chi-square result for one position within a token.

    Attributes:
        position: Index within the token (from the start, or from the end
            when from_start is False)
        n: Number of tokens long enough to contribute a symbol here
        chi2: Pearson chi-square statistic against the marginal distribution
        pvalue: Probability of a deviation this large under the marginal
    """

    position: int
    n: int
    chi2: float
    pvalue: float


def position_frequency_chi2(
    tokens: Sequence[Sequence[T]],
    *,
    from_start: bool = True,
    max_position: int | None = None,
    min_count: int = 50,
) -> list[PositionChiSquare]:
    """Test each within-token position against the marginal distribution.

    The marginal distribution is the symbol frequency pooled over every
    symbol of every token. For each position the symbols found there are
    counted and compared to the marginal with a chi-square goodness-of-fit
    test. A small p-value flags a position whose symbol distribution departs
    from the overall frequencies.

    Args:
        tokens: The tokens to analyze (words, lines, groups)
        from_start: Index positions from the start of each token; when False,
            index from the end (position 0 is the last symbol)
        max_position: Examine only positions with index below this; None
            examines every position reached by some token
        min_count: Skip positions contributing fewer than this many symbols

    Returns:
        A list of PositionChiSquare results in ascending position order,
        omitting positions with fewer than min_count symbols

    Raises:
        InvalidInputError: If min_count is not a positive integer
        InsufficientDataError: If no tokens are provided
    """
    validate_positive_integer(min_count, "min_count")
    if not tokens:
        msg = "no tokens provided"
        raise InsufficientDataError(msg, required_length=1, actual_length=0)

    marginal: Counter[T] = Counter()
    for token in tokens:
        marginal.update(token)
    total = sum(marginal.values())
    categories = list(marginal.keys())
    frequencies = [marginal[c] / total for c in categories]

    longest = max(len(token) for token in tokens)
    limit = longest if max_position is None else min(longest, max_position)

    results: list[PositionChiSquare] = []
    for position in range(limit):
        column: Counter[T] = Counter()
        for token in tokens:
            if len(token) > position:
                column[token[position if from_start else -1 - position]] += 1
        n = sum(column.values())
        if n < min_count:
            continue
        observed = [column[c] for c in categories]
        expected = [freq * n for freq in frequencies]
        stat, pvalue = chisquare(observed, expected)
        results.append(
            PositionChiSquare(
                position=position,
                n=n,
                chi2=float(stat),
                pvalue=float(pvalue),
            ),
        )
    return results
