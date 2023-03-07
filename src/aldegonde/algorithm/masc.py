"""monoalphabetic substitution cipher
"""

import random

from aldegonde.structures.alphabet import Alphabet
from aldegonde.structures.sequence import Sequence


def monoalphabetic_substitution_encrypt(
    plaintext: Sequence, key: list[int]
) -> Sequence:
    """
    Monalphabetic substitution
    """
    output = []
    for e in plaintext:
        output.append(key[e])
    outputseq: Sequence = Sequence.fromlist(
        data=output, alphabet=plaintext.alphabet.alphabet
    )
    return outputseq


def reverse_key(key: list[int]) -> list[int]:
    """Takes an array containing all elements and reverses the index and the value
    Returns output if the input contains valid values, else raises ValueError
    """
    output = [-1] * len(key)
    for i in key:
        try:
            output[key[i]] = i
        except IndexError:
            raise ValueError
    for i in output:
        if i == -1:
            raise ValueError
    return output


def monoalphabetic_substitution_decrypt(
    ciphertext: Sequence, key: list[int]
) -> Sequence:
    """Monalphabetic substitution
    NOTE: key input is the same as for encryption, this function will reverse the key
    """
    reversed_key = reverse_key(key)
    print(f"revkey: {reversed_key}")
    output = []
    for e in ciphertext:
        output.append(reversed_key[e])
    outputseq: Sequence = Sequence.fromlist(
        data=output, alphabet=ciphertext.alphabet.alphabet
    )
    return outputseq


def randomkey(length: int) -> list[int]:
    """Generate a random key for use the previous functions"""
    return random.sample(list(range(length)), length)
