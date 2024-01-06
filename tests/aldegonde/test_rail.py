from aldegonde import rail

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_rail() -> None:
    # PLAIN = """WE ARE DISCOVERED FLEE AT ONCE"""
    # CIPHER = """WECRL TEERD SOEEF EAOCA IVDEN"""
    PLAIN = """WEAREDISCOVEREDFLEEATONCE"""
    CIPHER = """WECRLTEERDSOEEFEAOCAIVDEN"""
    key = 3
    ciphertext = rail.rail_encrypt(PLAIN, key=key)
    assert tuple(ciphertext) == tuple(e for e in CIPHER)
    plaintext = rail.rail_decrypt(CIPHER, key=key)
    assert tuple(plaintext) == tuple(e for e in PLAIN)


def test_scytale() -> None:
    PLAIN = """WEAREDISCOVEREDFLEEATONCE"""
    CIPHER = """WOEEVEAEARRTEEODDNIFCSLEC"""
    key = 3
    ciphertext = rail.scytale_encrypt(PLAIN, key=key)
    assert tuple(ciphertext) == tuple(e for e in CIPHER)
    plaintext = rail.scytale_decrypt(CIPHER, key=key)
    assert tuple(plaintext) == tuple(e for e in PLAIN)
