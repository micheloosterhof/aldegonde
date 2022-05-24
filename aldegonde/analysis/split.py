from typing import Dict, List


def split_by_slice(inp: List[int], size: int) -> Dict[int, List[int]]:
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


def split_by_character(inp: List[int]) -> Dict[int, List[int]]:
    """
    by previous character
    """
    outp: Dict[int, List[int]] = {}
    for i in range(0, MAX):
        outp[i] = []
    for i in range(0, len(inp) - 1):
        outp[inp[i]].append(inp[i + 1])
    return outp


def split_by_doublet(ciphertext: List[int]) -> List[List[int]]:
    """
    split in simple chunks separated by a doublet
    """
    output: List[List[int]] = []
    current: List[int] = []
    for i in range(0, len(ciphertext)):
        if ciphertext[i] == ciphertext[i - 1]:
            output.append(current)
            current = [ciphertext[i]]
        else:
            current.append(ciphertext[i])
    output.append(current)
    return output
