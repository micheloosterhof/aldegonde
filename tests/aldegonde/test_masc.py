from aldegonde import masc
from aldegonde.exceptions import AldegondeKeyError

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALICE = (
    "ALICEWASBEGINNINGTOGETVERYTIREDOFSITTINGBYHERSISTERONTHEBANKANDOFHAVINGNOTHINGTO"
)


def test_masc_encrypt_random() -> None:
    rnd = masc.randomkey(ABC)
    ciphertext = masc.masc_encrypt(ALICE, key=rnd)
    plaintext = masc.masc_decrypt(ciphertext, key=rnd)
    assert tuple(ALICE) == tuple(e for e in plaintext)


def test_masc_encrypt_caesar() -> None:
    caesar = masc.shiftedkey(ABC, shift=3)
    ciphertext = masc.masc_encrypt(ALICE, key=caesar)
    plaintext = masc.masc_decrypt(ciphertext, key=caesar)
    assert tuple(ALICE) == tuple(e for e in plaintext)


def test_reverse_key() -> None:
    assert masc.shiftedkey(ABC, shift=13) == masc.reverse_key(
        masc.shiftedkey(ABC, shift=13),
    )


def test_atbashkey() -> None:
    ATBASH_CIPHERTEXT = "ZGGZXPZGWZDM"
    ATBASH_PLAINTEXT = "ATTACKATDAWN"
    assert masc.atbashkey("ABC") == {"A": "C", "B": "B", "C": "A"}
    atbash = masc.atbashkey(ABC)
    assert "".join(masc.masc_encrypt(ATBASH_PLAINTEXT, key=atbash)) == ATBASH_CIPHERTEXT
    assert "".join(masc.masc_decrypt(ATBASH_CIPHERTEXT, key=atbash)) == ATBASH_PLAINTEXT


def test_shiftedkey() -> None:
    assert masc.shiftedkey(ABC, shift=3) == masc.shiftedkey(ABC, shift=-23)
    assert masc.shiftedkey(ABC, shift=3) == masc.shiftedkey(ABC, shift=29)


def test_affinekey() -> None:
    assert masc.affinekey(ABC, a=3, b=8) == masc.affinekey(ABC, a=3, b=8)
    try:
        assert masc.affinekey(ABC, a=2, b=8) == masc.affinekey(ABC, a=2, b=8)
    except (ValueError, AldegondeKeyError):
        assert 1 == 1
    AFFINE_CIPHERTEXT = "OYHYJLEVYQBLSRIJLYEC"
    AFFINE_PLAINTEXT = "CELEBRATESPRINGBREAK"
    AFFINE_KEY_A = 5
    AFFINE_KEY_B = 4
    affine = masc.affinekey(ABC, a=AFFINE_KEY_A, b=AFFINE_KEY_B)
    assert "".join(masc.masc_encrypt(AFFINE_PLAINTEXT, key=affine)) == AFFINE_CIPHERTEXT
    assert "".join(masc.masc_decrypt(AFFINE_CIPHERTEXT, key=affine)) == AFFINE_PLAINTEXT


def test_mixedalphabet() -> None:
    assert masc.mixedalphabet("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "PAULBRANDT") == list(
        "PAULBRNDTCEFGHIJKMOQSVWXYZ",
    )


def test_cycles() -> None:
    """example, key FLYINGSAUCERBDHJKMOPQTVWXZ
    has cycles: (AFGSOH) (BLRM) (CYXWVTPJ) (DIUQKEN) (Z)
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mixedalphabet = "FLYINGSAUCERBDHJKMOPQTVWXZ"
    key = masc.mixedalphabet2key(plainalphabet=alphabet, cipheralphabet=mixedalphabet)
    cycles = [list(x) for x in ["AFGSOH", "BLRM", "CYXWVTPJ", "DIUQKEN", "Z"]]
    assert masc.cycles(key) == cycles
