"""Higher-order coincidence statistics.

The kappa test measures second-order coincidence: how often a symbol equals
the symbol a fixed lag away. Some ciphers leave a higher-order signature
instead, where the lag-L matches themselves cluster at particular separations.
This module exposes the lag-L match indicator and counts pairs of matches at
chosen separations, the canonical fourth-order generalization of kappa.

A periodic interaction shows up as an excess of joint matches at a separation
tied to the period. Significance is best judged against a Monte Carlo null
built from shuffles of the same text, since the joint counts are not
independent; this module supplies the raw statistic, not a p-value.

All functions work on arbitrary alphabets (runes, integers, letters).
"""

import random
import statistics
from collections import Counter
from collections.abc import Sequence
from typing import NamedTuple, TypeVar

from aldegonde.exceptions import InvalidInputError
from aldegonde.validation import validate_positive_integer, validate_text_sequence

T = TypeVar("T")


class JointCount(NamedTuple):
    """A joint match count alongside its chance expectation.

    Attributes:
        observed: Pairs of lag-L matches actually found at the separation
        expected: Pairs expected if the matches fell independently at the
            observed per-position rate
    """

    observed: int
    expected: float


def match_indicator(text: Sequence[T], lag: int) -> list[bool]:
    """Return the lag-L match indicator of a sequence.

    Entry i is True when the symbol at position i equals the symbol lag
    positions later. This is the per-position event whose mean is the kappa
    coincidence rate.

    Args:
        text: Sequence to analyze
        lag: Distance between the compared symbols

    Returns:
        A list of booleans of length len(text) - lag

    Raises:
        InvalidInputError: If lag is not a positive integer
        InsufficientDataError: If text is no longer than lag
    """
    validate_positive_integer(lag, "lag")
    validate_text_sequence(text, min_length=lag + 1)
    return [text[i] == text[i + lag] for i in range(len(text) - lag)]


def joint_coincidence(
    text: Sequence[T],
    lag: int,
    separations: Sequence[int],
) -> dict[int, JointCount]:
    """Count pairs of lag-L matches at each separation, against chance.

    For each separation s the observed count is the number of positions i
    where the lag-L match indicator is True at both i and i + s. The expected
    count is what that would be if the matches fell independently at the
    observed per-position rate: the number of available pairs times the
    squared rate. An observed count well above its expectation reveals a
    higher-order periodic structure that the plain kappa test averages away.

    Args:
        text: Sequence to analyze
        lag: Lag of the match indicator
        separations: Separations between matches to count pairs for

    Returns:
        A dictionary mapping each separation to its observed and expected
        joint match counts

    Raises:
        InvalidInputError: If lag or any separation is not a positive integer
        InsufficientDataError: If text is no longer than lag
    """
    indicator = match_indicator(text, lag)
    length = len(indicator)
    rate = sum(indicator) / length
    counts: dict[int, JointCount] = {}
    for separation in separations:
        validate_positive_integer(separation, "separation")
        observed = sum(
            indicator[i] and indicator[i + separation]
            for i in range(length - separation)
        )
        available_pairs = max(0, length - separation)
        counts[separation] = JointCount(
            observed=observed,
            expected=available_pairs * rate * rate,
        )
    return counts


class BoundaryCoincidence(NamedTuple):
    """Lag-L coincidence counts split by word membership.

    Attributes:
        within_observed: Matches whose two positions fall in the same word
        within_pairs: Position pairs available inside a single word
        across_observed: Matches whose two positions fall in different words
        across_pairs: Position pairs spanning a word boundary
    """

    within_observed: int
    within_pairs: int
    across_observed: int
    across_pairs: int


class BoundaryPermutation(NamedTuple):
    """Result of the word-boundary permutation test.

    Attributes:
        observed: Within-word matches under the real word boundaries
        null_mean: Mean of the statistic over the permuted boundaries
        null_sd: Standard deviation over the permuted boundaries
        p_value: Fraction of permutations at or above the observed value,
            with add-one smoothing
    """

    observed: int
    null_mean: float
    null_sd: float
    p_value: float


def word_index_map(words: Sequence[Sequence[T]]) -> list[int]:
    """Return the word index of every position in the concatenated stream.

    Args:
        words: Tokenized text, one sequence per word

    Returns:
        A list with one entry per symbol of the concatenation, giving the
        index of the word that symbol belongs to
    """
    return [index for index, word in enumerate(words) for _ in word]


