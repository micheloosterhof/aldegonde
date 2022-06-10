from ..structures import sequence


def print_kappa(
    ciphertext: sequence.Sequence,
    minimum: int = 1,
    maximum: int = 51,
    threshold: float = 1.3,
    trace: bool = False,
) -> None:
    """
    kappa test
    overlay text with itself and count the number of duplicate letters
    """
    MAX = len(ciphertext.alphabet)
    if maximum == 0:
        maximum = int(len(ciphertext) / 2)
    for keylen in range(minimum, maximum):
        counter = 0
        dups = 0
        for i in range(0, len(ciphertext) - keylen):
            counter = counter + 1
            if ciphertext[i] == ciphertext[i + keylen]:
                dups = dups + 1
        if (dups / counter * MAX) > threshold or trace is True:
            print(f"keylen={keylen:02d}, dups={dups:02d}, ioc={dups/counter*MAX:.3f} ")
    print()
