# ABOUTME: Signed standard score (z-score) of an observed count against its
# ABOUTME: chance expectation, with a zero-standard-deviation guard.
"""Standard score (z-score) helper."""


def z_score(observed: float, expected: float, sd: float) -> float:
    """Signed standard score: standard deviations of observed above expected.

    Args:
        observed: The measured value
        expected: The value expected by chance
        sd: The standard deviation of the chance distribution

    Returns:
        The signed number of standard deviations separating observed from
        expected, or 0.0 when sd is not positive (a degenerate distribution
        carries no information about deviation).
    """
    return (observed - expected) / sd if sd > 0 else 0.0
