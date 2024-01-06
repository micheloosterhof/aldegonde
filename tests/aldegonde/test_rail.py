from aldegonde import rail

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#PLAIN = """WE ARE DISCOVERED FLEE AT ONCE"""
#CIPHER = """WECRL TEERD SOEEF EAOCA IVDEN"""
PLAIN = """WEAREDISCOVEREDFLEEATONCE"""
CIPHER = """WECRLTEERDSOEEFEAOCAIVDEN"""
key = 3

def test_railencrypt() -> None:
    ciphertext = rail.rail_encrypt(PLAIN, key=key)
    assert tuple(ciphertext) == tuple(e for e in CIPHER)

def test_rail_decrypt() -> None:
    plaintext = rail.rail_decrypt(CIPHER, key=key)
    assert tuple(plaintext) == tuple(e for e in PLAIN)
