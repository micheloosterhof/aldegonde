from aldegonde.maths import factor


def test_factor_factor_pairs() -> None:
    assert factor.factor_pairs(49) == [(1,49), (7, 7), (49,1)]
    assert factor.factor_pairs(8) == [(1, 8), (2, 4), (4, 2), (8,1)]
    assert factor.factor_pairs(7) == [(1, 7), (7, 1)]
    assert factor.factor_pairs(12) == [(1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1)]
