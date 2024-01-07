from aldegonde.maths import factor


def test_factor_two_factors() -> None:
    assert factor.two_factors(49) == [(7, 7)]
    assert factor.two_factors(8) == [(2, 4)]
    assert factor.two_factors(7) == []
    assert factor.two_factors(12) == [(2, 6), (3, 4)]
