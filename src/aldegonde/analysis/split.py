"""Functions to split a text in various ways"""

from aldegonde.structures import sequence


def split_by_slice(inp: sequence.Sequence, size: int) -> dict[int, sequence.Sequence]:
    """
    Create slices of the input, with a certain slice size
    This will return every N'th element
    For size 3, it will return a dictionary of lists with elements:
       [0, 3, 6, 9] [1, 4, 7, 10] [2, 5, 8]
    """
    outp = {}
    for i in range(0, size):
        ra = inp[slice(i, len(inp), size)].copy()
        outp[i] = sequence.Sequence.fromlist(data=ra, alphabet=inp.alphabet.alphabet)
    return outp


def split_by_character(inp: sequence.Sequence) -> dict[int, sequence.Sequence]:
    """
    by previous character
    """
    MAX = len(inp.alphabet)
    outp: dict[int, sequence.Sequence] = {}
    for i in range(0, MAX):
        outp[i] = sequence.Sequence(alphabet=inp.alphabet)
    for i in range(0, len(inp) - 1):
        outp[inp[i]].append(inp[i + 1])
    return outp


def split_by_doublet(ciphertext: sequence.Sequence) -> list[sequence.Sequence]:
    """
    split in simple chunks separated by a doublet
    """
    output: list[sequence.Sequence] = []
    current = sequence.Sequence(alphabet=ciphertext.alphabet)
    for i in range(0, len(ciphertext)):
        if ciphertext[i] == ciphertext[i - 1]:
            output.append(current)
            current = sequence.Sequence(data=[i], alphabet=ciphertext.alphabet)
        else:
            current.append(ciphertext[i])
    output.append(current)
    return output
