#!/usr/bin/env python3

from ..structures.alphabet import UPPERCASE_ALPHABET
from ..structures.sequence import Sequence

from .vigenere import vigenere_encrypt, vigenere_decrypt
from .vigenere import beaufort_encrypt, beaufort_decrypt
from .vigenere import variant_beaufort_encrypt, variant_beaufort_decrypt
from .vigenere import vigenere_encrypt_with_alphabet, vigenere_decrypt_with_alphabet


def test_vigenere() -> None:
    key = Sequence.fromstr(text="LEMON", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence.fromstr(text="ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    ciphertext = Sequence.fromstr(text="LXFOPVEFRNHR", alphabet=UPPERCASE_ALPHABET)
    assert ciphertext == vigenere_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == vigenere_decrypt(ciphertext=ciphertext, primer=key)


def test_beaufort() -> None:
    key = Sequence.fromstr(text="FORTIFICATION", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence.fromstr(
        text="DEFENDTHEEASTWALLOFTHECASTLE", alphabet=UPPERCASE_ALPHABET
    )
    ciphertext = Sequence.fromstr(
        text="CKMPVCP VWPIWUJOGIUAPVWRIWUUK", alphabet=UPPERCASE_ALPHABET
    )
    assert ciphertext == beaufort_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == beaufort_decrypt(ciphertext=ciphertext, primer=key)


def test_variant_variant_beaufort() -> None:
    key = Sequence.fromstr(text="CIPHER", alphabet=UPPERCASE_ALPHABET)
    plaintext = Sequence.fromstr(
        text="HONESTY IS THE BEST POLICY", alphabet=UPPERCASE_ALPHABET
    )
    ciphertext = Sequence.fromstr(
        text="FGYXOCWADMDNZWDMLXJANR", alphabet=UPPERCASE_ALPHABET
    )
    assert ciphertext == variant_beaufort_encrypt(plaintext=plaintext, primer=key)
    assert plaintext == variant_beaufort_decrypt(ciphertext=ciphertext, primer=key)


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
    assert demo_cipher_string == vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )


def test_vigenere_with_standard_alphabet() -> None:
    demo_alphabet = Sequence.fromstr(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ", alphabet=UPPERCASE_ALPHABET
    )
    demo_key = Sequence.fromstr("LEMON", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_string = Sequence.fromstr("LXFOPVEFRNHR", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_decoded = Sequence.fromstr("ATTACKATDAWN", alphabet=UPPERCASE_ALPHABET)
    assert demo_cipher_string == vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )