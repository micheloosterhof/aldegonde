#!/usr/bin/env pypy3

MAX = 29

from lib import *

nils = [0] * 30
ones = [1] * 30
rand = range(0, MAX + 1)


def test_ioc_random():
    assert ioc(rand) == 0.0


def test_ioc_uniform():
    assert ioc(ones) == MAX
    assert ioc(nils) == MAX


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


def test_split_by_doublet():
    inp = [0, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10]
    outp = [[0, 1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]]
    assert split_by_doublet(inp) == outp


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
