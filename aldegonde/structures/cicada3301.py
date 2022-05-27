import random

CICADA_ALPHABET = [
    "ᚠ",
    "ᚢ",
    "ᚦ",
    "ᚩ",
    "ᚱ",
    "ᚳ",
    "ᚷ",
    "ᚹ",
    "ᚻ",
    "ᚾ",
    "ᛁ",
    "ᛄ",
    "ᛇ",
    "ᛈ",
    "ᛉ",
    "ᛋ",
    "ᛏ",
    "ᛒ",
    "ᛖ",
    "ᛗ",
    "ᛚ",
    "ᛝ",
    "ᛟ",
    "ᛞ",
    "ᚪ",
    "ᚫ",
    "ᚣ",
    "ᛡ",
    "ᛠ",
]

CICADA_ENGLISH_ALPHABET = [
    "F",
    "U",
    "TH",
    "O",
    "R",
    "C",
    "G",
    "W",
    "H",
    "N",
    "I",
    "J",
    "EO",
    "P",
    "X",
    "S",
    "T",
    "B",
    "E",
    "M",
    "L",
    "NG",
    "OE",
    "D",
    "A",
    "AE",
    "Y",
    "IA",
    "EA",
]


def randomrunes(l: int, max: int = 29) -> list[int]:
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
    l = numberToBase(input, 29)
    if padding == -1:
        return l
    else:
        pad_value = 0
        pad_size = padding - len(l)
        final_list = [*[pad_value] * pad_size, *l]
        return final_list


class RuneIterator:
    """
    iterates over runes length L, [0,0,0], [0,0,1], [0,0,2], ..., [0,0,28], [0,1,0], ...
    """

    i: int
    maximum: int
    length: int

    def __init__(self, length: int):
        self.length = length
        self.maximum = 29**length

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


def print_all(runes: list[int], limit: int = 0) -> None:
    print_rune(runes, limit)
    print_rune_index(runes, limit)
    print_english(runes, limit)


def print_english(runes: list[int], limit: int = 0) -> None:
    """
    prints rune output translated back to english letters
    """
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("ENGLISH:  ", end="")
    for i in range(0, limit):
        print("{:2} ".format(CICADA_ENGLISH_ALPHABET[runes[i]]), end="")
    print()


def print_rune_index(runes: list[int], limit: int = 0) -> None:
    """
    prints rune output translated back to english letters
    """
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("RUNEIDX: ", end="")
    for i in range(0, limit):
        print(f"{runes[i]:02} ", end="")
    print()


def print_rune(runes: list[int], limit: int = 0) -> None:
    """
    prints rune output translated back to english letters
    """
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("RUNES  :  ", end="")
    for i in range(0, limit):
        print("{:2} ".format(CICADA_ALPHABET[runes[i]]), end="")
    print()
