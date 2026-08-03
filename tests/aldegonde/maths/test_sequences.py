import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.maths.sequences import (
    catalogue,
    fibonacci,
    linear_recurrence,
    lucas,
    moebius_sequence,
    naturals,
    polygonal,
    prime_gaps,
    primes,
    totients,
    triangular,
)


def test_primes_first_n() -> None:
    assert primes(6) == [2, 3, 5, 7, 11, 13]
    assert primes(0) == []
    assert primes(1) == [2]
    assert len(primes(100)) == 100


def test_prime_gaps() -> None:
    assert prime_gaps(5) == [1, 2, 2, 4, 2]


def test_naturals() -> None:
    assert naturals(4) == [0, 1, 2, 3]
    assert naturals(3, start=10) == [10, 11, 12]


def test_totients() -> None:
    # phi(1..6) = 1,1,2,2,4,2
    assert totients(6) == [1, 1, 2, 2, 4, 2]


def test_moebius_sequence() -> None:
    # mu(1..6) = 1,-1,-1,0,-1,1
    assert moebius_sequence(6) == [1, -1, -1, 0, -1, 1]


def test_triangular_and_polygonal() -> None:
    assert triangular(5) == [1, 3, 6, 10, 15]
    assert polygonal(5, 3) == triangular(5)
    assert polygonal(5, 4) == [1, 4, 9, 16, 25]
    assert polygonal(4, 5) == [1, 5, 12, 22]


def test_linear_recurrence_families() -> None:
    assert fibonacci(8) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert lucas(6) == [2, 1, 3, 4, 7, 11]
    tribonacci = linear_recurrence(8, [0, 0, 1], [1, 1, 1])
    assert tribonacci == [0, 0, 1, 1, 2, 4, 7, 13]


def test_linear_recurrence_short_request() -> None:
    assert fibonacci(0) == []
    assert fibonacci(1) == [0]
    assert fibonacci(2) == [0, 1]


def test_catalogue_uniform_length() -> None:
    cat = catalogue(7)
    assert all(len(seq) == 7 for seq in cat.values())
    assert "primes" in cat
    assert "fibonacci" in cat
    assert cat["squares"] == polygonal(7, 4)


def test_validation() -> None:
    with pytest.raises(InvalidInputError):
        primes(-1)
    with pytest.raises(InvalidInputError):
        polygonal(5, 2)
    with pytest.raises(InvalidInputError):
        totients(5, start=0)
    with pytest.raises(InvalidInputError):
        linear_recurrence(5, [], [])
    with pytest.raises(InvalidInputError):
        linear_recurrence(5, [1, 1], [1])
