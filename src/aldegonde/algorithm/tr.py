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


def construct_tabula_recta(alphabet, trace: bool = False) -> list[list[int]]:
    """
    construct a tabula recta based on custom alphabet.
    output is a MAX*MAX matrix
    """
    output: list[list[int]] = []
    for shift in range(0, len(alphabet)):
        output.append(alphabet[shift:] + alphabet[:shift])
    if trace:
        print(repr(output))
    return output


TR = construct_tabula_recta(CICADA_ALPHABET)
for line in TR:
    print(line)
