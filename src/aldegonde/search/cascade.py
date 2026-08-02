# ABOUTME: Cheap-to-expensive filter cascade over a candidate key space,
# ABOUTME: reporting the survivor funnel at every stage.
"""Staged filtering of candidate keys.

Enumerated key families are best culled by a cascade: order the tests from
cheapest to most expensive, let each stage eliminate what it can, and only
pay for the expensive scoring on the few survivors. The funnel — how many
candidates each stage passed — is itself the result worth reporting: a
stage that eliminates nothing is dead weight, and a cascade that eliminates
everything deserves a self-test before the conclusion is believed (plant a
known key, confirm the cascade passes it; a cascade that rejects the true
key proves only its own brokenness).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, NamedTuple, TypeVar

from aldegonde.exceptions import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

S = TypeVar("S")

Stage = tuple[str, Callable[[S], bool]]
"""A named predicate: candidates failing it are eliminated."""


class StageReport(NamedTuple):
    """Survivor count after one cascade stage.

    Attributes:
        name: The stage's name
        entered: Candidates that reached this stage
        survived: Candidates that passed it
    """

    name: str
    entered: int
    survived: int


def filter_cascade(
    candidates: Iterable[S],
    stages: Sequence[Stage[S]],
) -> tuple[list[S], list[StageReport]]:
    """Run candidates through named predicate stages, cheapest first.

    Every candidate is evaluated stage by stage and dropped at its first
    failure, so later (more expensive) stages only see earlier survivors.

    Args:
        candidates: The candidate states to filter
        stages: Named predicates in evaluation order

    Returns:
        The candidates surviving every stage, and a per-stage funnel report

    Raises:
        InvalidInputError: If no stages are given
    """
    if not stages:
        msg = "filter_cascade needs at least one stage"
        raise InvalidInputError(msg)
    survivors = list(candidates)
    reports: list[StageReport] = []
    for name, predicate in stages:
        entered = len(survivors)
        survivors = [candidate for candidate in survivors if predicate(candidate)]
        reports.append(StageReport(name=name, entered=entered, survived=len(survivors)))
    return survivors, reports
