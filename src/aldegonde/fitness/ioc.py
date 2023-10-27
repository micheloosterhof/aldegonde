"""IOC Scoring Function."""

from collections.abc import Callable, Sequence
from math import sqrt
from typing import TypeVar

from aldegonde.stats import ioc

T = TypeVar("T")

ENGLISH = 0.0667
FRENCH = 0.0778
GERMAN = 0.0762
SPANISH = 0.0770
ITALIAN = 0.0738
RUSSIAN = 0.0529


def IocFitness(target_ioc: float) -> Callable[[Sequence[T]], float]:
    """Score a text by evaluating its IOC score.

    Example:
    -------
        >>> fitness = IOCScore(ENGLISH)
        >>> fitness("ABC")
        -32.2

    Args:
    ----
        target_ioc (lfoat): symbol to frequency mapping of the distribution to compare with
    """

    def inner(text: Sequence[T]) -> float:
        return -sqrt(abs(ioc.ioc(text) - target_ioc))

    return inner
