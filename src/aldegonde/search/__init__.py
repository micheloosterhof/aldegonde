"""Key-space search: hill climbing and filter cascades."""

from aldegonde.search.cascade import Stage, StageReport, filter_cascade
from aldegonde.search.hillclimb import (
    ClimbResult,
    Neighbor,
    Score,
    conjugation_neighbor,
    hill_climb,
    multi_start,
    swap_neighbor,
)

__all__ = [
    # cascade
    "Stage",
    "StageReport",
    "filter_cascade",
    # hillclimb
    "ClimbResult",
    "Neighbor",
    "Score",
    "conjugation_neighbor",
    "hill_climb",
    "multi_start",
    "swap_neighbor",
]
