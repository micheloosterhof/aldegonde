from aldegonde import pgsc

"""
Key text: Monarchy
Plain text: instruments
Cipher text: gatlmzclrqtx
"""
KEY = "MONARCHY"
PLAIN = "INSTRUMENTS"
CIPHER = "GATLMZCLRQTX"


def test_playfair_encrypt() -> None:
    """ """
    assert pgsc.playfair_encrypt(plaintext=PLAIN, keyword=KEY) == CIPHER


def test_playfair_decrypt() -> None:
    """ """
    assert pgsc.playfair_decrypt(ciphertext=CIPHER, keyword=KEY) == PLAIN + "Z"
