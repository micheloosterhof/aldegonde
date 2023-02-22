#!/usr/bin/env python3

from aldegonde.algorithms import autokey
from aldegonde.structures.alphabet import UPPERCASE_ALPHABET
from aldegonde.structures.sequence import Sequence


def test_plaintext_autokey_vigenere_x() -> None:
    demo_key = Sequence.fromstr("X", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence.fromstr(
        "NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET
    )
    demo_ciphertext = Sequence.fromstr(
        "KBHBNDOKURKXVDMSLXV", alphabet=UPPERCASE_ALPHABET
    )
    assert (
        autokey.plaintext_autokey_vigenere_encrypt(
            plaintext=demo_plaintext, primer=demo_key
        )
        == demo_ciphertext
    )
    assert (
        autokey.plaintext_autokey_vigenere_decrypt(
            ciphertext=demo_ciphertext, primer=demo_key
        )
        == demo_plaintext
    )


def test_plaintext_autokey_vigenere_typewriter() -> None:
    demo_key = Sequence.fromstr("TYPEWRITER", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence.fromstr(
        "NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET
    )
    demo_ciphertext = Sequence.fromstr(
        "GMIMBPYNEIGSKUFQJYR", alphabet=UPPERCASE_ALPHABET
    )
    assert (
        autokey.plaintext_autokey_vigenere_encrypt(
            plaintext=demo_plaintext, primer=demo_key
        )
        == demo_ciphertext
    )
    assert (
        autokey.plaintext_autokey_vigenere_decrypt(
            ciphertext=demo_ciphertext, primer=demo_key
        )
        == demo_plaintext
    )


def test_ciphertext_autokey_vigenere_x() -> None:
    demo_key = Sequence.fromstr("X", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence.fromstr(
        "NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET
    )
    demo_ciphertext = Sequence.fromstr(
        "KYRZECSMMDWARDDVOSJ", alphabet=UPPERCASE_ALPHABET
    )
    assert (
        autokey.ciphertext_autokey_vigenere_encrypt(
            plaintext=demo_plaintext, primer=demo_key
        )
        == demo_ciphertext
    )
    assert (
        autokey.ciphertext_autokey_vigenere_decrypt(
            ciphertext=demo_ciphertext, primer=demo_key
        )
        == demo_plaintext
    )

    assert (
        autokey.ciphertext_autokey_encrypt(
            plaintext=demo_plaintext, primer=demo_key, encryptf=autokey.vigenere_encrypt
        )
        == demo_ciphertext
    )


def test_ciphertext_autokey_vigenere_typewriter() -> None:
    demo_key = Sequence.fromstr("TYPEWRITER", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence.fromstr(
        "NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET
    )
    demo_ciphertext = Sequence.fromstr(
        "GMIMBPYNEIGSKUFQJYR", alphabet=UPPERCASE_ALPHABET
    )
    assert (
        autokey.plaintext_autokey_vigenere_encrypt(
            plaintext=demo_plaintext, primer=demo_key
        )
        == demo_ciphertext
    )
    assert (
        autokey.plaintext_autokey_vigenere_decrypt(
            ciphertext=demo_ciphertext, primer=demo_key
        )
        == demo_plaintext
    )