def recut_words(stream: Sequence[T], lengths: Sequence[int]) -> list[list[T]]:
    """Cut a stream into words of the given lengths.

    The inverse of concatenation: used to re-tokenize an unchanged symbol
    stream under a shuffled word-length sequence, the core move of the
    boundary permutation test.

    Args:
        stream: Symbol stream to cut
        lengths: Length of each word, in order

    Returns:
        The stream as a list of words

    Raises:
        InvalidInputError: If a length is not positive or the lengths do not
            add up to the stream length
    """
    for length in lengths:
        validate_positive_integer(length, "length")
    if sum(lengths) != len(stream):
        msg = f"lengths sum to {sum(lengths)}, stream has {len(stream)} symbols"
        raise InvalidInputError(msg)
    words: list[list[T]] = []
    position = 0
    for length in lengths:
        words.append(list(stream[position : position + length]))
        position += length
    return words


def boundary_coincidence(
    words: Sequence[Sequence[T]],
    lag: int,
    length: int = 1,
) -> BoundaryCoincidence:
    """Split the lag-L n-gram coincidence count by word membership.

    Counts matches on the concatenation of the words, comparing the n-gram
    starting at i with the n-gram starting at i + lag. A pair is within-word
    when both n-grams fall entirely inside the same single word, and
    across-word otherwise. A within rate above the across rate means the
    coincidences know where the word boundaries are. Length 2 counts the
    XY..XY digraph repeats at distance lag.

    Args:
        words: Tokenized text, one sequence per word
        lag: Distance between the compared n-grams
        length: Size of the compared n-grams (1 = single symbols)

    Returns:
        Observed matches and available pairs for both classes

    Raises:
        InvalidInputError: If lag or length is not a positive integer
        InsufficientDataError: If the concatenation is no longer than lag
    """
    validate_positive_integer(lag, "lag")
    validate_positive_integer(length, "length")
    stream = [symbol for word in words for symbol in word]
    validate_text_sequence(stream, min_length=lag + 1)
    indices = word_index_map(words)
    within_observed = within_pairs = across_observed = across_pairs = 0
    for i in range(len(stream) - lag - length + 1):
        matched = stream[i : i + length] == stream[i + lag : i + lag + length]
        # indices is monotonic, so equal endpoints put both n-grams in one word
        if indices[i] == indices[i + lag + length - 1]:
            within_pairs += 1
            within_observed += matched
        else:
            across_pairs += 1
            across_observed += matched
    return BoundaryCoincidence(
        within_observed=within_observed,
        within_pairs=within_pairs,
        across_observed=across_observed,
        across_pairs=across_pairs,
    )


def _within_word_matches(
    stream: Sequence[T],
    lengths: Sequence[int],
    lag: int,
) -> int:
    """Count lag-L matches falling inside single words of the given cut."""
    matches = 0
    position = 0
    for length in lengths:
        end = position + length
        for i in range(position, end - lag):
            if stream[i] == stream[i + lag]:
                matches += 1
        position = end
    return matches


def boundary_permutation_test(
    sections: Sequence[Sequence[Sequence[T]]],
    lag: int,
    permutations: int = 1000,
    seed: int = 0,
) -> BoundaryPermutation:
    """Test whether word boundaries know where the lag-L matches are.

    The symbol stream of every section is kept byte-for-byte intact —
    preserving all stream correlations — while each section's word-length
    sequence is shuffled before re-cutting it into words. The statistic is
    the total number of within-word lag-L matches. A small p-value means the
    real boundaries align with the matches more than shuffled boundaries do,
    i.e. the coincidence structure is word-aware.

    Args:
        sections: Tokenized text, one word list per section; lengths are
            shuffled within each section independently
        lag: Distance between the compared symbols
        permutations: Number of shuffles to draw
        seed: Seed for the shuffle generator, for reproducibility

    Returns:
        The observed statistic, the permutation null mean and standard
        deviation, and the one-sided p-value

    Raises:
        InvalidInputError: If lag or permutations is not a positive integer
    """
    validate_positive_integer(lag, "lag")
    validate_positive_integer(permutations, "permutations")
    prepared = []
    observed = 0
    for words in sections:
        stream = [symbol for word in words for symbol in word]
        lengths = [len(word) for word in words]
        observed += _within_word_matches(stream, lengths, lag)
        prepared.append((stream, lengths))
    rng = random.Random(seed)
    null: list[int] = []
    for _ in range(permutations):
        total = 0
        for stream, lengths in prepared:
            shuffled = list(lengths)
            rng.shuffle(shuffled)
            total += _within_word_matches(stream, shuffled, lag)
        null.append(total)
    at_least = sum(1 for value in null if value >= observed)
    return BoundaryPermutation(
        observed=observed,
        null_mean=statistics.fmean(null),
        null_sd=statistics.pstdev(null),
        p_value=(at_least + 1) / (permutations + 1),
    )


