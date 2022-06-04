#!/usr/bin/env python3

from ..structures.alphabet import UPPERCASE_ALPHABET
from ..structures.sequence import Sequence

from .vigenere import vigenere_encrypt, vigenere_decrypt
from .vigenere import vigenere_encrypt_with_alphabet, vigenere_decrypt_with_alphabet


def test_vigenere():
    key = Sequence(text="LEMON", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence(text="ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    ciphertext = Sequence(text="LXFOPVEFRNHR", alphabet=UPPERCASE_ALPHABET)
    a = vigenere_encrypt(plaintext=plaintext, primer=key)
    assert ciphertext == vigenere_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == vigenere_decrypt(ciphertext=ciphertext, primer=key)


def z_test_vigenere_with_custom_alphabet():
    demo_alphabet = Sequence(
        text="KRYPTOSABCDEFGHIJLMNQUVWXZ", alphabet=UPPERCASE_ALPHABET
    )
    demo_key = Sequence("PALIMPSEST", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_string = Sequence(
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD",
        alphabet=UPPERCASE_ALPHABET,
    )
    demo_cipher_decoded = Sequence(
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION",
        alphabet=UPPERCASE_ALPHABET,
    )
    assert demo_cipher_string == vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )


def z_test_vigenere_with_standard_alphabet():
    demo_alphabet = Sequence("ABCDEFGHIJKLMNOPQRSTUVWXYZ", alphabet=UPPERCASE_ALPHABET)
    demo_key = Sequence("LEMON", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_string = Sequence("LXFOPVEFRNHR", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_decoded = Sequence("ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    assert demo_cipher_string == vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )
