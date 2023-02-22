"""Quagmire variants
From: https://sites.google.com/site/cryptocrackprogram/user-guide/cipher-types/substitution/quagmire
"""

from aldegonde.structures.alphabet import Alphabet
from aldegonde.structures.sequence import Sequence


def quagmire1_encrypt(
    plaintext: Sequence,
    indicator_keyword: str,
    indicator_position: str,
    plaintext_alphabet: str,
    ciphertext_alphabet: str,
    trace: bool = False,
) -> Sequence:
    output: Sequence = Sequence(alphabet=plaintext.alphabet)
    qtr = quagmire_tabula_recta(
        plaintext_alphabet=plaintext_alphabet,
        ciphertext_alphabet=ciphertext_alphabet,
        indicator_position=indicator_position,
        indicator_keyword=indicator_keyword,
    )
    for i, e in enumerate(plaintext):
        modifier = indicator_keyword[i % len(indicator_keyword)]
        output.append(qtr[e, modifier])
    return output


def quagmire1_decrypt(
    ciphertext: Sequence, plaintext_alphabet: Sequence, trace: bool = False
) -> Sequence:
    output: Sequence = Sequence(alphabet=ciphertext.alphabet)
    for i, e in enumerate(ciphertext):
        output.append((e - primer[i % len(primer)]) % len(output.alphabet))
    return output


def quagmire_tabula_recta(alphabet: Alphabet, trace: bool = True) -> list[list[str]]:
    """
    construct a tabula recta based on custom alphabet.
    output is a MAX*MAX matrix
    """
    output: list[list[str]] = []
    for shift in range(0, len(alphabet)):
        output.append(alphabet[shift:] + alphabet[:shift])
    if trace:
        print(repr(output))
    return output


"""
The Quagmire group of periodic ciphers are similar to the Vigenère
cipher but use one or more mixed alphabets. There are four variations;
I, II, III and IV. The simplest of these, the Quagmire I cipher,
is constructed from a keyed plaintext alphabet created from the
keyword with repeated letters being omitted and followed by the
unused letters of the alphabet in alphabetic order. For example the
keyword PAULBRANDT is reduced to PAULBRNDT when repeated letters
are removed. Appending unused alphabet letters produces the following
keyed alphabet:

PAULBRNDTCEFGHIJKMOQSVWXYZ

The Quagmires 2, 3 and 4 are constructed in a similar way except:

Quagmire 2 uses a straight (A-Z) alphabet for the plaintext and a keyed alphabet for the ciphertext,

Quagmire 3 uses a keyed alphabet for the plaintext and the same keyed alphabet for the ciphertext,

Quagmire 4 uses a keyed alphabet for the plaintext and a different keyed alphabet for the ciphertext.
"""


def quagmire1_encrypt(
    plaintext: Sequence,
    primer: Sequence,
    alphabet: list[int],
    trace: bool = False,
) -> Sequence:
    """
    Quagmire I Encrypt
    """
    output: Sequence = Sequence(alphabet=plaintext.alphabet)
    if not alphabet:
        alphabet = list(range(0, len(plaintext.alphabet) + 1))
    tr: list[list[int]] = construct_tabula_recta(alphabet)
    abc = list(alphabet)

    for i in range(0, len(plaintext)):
        row_index = abc.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = abc.index(plaintext[i])
        output.append(tr[row_index][column_index])

    return output


def quagmire1_decrypt(
    ciphertext: Sequence,
    primer: Sequence,
    alphabet: list[int],
    trace: bool = False,
) -> Sequence:
    """
    Quagmire I Decrypt
    """
    output: Sequence = Sequence(alphabet=ciphertext.alphabet)
    if not alphabet:
        alphabet = list(range(0, len(ciphertext.alphabet) + 1))
    tr: list[list[int]] = construct_tabula_recta(alphabet)

    for i, e in enumerate(ciphertext):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = row.index(e)
        output.append(alphabet[column_index])

    return output


def keyword_generator(keyword: str, alphabet: str) -> str:
    """Custom alphabet generator, takes a keyword, and

    example: keyword:  PAULBRANDT
             alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ
             returns:  PAULBRNDTCEFGHIJKMOQSVWXYZ
    """
    output: str = ""
    assert False not in [letter in alphabet for letter in keyword]

    for letter in keyword:
        if not letter in output:
            output += letter
    for letter in alphabet:
        if not letter in output:
            output += letter

    assert len(output) == len(alphabet)
    return output
