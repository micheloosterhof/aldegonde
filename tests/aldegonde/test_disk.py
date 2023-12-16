from aldegonde import disk


def test_disk_wheatstone() -> None:
    """https://eprint.iacr.org/2020/1492.pdf"""
    plainabc = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cipherabc = "SCQEDRBFUAGVHWTIXOJYPKZMLN"
    plaintext = "SECRET MESQAGE "
    ciphertext = "YBRPUMDOGLMUTWA"
    assert list(disk.disk_encrypt(plaintext, plainabc, cipherabc)) == list(ciphertext)
    assert list(disk.disk_decrypt(ciphertext, plainabc, cipherabc)) == list(plaintext)


# def test_disk_wadsworth() -> None:
#    cipherabc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ2345678"
#    plainabc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#    plaintext = ""
#    ciphertext = ""
#    assert list(disk.disk_encrypt(plaintext, plainabc, cipherabc)) == list(ciphertext)
#    assert list(disk.disk_decrypt(ciphertext, plainabc, cipherabc)) == list(plaintext)


#
# def test_plaintext_disk_vigenere_typewriter() -> None:
#     primer = "TYPEWRITER"
#     tr = pasc.vigenere_tr(ABC)
#     plaintext = "NOTIFYQUARTERMASTER"
#     ciphertext = "GMIMBPYNEIGSKUFQJYR"
#     assert list(auto.plaintext_disk_encrypt(plaintext, primer, tr)) == list(
#         ciphertext
#     )
#     assert list(auto.plaintext_disk_decrypt(ciphertext, primer, tr)) == list(
#         plaintext
#     )
#
#
# def test_ciphertext_disk_vigenere_x() -> None:
#     primer = "X"
#     tr = pasc.vigenere_tr(ABC)
#     plaintext = "NOTIFYQUARTERMASTER"
#     ciphertext = "KYRZECSMMDWARDDVOSJ"
#     assert list(auto.ciphertext_disk_encrypt(plaintext, primer, tr)) == list(
#         ciphertext
#     )
#     assert list(auto.ciphertext_disk_decrypt(ciphertext, primer, tr)) == list(
#         plaintext
#     )
#
#
# def test_ciphertext_disk_vigenere_typewriter() -> None:
#     primer = "TYPEWRITER"
#     tr = pasc.vigenere_tr(ABC)
#     plaintext = "NOTIFYQUARTERMASTER"
#     ciphertext = "GMIMBPYNEIZQZYBHRRV"
#     assert list(auto.ciphertext_disk_encrypt(plaintext, primer, tr)) == list(
#         ciphertext
#     )
#     assert list(auto.ciphertext_disk_decrypt(ciphertext, primer, tr)) == list(
#         plaintext
#     )
