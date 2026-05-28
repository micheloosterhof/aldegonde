"""DELT: horizontal differences or sums of a sequence under modular arithmetic.

Produces a derived sequence that can be fed back into the diagnostic functions.
"""

from collections.abc import Sequence
from enum import Enum

from aldegonde.maths.modular import modDivide


class DeltaOp(Enum):
    """Arithmetic combining each symbol with the one `skip` positions later."""

    SUB = "sub"    # c[i+skip] - c[i]
    RSUB = "rsub"  # c[i] - c[i+skip]
    ADD = "add"    # c[i+skip] + c[i]
    MUL = "mul"    # c[i+skip] * c[i]
    DIV = "div"    # c[i+skip] / c[i]; raises on a non-invertible divisor
    RDIV = "rdiv"  # c[i] / c[i+skip]; raises on a non-invertible divisor


def delta(
    text: Sequence[object],
    alphabet: Sequence[object],
    skip: int = 1,
    op: DeltaOp = DeltaOp.SUB,
) -> list[object]:
    """Combine each symbol with the one `skip` positions later, modulo alphabet size.

    The result is a list of alphabet symbols, one shorter than the input by `skip`.
    DIV raises ValueError when the divisor symbol has no modular inverse.
    """
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    modulus = len(alphabet)
    result: list[object] = []
    for i in range(len(text) - skip):
        a = index[text[i]]
        b = index[text[i + skip]]
        if op is DeltaOp.SUB:
            value = (b - a) % modulus
        elif op is DeltaOp.RSUB:
            value = (a - b) % modulus
        elif op is DeltaOp.ADD:
            value = (b + a) % modulus
        elif op is DeltaOp.MUL:
            value = (b * a) % modulus
        elif op is DeltaOp.DIV:
            value = modDivide(b, a, modulus)
        else:  # DeltaOp.RDIV
            value = modDivide(a, b, modulus)
        result.append(alphabet[value])
    return result


def delta2(
    text: Sequence[object],
    alphabet: Sequence[object],
    skip: int = 1,
    op: DeltaOp = DeltaOp.SUB,
) -> list[object]:
    """Second-order delta: apply `delta` twice."""
    return delta(delta(text, alphabet, skip, op), alphabet, skip, op)
