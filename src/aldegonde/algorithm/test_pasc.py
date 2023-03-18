#!/usr/bin/env python3

from aldegonde.algorithm import pasc

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_vigenere() -> None:
    key = "LEMON"
    plaintext = "ATTACKATDAWN"
    ciphertext = "LXFOPVEFRNHR"
    assert list(ciphertext) == pasc.pasc_encrypt(plaintext, key, pasc.vigenere_tr(ABC))
    assert list(plaintext) == pasc.pasc_decrypt(ciphertext, key, pasc.vigenere_tr(ABC))


def test_beaufort() -> None:
    key = "FORTIFICATION"
    plaintext = "DEFENDTHEEASTWALLOFTHECASTLE"
    ciphertext = "CKMPVCPVWPIWUJOGIUAPVWRIWUUK"
    assert list(ciphertext) == pasc.pasc_encrypt(plaintext, key, pasc.beaufort_tr(ABC))
    assert list(plaintext) == pasc.pasc_decrypt(ciphertext, key, pasc.beaufort_tr(ABC))


def test_variantbeaufort() -> None:
    key = "CIPHER"
    plaintext = "HONESTYISTHEBESTPOLICY"
    ciphertext = "FGYXOCWADMDNZWDMLXJANR"
    assert list(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.variantbeaufort_tr(ABC)
    )
    assert list(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.variantbeaufort_tr(ABC)
    )


def test_quagmire1() -> None:
    """
    is this quagmire1?
    """
    return
    alphabet = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    key = "PALIMPSEST"
    ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    assert list(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.quagmire1_tr(alphabet)
    )
    assert list(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.quagmire1_tr(alphabet)
    )


def test_quagmire1b() -> None:
    """
    is this quagmire1?
    """
    return
    alphabet = "PAULBRNDTCEFGHIJKMOQSVWXYZ"
    key = "BRANDT"
    plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    ciphertext = "HIFUFCIRFKUYKYJPFQSSHZMMQONGKFKTNDQAWDJSKFKVJNHCLIRUCXOWHGUYIDJDUKG"
    assert list(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.quagmire1_tr(alphabet)
    )
    assert list(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.quagmire1_tr(alphabet)
    )
