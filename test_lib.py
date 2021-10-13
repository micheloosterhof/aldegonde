#!/usr/bin/env pypy3

MAX=29

from lib import *

nuls = [0] * 30
ones = [1] * 30
rand = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]

print(nuls)
print(ioc(nuls))

print(ones)
print(ioc(ones))

print(rand)
print(ioc(rand))

def test_ioc_random():
    assert ioc(rand)==0.0
    
def test_ioc_uniform():
    assert ioc(ones)==29.0

# sanity check
def autokey():
    assert ciphertext_autokey_beaufort_decrypt(ciphertext_autokey_beaufort_encrypt(rand)) == rand
    assert ciphertext_autokey_vigenere_decrypt(ciphertext_autokey_vigenere_encrypt(rand)) == rand
    assert ciphertext_autokey_minuend_decrypt(ciphertext_autokey_minuend_encrypt(rand)) == rand
    assert plaintext_autokey_beaufort_decrypt(plaintext_autokey_beaufort_encrypt(rand)) == rand
    assert plaintext_autokey_vigenere_decrypt(plaintext_autokey_vigenere_encrypt(rand)) == rand
    assert plaintext_autokey_minuend_decrypt(plaintext_autokey_minuend_encrypt(rand)) == rand
