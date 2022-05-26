def split_by_slice(inp: list[int], size: int) -> dict[int, list[int]]:
    """
    Create slices of the input, with a certain slice size
    This will return every N'th element
    For size 3, it will return a dictionary of lists with elements:
       [0, 3, 6, 9] [1, 4, 7, 10] [2, 5, 8]
    """
    outp = {}
    for i in range(0, size):
        outp[i] = inp[slice(i, len(inp), size)].copy()
    return outp


def split_by_character(inp: list[int]) -> dict[int, list[int]]:
    """
    by previous character
    """
    outp: dict[int, list[int]] = {}
    for i in range(0, MAX):
        outp[i] = []
    for i in range(0, len(inp) - 1):
        outp[inp[i]].append(inp[i + 1])
    return outp


def split_by_doublet(ciphertext: list[int]) -> list[list[int]]:
    """
    split in simple chunks separated by a doublet
    """
    output: list[list[int]] = []
    current: list[int] = []
    for i in range(0, len(ciphertext)):
        if ciphertext[i] == ciphertext[i - 1]:
            output.append(current)
            current = [ciphertext[i]]
        else:
            current.append(ciphertext[i])
    output.append(current)
    return output
