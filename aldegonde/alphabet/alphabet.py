from typing import Dict, List

# There are 29 runes. Generally counted 0-28
MAX = 29


def a2i(text: str) -> List[int]:
    """
    ASCII 2 INTEGER [A-Z] -> [0-25]
    """
    output: List[int] = []
    for c in text:
        output.append(ord(c) - ord("A"))
    return output


def i2a(text: List[int]) -> str:
    """
    INTEGER 2 ASCII [0-25] -> [A-Z]
    """
    output: str = ""
    for c in text:
        output += chr(ord("A") + c)
    return output


def alphabet(text: List[int]) -> List[int]:
    """
    Find all unique values
    """
    return sorted(list(set(text)))


def numberToBase(n: int, b: int) -> List[int]:
    """
    converts from base10 to any other base. outputs as list of int
    """
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def base29(input: int, padding: int = -1) -> List[int]:
    """
    input `int` and output in Base29 as list of integers
    """
    l = numberToBase(input, MAX)
    if padding == -1:
        return l
    else:
        pad_value = 0
        pad_size = padding - len(l)
        final_list = [*[pad_value] * pad_size, *l]
        return final_list


class RuneIterator:
    """
    iterates over runes length L, [0,0,0], [0,0,1], [0,0,2], ..., [0,0,MAX], [0,1,0], ...
    """

    i: int
    maximum: int
    length: int

    def __init__(self, length: int):
        self.length = length
        self.maximum = MAX**length

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i >= self.maximum:
            raise StopIteration
        else:
            x = self.i
            self.i += 1
            return base29(x, padding=self.length)


def keyword_to_alphabet(keyword: List[int] = range(0, MAX + 1)):
    """
    construct alphabet order based on keyword
    example:    keyword_to_alphabet(a2i("HYDRAULIC"))
    """
    alphabet = keyword
    return alphabet
