#!/usr/bin/env python3

from aldegonde.structures.alphabet import UPPERCASE_ALPHABET
from aldegonde.structures.sequence import Sequence
from aldegonde.algorithm import vigenere


def test_vigenere() -> None:
    key = Sequence.fromstr(text="LEMON", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence.fromstr(text="ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    ciphertext = Sequence.fromstr(text="LXFOPVEFRNHR", alphabet=UPPERCASE_ALPHABET)
    assert ciphertext == vigenere.vigenere_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == vigenere.vigenere_decrypt(ciphertext=ciphertext, primer=key)


def test_beaufort() -> None:
    key = Sequence.fromstr(text="FORTIFICATION", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence.fromstr(
        text="DEFENDTHEEASTWALLOFTHECASTLE", alphabet=UPPERCASE_ALPHABET
    )
    ciphertext = Sequence.fromstr(
        text="CKMPVCP VWPIWUJOGIUAPVWRIWUUK", alphabet=UPPERCASE_ALPHABET
    )
    assert ciphertext == vigenere.beaufort_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == vigenere.beaufort_decrypt(ciphertext=ciphertext, primer=key)


def test_variant_variant_beaufort() -> None:
    key = Sequence.fromstr(text="CIPHER", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence.fromstr(
        text="HONESTY IS THE BEST POLICY", alphabet=UPPERCASE_ALPHABET
    )
    ciphertext = Sequence.fromstr(
        text="FGYXOCWADMDNZWDMLXJANR", alphabet=UPPERCASE_ALPHABET
    )
    assert ciphertext == vigenere.variant_beaufort_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == vigenere.variant_beaufort_decrypt(ciphertext=ciphertext, primer=key)


def test_vigenere_with_custom_alphabet() -> None:
    demo_alphabet = Sequence.fromstr(
        text="KRYPTOSABCDEFGHIJLMNQUVWXZ", alphabet=UPPERCASE_ALPHABET
    )
    demo_key = Sequence.fromstr("PALIMPSEST", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_string = Sequence.fromstr(
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD",
        alphabet=UPPERCASE_ALPHABET,
    )
    demo_cipher_decoded = Sequence.fromstr(
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION",
        alphabet=UPPERCASE_ALPHABET,
    )
    assert demo_cipher_string == vigenere.vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere.vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )


def test_vigenere_with_standard_alphabet() -> None:
    demo_alphabet = Sequence.fromstr(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ", alphabet=UPPERCASE_ALPHABET
    )
    demo_key = Sequence.fromstr("LEMON", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_string = Sequence.fromstr("LXFOPVEFRNHR", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_decoded = Sequence.fromstr("ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    assert demo_cipher_string == vigenere.vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere.vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )
