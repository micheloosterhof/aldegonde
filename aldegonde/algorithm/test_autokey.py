
from . import autokey
from .. structures.alphabet import Alphabet, a2i
from .. structures.sequence import Sequence

def test_autokey_vigenere():
    # demo_alphabet = Alphabet("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    demo_key = Sequence("X")
    demo_plaintext = Sequence("NOTIFYQUARTERMASTER")
    demo_ciphertext = a2i("KBHBNDOKURKXVDMSLXV")
    assert autokey.plaintext_autokey_vigenere_encrypt(plaintext=demo_plaintext, primer=demo_key) == demo_ciphertext
    assert autokey.plaintext_autokey_vigenere_decrypt(ciphertext=demo_ciphertext, primer=demo_key) == demo_plaintext


def test_ciphertext_autokey_vigenere():
    demo_key = Sequence("X")
    demo_plaintext = Sequence("NOTIFYQUARTERMASTER")
    demo_ciphertext = a2i("KYRZECSMMDWARDDVOSJ")
    assert autokey.ciphertext_autokey_vigenere_encrypt(plaintext=demo_plaintext, primer=demo_key) == demo_ciphertext
    assert autokey.ciphertext_autokey_vigenere_encrypt(ciphertext=demo_ciphertext, primer=demo_key) == demo_plaintext






