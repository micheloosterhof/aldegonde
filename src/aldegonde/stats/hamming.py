from ..structures import sequence


def hamming_distance(s1: sequence.Sequence, s2: sequence.Sequence) -> int:
    """
    The Hamming distance between two equal-length strings of symbols
    is the number of positions at which the corresponding symbols
    are different
    """
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length.")
    return sum(el1 != el2 for el1, el2 in zip(s1, s2))
