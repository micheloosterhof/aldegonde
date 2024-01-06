from aldegonde import trns

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_rail() -> None:
    # PLAIN = """WE ARE DISCOVERED FLEE AT ONCE"""
    # CIPHER = """WECRL TEERD SOEEF EAOCA IVDEN"""
    PLAIN = """WEAREDISCOVEREDFLEEATONCE"""
    CIPHER = """WECRLTEERDSOEEFEAOCAIVDEN"""
    key = 3
    ciphertext = trns.rail_encrypt(PLAIN, key=key)
    assert tuple(ciphertext) == tuple(e for e in CIPHER)
    plaintext = trns.rail_decrypt(CIPHER, key=key)
    assert tuple(plaintext) == tuple(e for e in PLAIN)


def test_scytale() -> None:
    PLAIN = """WEAREDISCOVEREDFLEEATONCE"""
    CIPHER = """WOEEVEAEARRTEEODDNIFCSLEC"""
    key = 3
    ciphertext = trns.scytale_encrypt(PLAIN, key=key)
    assert tuple(ciphertext) == tuple(e for e in CIPHER)
    plaintext = trns.scytale_decrypt(CIPHER, key=key)
    assert tuple(plaintext) == tuple(e for e in PLAIN)
