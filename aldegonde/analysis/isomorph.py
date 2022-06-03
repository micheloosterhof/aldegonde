from ..structures import sequence


def isomorph(ciphertext: sequence.Sequence) -> str:
    """
    Input is a piece of ciphertext as a list of int
    Output is this normalized as an isomorph, it's output as a string for easy comparison in alphabet A-Z
    Example ATTACK and EFFECT both normalize to ABBACD
    """
    output = ""
    letter = "A"
    mapping: dict[int, str] = {}
    for r in ciphertext:
        if r not in mapping:
            mapping[r] = letter
            letter = chr(ord(letter) + 1)
        output = output + mapping[r]
    return output