def match_separations(
    text: Sequence[T],
    lag: int,
    max_separation: int | None = None,
) -> dict[int, int]:
    """Histogram the separations between consecutive lag-L matches.

    Where `joint_coincidence` counts pairs of matches at chosen separations,
    this profiles the gaps between one match and the next. Under
    independence the gaps are geometric; an excess at particular separations
    (or a dead zone at small ones) is the higher-order signature of a
    periodic or self-excluding mechanism. Judge significance against a
    resampled null; the gaps are not independent.

    Args:
        text: Sequence to analyze
        lag: Lag of the match indicator
        max_separation: Largest separation to include; unlimited when omitted

    Returns:
        A dictionary mapping each observed separation between consecutive
        matches to its count

    Raises:
        InvalidInputError: If lag is not a positive integer
        InsufficientDataError: If text is no longer than lag
    """
    indicator = match_indicator(text, lag)
    separations: dict[int, int] = {}
    previous: int | None = None
    for i, matched in enumerate(indicator):
        if not matched:
            continue
        if previous is not None:
            gap = i - previous
            if max_separation is None or gap <= max_separation:
                separations[gap] = separations.get(gap, 0) + 1
        previous = i
    return separations


def within_delta_histogram(
    words: Sequence[Sequence[T]],
    alphabet: Sequence[T],
    lag: int,
) -> list[int]:
    """Histogram the modular symbol difference over within-word lag-L pairs.

    For every pair of positions lag apart inside a single word, counts the
    difference of alphabet indices modulo the alphabet size. Bin 0 holds the
    coincidences; the shape of the nonzero bins discriminates mechanisms
    that a bare match count cannot: a literal copy inflates only bin 0,
    additive key drift shifts mass to specific nonzero bins, and an
    unstructured stream leaves them flat.

    Args:
        words: Tokenized text, one sequence per word
        alphabet: The alphabet fixing the index of every symbol
        lag: Distance between the compared symbols

    Returns:
        A list of alphabet-size counts, entry d holding the number of pairs
        with (index(second) - index(first)) mod alphabetsize == d

    Raises:
        InvalidInputError: If lag is not a positive integer or a symbol is
            missing from the alphabet
    """
    validate_positive_integer(lag, "lag")
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    modulus = len(alphabet)
    histogram = [0] * modulus
    for word in words:
        for i in range(len(word) - lag):
            try:
                delta = (index[word[i + lag]] - index[word[i]]) % modulus
            except KeyError as exc:
                msg = f"symbol {exc.args[0]!r} not in alphabet"
                raise InvalidInputError(msg) from exc
            histogram[delta] += 1
    return histogram


class BucketCoincidence(NamedTuple):
    """Pooled pairwise coincidence within position buckets.

    Attributes:
        observed: Equal-symbol pairs found inside buckets
        pairs: Position pairs available inside buckets
        rate: observed / pairs, or 0.0 with no pairs
    """

    observed: int
    pairs: int
    rate: float


def bucket_coincidence(
    stream: Sequence[T],
    labels: Sequence[object],
) -> BucketCoincidence:
    """Pool the pairwise coincidence rate inside arbitrary position buckets.

    Every position carries a label; all unordered position pairs sharing a
    label are compared. A pooled rate above the chance rate means positions
    with the same label tend to hold the same symbol — the general test for
    "is the key a function of this observable?", with the label encoding the
    hypothesis: position within a period, word length and phase, line
    number, or any other public feature.

    Args:
        stream: Symbol stream to analyze
        labels: One bucket label per position; positions with equal labels
            are compared

    Returns:
        The pooled matched pairs, available pairs, and rate

    Raises:
        InvalidInputError: If labels and stream lengths differ
    """
    if len(labels) != len(stream):
        msg = f"{len(labels)} labels for {len(stream)} positions"
        raise InvalidInputError(msg)
    buckets: dict[object, Counter[T]] = {}
    sizes: Counter[object] = Counter()
    for symbol, label in zip(stream, labels):
        buckets.setdefault(label, Counter())[symbol] += 1
        sizes[label] += 1
    observed = 0
    pairs = 0
    for label, counts in buckets.items():
        size = sizes[label]
        pairs += size * (size - 1) // 2
        observed += sum(count * (count - 1) // 2 for count in counts.values())
    return BucketCoincidence(
        observed=observed,
        pairs=pairs,
        rate=observed / pairs if pairs else 0.0,
    )
