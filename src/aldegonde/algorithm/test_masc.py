#!/usr/bin/env python3

from aldegonde.algorithm import masc

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALICE = (
    "ALICEWASBEGINNINGTOGETVERYTIREDOFSITTINGBYHERSISTERONTHEBANKANDOFHAVINGNOTHINGTO"
)


def test_masc_encrypt_random() -> None:
    rnd = masc.randomkey(ABC)
    ciphertext = masc.masc_encrypt(ALICE, key=rnd)
    plaintext = masc.masc_decrypt(ciphertext, key=rnd)
    assert tuple(ALICE) == plaintext


def test_masc_encrypt_caesar() -> None:
    caesar = masc.shiftedkey(ABC, shift=3)
    ciphertext = masc.masc_encrypt(ALICE, key=caesar)
    plaintext = masc.masc_decrypt(ciphertext, key=caesar)
    assert tuple(ALICE) == plaintext


def test_reverse_key() -> None:
    assert masc.shiftedkey(ABC, shift=13) == masc.reverse_key(
        masc.shiftedkey(ABC, shift=13)
    )


def test_shiftedkey() -> None:
    assert masc.shiftedkey(ABC, shift=3) == masc.shiftedkey(ABC, shift=-23)
    assert masc.shiftedkey(ABC, shift=3) == masc.shiftedkey(ABC, shift=29)


def test_affinekey() -> None:
    assert masc.affinekey(ABC, a=3, b=8) == masc.affinekey(ABC, a=3, b=8)
    try:
        assert masc.affinekey(ABC, a=2, b=8) == masc.affinekey(ABC, a=2, b=8)
    except ValueError:
        pass


def test_keywordkey() -> None:
    assert masc.keywordkey("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "PAULBRANDT") == list(
        "PAULBRNDTCEFGHIJKMOQSVWXYZ"
    )
