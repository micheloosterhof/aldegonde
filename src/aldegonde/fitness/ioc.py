"""
IOC Scoring Function
"""

from math import sqrt
from collections.abc import Callable

from aldegonde.structures import sequence
from aldegonde.stats import ioc

ENGLISH = 0.0667
FRENCH = 0.0778
GERMAN = 0.0762
SPANISH = 0.0770
ITALIAN = 0.0738
RUSSIAN = 0.0529


def IocFitness(target_ioc: float) -> Callable[[sequence.Sequence], float]:
    """Score a text by evaluating its IOC score

    Example:
        >>> fitness = IOCScore(ENGLISH)
        >>> fitness("ABC")
        -32.2

    Args:
        target_ioc (lfoat): symbol to frequency mapping of the distribution to compare with
    """

    def inner(text: sequence.Sequence) -> float:
        return -sqrt(abs(ioc.ioc(text) - target_ioc))

    return inner
