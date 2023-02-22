"""module description
"""

from aldegonde.structures import sequence


def print_kappa(
    ciphertext: sequence.Sequence,
    minimum: int = 1,
    maximum: int = 51,
    threshold: float = 1.3,
    trace: bool = False,
) -> None:
    """The `Kappa` test. Overlay the ciphertext with itself shifted by a number
    of positions, then count the positions with the same character.
    """
    assert maximum >= 0
    assert minimum >= 1
    MAX = len(ciphertext.alphabet)
    if maximum == 0:
        maximum = int(len(ciphertext) / 2)
    elif maximum > len(ciphertext):
        maximum = len(ciphertext)
    for keylen in range(minimum, maximum):
        counter = 0
        dups = 0
        for i in range(0, len(ciphertext) - keylen):
            counter = counter + 1
            if ciphertext[i] == ciphertext[i + keylen]:
                dups = dups + 1
        if (dups / counter * MAX) > threshold or trace is True:
            print(
                f"kappa: keylen={keylen:02d},"
                + f"dups={dups:02d},"
                + f"ioc={dups/counter*MAX:.3f} "
            )
    print()
