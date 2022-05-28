#!/usr/bin/env python3

from . import autokey
from .. structures.alphabet import Alphabet, UPPERCASE_ALPHABET
from .. structures.sequence import Sequence

def test_plaintext_autokey_vigenere_x():
    demo_key = Sequence("X", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence("NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET)
    demo_ciphertext = Sequence("KBHBNDOKURKXVDMSLXV", alphabet=UPPERCASE_ALPHABET)
    assert autokey.plaintext_autokey_vigenere_encrypt(plaintext=demo_plaintext, primer=demo_key) == demo_ciphertext
    assert autokey.plaintext_autokey_vigenere_decrypt(ciphertext=demo_ciphertext, primer=demo_key) == demo_plaintext

def test_plaintext_autokey_vigenere_typewriter():
    demo_key = Sequence("TYPEWRITER", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence("NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET)
    demo_ciphertext = Sequence("GMIMBPYNEIGSKUFQJYR", alphabet=UPPERCASE_ALPHABET)
    assert autokey.plaintext_autokey_vigenere_encrypt(plaintext=demo_plaintext, primer=demo_key) == demo_ciphertext
    assert autokey.plaintext_autokey_vigenere_decrypt(ciphertext=demo_ciphertext, primer=demo_key) == demo_plaintext

def test_ciphertext_autokey_vigenere_x():
    demo_key = Sequence("X", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence("NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET)
    demo_ciphertext = Sequence("KYRZECSMMDWARDDVOSJ", alphabet=UPPERCASE_ALPHABET)
    assert autokey.ciphertext_autokey_vigenere_encrypt(plaintext=demo_plaintext, primer=demo_key) == demo_ciphertext
    assert autokey.ciphertext_autokey_vigenere_encrypt(ciphertext=demo_ciphertext, primer=demo_key) == demo_plaintext

def test_ciphertext_autokey_vigenere_typewriter():
    demo_key = Sequence("TYPEWRITER", alphabet=UPPERCASE_ALPHABET)
    demo_plaintext = Sequence("NOTIFYQUARTERMASTER", alphabet=UPPERCASE_ALPHABET)
    demo_ciphertext = Sequence("GMIMBPYNEIGSKUFQJYR", alphabet=UPPERCASE_ALPHABET)
    assert autokey.ciphertext_autokey_vigenere_encrypt(plaintext=demo_plaintext, primer=demo_key) == demo_ciphertext
    assert autokey.ciphertext_autokey_vigenere_encrypt(ciphertext=demo_ciphertext, primer=demo_key) == demo_plaintext
