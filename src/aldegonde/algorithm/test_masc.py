#!/usr/bin/env python3

from aldegonde.structures.alphabet import UPPERCASE_ALPHABET
from aldegonde.structures.sequence import Sequence
from aldegonde.algorithm import masc


def test_masc() -> None:
    plaintext = Sequence.fromstr(text="ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    key = masc.randomkey(length=len(plaintext.alphabet))
    print(key)
    ciphertext = masc.monoalphabetic_substitution_encrypt(plaintext, key)
    print(ciphertext)
    assert plaintext == masc.monoalphabetic_substitution_decrypt(
        ciphertext=ciphertext, key=key
    )
