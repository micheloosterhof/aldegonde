import random

import gematria

g = gematria.gematria

# There are 29 runes. Generally counted 0-28
MAX = 29


def randomrunes(l: int, max: int = MAX) -> list[int]:
    """
    Random list of runes of lenth len
    """
    rl = []
    for i in range(0, l):
        rl.append(random.randrange(0, max))
    return rl


def numberToBase(n: int, b: int) -> list[int]:
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


def base29(input: int, padding: int = -1) -> list[int]:
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


def english_output(runes: list[int], limit=0) -> None:
    """
    prints rune output translated back to english letters
    """
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("RUNEIDX: ", end="")
    for i in range(0, limit):
        print("{:02} ".format(runes[i]), end="")
    print()

    print("ENGLISH:  ", end="")
    for i in range(0, limit):
        print("{:2} ".format(g.position_to_latin_forward_dict[runes[i]]), end="")
    print()
