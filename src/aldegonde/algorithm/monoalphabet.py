"""monoalphabetic substitution
"""

import random


def monoalphabetic_substitution_encrypt(
    sequence: list[int], key: list[int]
) -> list[int]:
    """
    Monalphabetic substitution
    """
    output = []
    for e in sequence:
        output.append(key[e])
    return output


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
    sequence: list[int], key: list[int]
) -> list[int]:
    """Monalphabetic substitution
    NOTE: key input is the same as for encryption, this function will reverse the key
    """
    reversed_key = reverse_key(key)
    # print(f"revkey: {reversed_key}")
    output = []
    for e in sequence:
        output.append(reversed_key[e])
    return output


def randomkey(length: int) -> list[int]:
    """Generate a random key for use the previous functions"""
    return random.sample(list(range(length)), length)
