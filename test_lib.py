#!/usr/bin/env pypy3

MAX = 29

from lib import *

nils = [0] * 300
ones = [1] * 300
rand = range(0, MAX + 1)


def test_ioc_random():
    assert ioc(rand) == 0.0


def test_ioc_uniform():
    assert ioc(ones) == 1.0
    assert ioc(nils) == 1.0


def test_ioc2_random():
    assert ioc2(rand) == 0.0


def test_ioc2_uniform():
    assert ioc2(ones) == MAX * MAX
    assert ioc2(nils) == MAX * MAX


def test_ioc2_random():
    assert ioc2(rand, cut=1) == 0.0


def test_ioc2_uniform():
    assert ioc2(ones, cut=1) == MAX * MAX
    assert ioc2(nils, cut=1) == MAX * MAX


def test_ioc2_random():
    assert ioc2(rand, cut=2) == 0.0


def test_ioc2_uniform():
    assert ioc2(ones, cut=2) == MAX * MAX
    assert ioc2(nils, cut=2) == MAX * MAX


def test_ioc3_random():
    assert ioc3(rand) == 0.0


def test_ioc3_uniform():
    assert ioc3(ones) == MAX * MAX * MAX


def test_isomorph():
    assert isomorph([0, 1, 2, 3, 4]) == isomorph([1, 2, 3, 4, 5])
    assert isomorph([0, 1, 1, 3, 5]) == isomorph([1, 2, 2, 9, 8])


def test_split_by_doublet():
    inp = [0, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10]
    outp = [[0, 1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]]
    assert split_by_doublet(inp) == outp


def test_split_by_slice():
    inp = [0, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10]
    outp = {0: [0, 3, 5, 7, 10], 1: [1, 4, 6, 8], 2: [2, 4, 7, 9]}
    assert split_by_slice(inp, 3) == outp


# sanity check
def autokey():
    assert (
        ciphertext_autokey_beaufort_decrypt(ciphertext_autokey_beaufort_encrypt(rand))
        == rand
    )
    assert (
        ciphertext_autokey_vigenere_decrypt(ciphertext_autokey_vigenere_encrypt(rand))
        == rand
    )
    assert (
        ciphertext_autokey_minuend_decrypt(ciphertext_autokey_minuend_encrypt(rand))
        == rand
    )
    assert (
        plaintext_autokey_beaufort_decrypt(plaintext_autokey_beaufort_encrypt(rand))
        == rand
    )
    assert (
        plaintext_autokey_vigenere_decrypt(plaintext_autokey_vigenere_encrypt(rand))
        == rand
    )
    assert (
        plaintext_autokey_minuend_decrypt(plaintext_autokey_minuend_encrypt(rand))
        == rand
    )


def vig2():
    assert (
        ciphertext_autokey_vig2_decrypt(ciphertext_autokey_vig2_encrypt(rand)) == rand
    )
    assert (
        ciphertext_autokey_oddvig_decrypt(ciphertext_autokey_oddvig_encrypt(rand))
        == rand
    )


def test_a2i():
    assert a2i("HYDRAULIC") == [7, 24, 3, 17, 0, 20, 11, 8, 2]


def test_i2a():
    assert i2a([7, 24, 3, 17, 0, 20, 11, 8, 2]) == "HYDRAULIC"


def test_vigenere_encrypt_with_custom_alphabet():
    demo_alphabet = a2i("KRYPTOSABCDEFGHIJLMNQUVWXZ")
    demo_key = a2i("PALIMPSEST")
    demo_cipher_string = a2i(
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
    )
    demo_cipher_decoded = a2i(
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    )
    assert demo_cipher_string == vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )


def test_vigenere_decrypt_with_custom_alphabet():
    demo_alphabet = a2i("KRYPTOSABCDEFGHIJLMNQUVWXZ")
    demo_key = a2i("PALIMPSEST")
    demo_cipher_string = a2i(
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
    )
    demo_cipher_decoded = a2i(
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    )
    assert demo_cipher_decoded == vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )
