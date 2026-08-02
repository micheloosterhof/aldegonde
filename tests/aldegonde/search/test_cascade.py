import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.search.cascade import filter_cascade


def test_cascade_funnels_and_reports() -> None:
    survivors, reports = filter_cascade(
        range(30),
        [
            ("even", lambda x: x % 2 == 0),
            ("div3", lambda x: x % 3 == 0),
        ],
    )
    assert survivors == [0, 6, 12, 18, 24]
    assert reports[0].entered == 30
    assert reports[0].survived == 15
    assert reports[1].entered == 15
    assert reports[1].survived == 5


def test_cascade_stops_evaluating_dropped_candidates() -> None:
    seen: list[int] = []

    def expensive(x: int) -> bool:
        seen.append(x)
        return True

    filter_cascade(
        range(10),
        [("cheap", lambda x: x < 3), ("expensive", expensive)],
    )
    # only the 3 survivors of the cheap stage reach the expensive one
    assert sorted(seen) == [0, 1, 2]


def test_cascade_all_survive() -> None:
    survivors, reports = filter_cascade([1, 2, 3], [("all", lambda _x: True)])
    assert survivors == [1, 2, 3]
    assert reports[0].survived == 3


def test_cascade_none_survive() -> None:
    survivors, reports = filter_cascade([1, 2, 3], [("none", lambda _x: False)])
    assert survivors == []
    assert reports[0].survived == 0


def test_cascade_requires_a_stage() -> None:
    with pytest.raises(InvalidInputError):
        filter_cascade([1, 2, 3], [])


def test_cascade_self_test_pattern() -> None:
    # plant a known-good candidate and confirm the cascade passes it
    stages = [
        ("positive", lambda x: x > 0),
        ("even", lambda x: x % 2 == 0),
    ]
    survivors, _ = filter_cascade([4], stages)
    assert survivors == [4]
