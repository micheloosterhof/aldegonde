from aldegonde import auto, pasc

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_plaintext_autokey_vigenere_x() -> None:
    tr = pasc.vigenere_tr(ABC)
    primer = "X"
    plaintext = "NOTIFYQUARTERMASTER"
    ciphertext = "KBHBNDOKURKXVDMSLXV"
    assert list(auto.plaintext_autokey_encrypt(plaintext, primer, tr)) == list(
        ciphertext,
    )
    assert list(auto.plaintext_autokey_decrypt(ciphertext, primer, tr)) == list(
        plaintext,
    )


def test_plaintext_autokey_vigenere_typewriter() -> None:
    primer = "TYPEWRITER"
    tr = pasc.vigenere_tr(ABC)
    plaintext = "NOTIFYQUARTERMASTER"
    ciphertext = "GMIMBPYNEIGSKUFQJYR"
    assert list(auto.plaintext_autokey_encrypt(plaintext, primer, tr)) == list(
        ciphertext,
    )
    assert list(auto.plaintext_autokey_decrypt(ciphertext, primer, tr)) == list(
        plaintext,
    )


def test_ciphertext_autokey_vigenere_x() -> None:
    primer = "X"
    tr = pasc.vigenere_tr(ABC)
    plaintext = "NOTIFYQUARTERMASTER"
    ciphertext = "KYRZECSMMDWARDDVOSJ"
    assert list(auto.ciphertext_autokey_encrypt(plaintext, primer, tr)) == list(
        ciphertext,
    )
    assert list(auto.ciphertext_autokey_decrypt(ciphertext, primer, tr)) == list(
        plaintext,
    )


def test_ciphertext_autokey_vigenere_typewriter() -> None:
    primer = "TYPEWRITER"
    tr = pasc.vigenere_tr(ABC)
    plaintext = "NOTIFYQUARTERMASTER"
    ciphertext = "GMIMBPYNEIZQZYBHRRV"
    assert list(auto.ciphertext_autokey_encrypt(plaintext, primer, tr)) == list(
        ciphertext,
    )
    assert list(auto.ciphertext_autokey_decrypt(ciphertext, primer, tr)) == list(
        plaintext,
    )
