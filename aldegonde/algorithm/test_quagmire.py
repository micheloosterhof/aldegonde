from ..structures.alphabet import UPPERCASE_ALPHABET
from ..structures.sequence import Sequence

from .vigenere import vigenere_encrypt_with_alphabet, vigenere_decrypt_with_alphabet

"""
From: https://sites.google.com/site/cryptocrackprogram/user-guide/cipher-types/substitution/quagmire

Type: Quagmire 1
Plaintext keyword: PAULBRANDT
Indicator keyword: BRANDT
Indicator position: A
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontle tanyon etelly outhes kyisth elimit whenth ereare footpr intson themoo n
    Ciphertext: HIFUFC IRFKUY KYJPFQ SSHZMM QONGKF KTNDQA WDJSKF KVJNHC LIRUCX OWHGUY IDJDUK G
"""

def test_quagmire_1():
    return 0

    demo_alphabet = Sequence(
        text="PAULBRNDTCEFGHIJKMOQSVWXYZ", alphabet=UPPERCASE_ALPHABET
    )
    demo_key = Sequence("BRANDT", alphabet=UPPERCASE_ALPHABET)
    demo_ciphertext = Sequence(
        "HIFUFCIRFKUYKYJPFQSSHZMMQONGKFKTNDQAWDJSKFKVJNHCLIRUCXOWHGUYIDJDUKG",
        alphabet=UPPERCASE_ALPHABET,
    )
    demo_plaintext = Sequence(
        "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON",
        alphabet=UPPERCASE_ALPHABET,
    )
    assert demo_ciphertext == vigenere_encrypt_with_alphabet(
        plaintext=demo_plaintext, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_plaintext == vigenere_decrypt_with_alphabet(
        ciphertext=demo_ciphertext, primer=demo_key, alphabet=demo_alphabet
    )

def test_vigenere_with_custom_alphabet():
    demo_alphabet = Sequence(
        text="KRYPTOSABCDEFGHIJLMNQUVWXZ", alphabet=UPPERCASE_ALPHABET
    )
    demo_key = Sequence("PALIMPSEST", alphabet=UPPERCASE_ALPHABET)
    demo_cipher_string = Sequence(
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD",
        alphabet=UPPERCASE_ALPHABET,
    )
    demo_cipher_decoded = Sequence(
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION",
        alphabet=UPPERCASE_ALPHABET,
    )
    assert demo_cipher_string == vigenere_encrypt_with_alphabet(
        plaintext=demo_cipher_decoded, primer=demo_key, alphabet=demo_alphabet
    )
    assert demo_cipher_decoded == vigenere_decrypt_with_alphabet(
        ciphertext=demo_cipher_string, primer=demo_key, alphabet=demo_alphabet
    )






"""
Type: Quagmire 2

Ciphertext keyword: PAULBRANDT
Indicator keyword: BRANDT
Indicator position: C
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontle tanyon etelly outhes kyisth elimit whenth ereare footpr intson themoo n
    Ciphertext: RMGXKE VLGUQQ NWLJKB KXOFCY GADWYH NIDKHZ YELMYH NSLBWE DMHXSX EKOWQQ VELKQS J

Type: Quagmire 3
Plain/Ciphertext keywords: PAULBRANDT
Indicator keyword: BRANDT
Indicator position: P
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontle tanyon etelly outhes kyisth elimit whenth ereare footpr intson themoo n
    Ciphertext: FXDIEO GNDBZI IHFCEN WDCQMU SLJPJV ITJXVK POFGJV IEFDGO JXQIDH OFCPZI GOFXZP E

Type: Quagmire 4
Plaintext keyword: PAULBRANDT
Ciphertext keyword: BRANDT
Indicator keyword: COUNTRY
Indicator position: P
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontlet anyonet ellyout heskyis thelimi twhenth erearef ootprin tsonthe moon
    Ciphertext: KFBIFIC EWQVIIC OSXRXNC SBLSNMQ LNDCSQJ LJEKIGI OVDDHIG YFANHMD LHJGKLF XFJG
"""
