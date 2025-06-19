"""prime factorization."""

from aldegonde.exceptions import MathematicalError
from aldegonde.validation import validate_positive_integer


def prime_factors(number: int) -> list[int]:
    """Find all prime factors of a number.

    Args:
        number: Positive integer to factorize

    Returns:
        List of prime factors

    Raises:
        InvalidInputError: If number is not a positive integer
        MathematicalError: If factorization fails
    """
    validate_positive_integer(number, "number")

    if number == 1:
        return []

    try:
        i = 2
        factors = []
        original_number = number

        while i * i <= number:
            if number % i:
                i += 1
            else:
                number //= i
                factors.append(i)

        if number > 1:
            factors.append(number)

    except Exception as exc:
        msg = f"Prime factorization failed for {original_number}"
        raise MathematicalError(
            msg,
            operation="prime_factorization",
            operands=(original_number,),
        ) from exc
    else:
        return factors


def factor_pairs(number: int) -> list[tuple[int, int]]:
    """Find all factor pairs of a number.

    Args:
        number: Positive integer to find factor pairs for

    Returns:
        List of tuples containing factor pairs

    Raises:
        InvalidInputError: If number is not a positive integer
        MathematicalError: If factor computation fails
    """
    validate_positive_integer(number, "number")

    try:
        output = []
        # Only check up to sqrt(number) for efficiency
        i = 1
        while i * i <= number:
            if number % i == 0:
                factor2 = number // i
                output.append((i, factor2))
                # Avoid duplicate pairs for perfect squares
                if i != factor2:
                    output.append((factor2, i))
            i += 1

        # Sort pairs by first element
        output.sort()

    except Exception as exc:
        msg = f"Factor pair computation failed for {number}"
        raise MathematicalError(
            msg,
            operation="factor_pairs",
            operands=(number,),
        ) from exc
    else:
        return output
