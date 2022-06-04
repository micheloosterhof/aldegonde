# ciphertext autokey variations
# we can do 3 operations, 2 subtractions and 1 addition, addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P

from ..structures.alphabet import Alphabet
from ..structures.sequence import Sequence


def ciphertext_autokey_vigenere_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """
    Vigenere primitive without any console output, C=P+K
    """
    assert primer.alphabet == plaintext.alphabet
    key: Sequence = primer.copy()
    output = Sequence(alphabet=plaintext.alphabet)
    MAX = len(plaintext.alphabet)
    for j in range(0, len(plaintext)):
        c = (plaintext[j] + key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_vigenere_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """
    Vigenere primitive without any console output, P=C-K
    """
    assert primer.alphabet == ciphertext.alphabet
    MAX = len(ciphertext.alphabet)
    key = primer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] - key[j]) % MAX)
    return output


def ciphertext_autokey_minuend_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """
    Minuend primitive without any console output, C=K-P
    """
    assert primer.alphabet == plaintext.alphabet
    key: Sequence = primer.copy()
    output: Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        c = (key[j] - plaintext[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_minuend_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """
    Minuend primitive without any console output, P=K-C
    """
    assert primer.alphabet == ciphertext.alphabet
    key: Sequence = primer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        output.append((key[j] - ciphertext[j]) % MAX)
    return output


def ciphertext_autokey_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """
    Beafort primitive without any console output, C=P-K
    """
    assert primer.alphabet == plaintext.alphabet
    key: Sequence = primer.copy()
    output: Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """
    Beafort primitive without any console output, P=C+K
    """
    assert primer.alphabet == ciphertext.alphabet
    key: Sequence = primer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] + key[j]) % MAX)
    return output


"""
Combo autokey combines both the plaintext and ciphertext algorithms
"""


def combo_autokey_vigenere_encrypt(
    plaintext: Sequence, primer: Sequence, mode: int = 1
) -> Sequence:
    """
    Vigenere primitive without any console output, C=P+K
    """
    assert primer.alphabet == plaintext.alphabet
    plain_key: Sequence = primer + plaintext
    cipher_key: Sequence = primer
    output: Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        if mode == 1:
            c = (plaintext[j] + plain_key[j] + cipher_key[j]) % MAX
        elif mode == 2:
            c = (plaintext[j] + plain_key[j] - cipher_key[j]) % MAX
        elif mode == 3:
            c = (plaintext[j] - plain_key[j] + cipher_key[j]) % MAX
        elif mode == 4:
            c = (plaintext[j] - plain_key[j] - cipher_key[j]) % MAX
        elif mode == 5:
            c = (-plaintext[j] + plain_key[j] + cipher_key[j]) % MAX
        elif mode == 6:
            c = (-plaintext[j] + plain_key[j] - cipher_key[j]) % MAX
        elif mode == 7:
            c = (-plaintext[j] - plain_key[j] + cipher_key[j]) % MAX
        elif mode == 8:
            c = (-plaintext[j] - plain_key[j] - cipher_key[j]) % MAX
        else:
            raise Exception
        cipher_key.append(c)
        output.append(c)
    return output


def combo_autokey_vigenere_decrypt(
    ciphertext: Sequence, primer: Sequence, mode: int = 1
) -> Sequence:
    """
    Vigenere primitive without any console output, C=P+K
    """
    assert primer.alphabet == ciphertext.alphabet
    plain_key: Sequence = primer
    cipher_key: Sequence = primer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        # TODO encrypt and decrypt modes don't match
        if mode == 1:
            p = (ciphertext[j] + plain_key[j] + cipher_key[j]) % MAX
        elif mode == 2:
            p = (ciphertext[j] + plain_key[j] - cipher_key[j]) % MAX
        elif mode == 3:
            p = (ciphertext[j] - plain_key[j] + cipher_key[j]) % MAX
        elif mode == 4:
            p = (ciphertext[j] - plain_key[j] - cipher_key[j]) % MAX
        elif mode == 5:
            p = (-ciphertext[j] + plain_key[j] + cipher_key[j]) % MAX
        elif mode == 6:
            p = (-ciphertext[j] + plain_key[j] - cipher_key[j]) % MAX
        elif mode == 7:
            p = (-ciphertext[j] - plain_key[j] + cipher_key[j]) % MAX
        elif mode == 8:
            p = (-ciphertext[j] - plain_key[j] - cipher_key[j]) % MAX
        else:
            raise Exception
        plain_key.append(p)
        output.append(p)
    return output


# plaintext autokey variations
# we can do 3 operations, 2 subtractions and 1 addition, addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P


def plaintext_autokey_vigenere_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """
    Vigenere primitive without any console output, C=P+K
    """
    assert primer.alphabet == plaintext.alphabet
    key = primer + plaintext
    MAX = len(plaintext.alphabet)
    output = Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        c = (plaintext[j] + key[j]) % MAX
        output.append(c)
    return output


def plaintext_autokey_vigenere_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """
    Vigenere primitive without any console output, P=C-K
    """
    assert primer.alphabet == ciphertext.alphabet
    key: Sequence = primer.copy()
    MAX = len(ciphertext.alphabet)
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        c = (ciphertext[j] - key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_minuend_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """
    Minuend primitive without any console output, C=K-P
    """
    assert primer.alphabet == plaintext.alphabet
    key: Sequence = primer + plaintext
    output = Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        c = (key[j] - plaintext[j]) % MAX
        output.append(c)
    return output


def plaintext_autokey_minuend_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """
    Minuend primitive without any console output, P=K-C
    """
    assert primer.alphabet == ciphertext.alphabet
    key: Sequence = primer.copy()
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        c = (key[j] - ciphertext[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """
    Beafort primitive without any console output, C=P-K
    """
    assert primer.alphabet == plaintext.alphabet
    key: Sequence = primer + plaintext
    output = Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j]) % MAX
        output.append(c)
    return output


def plaintext_autokey_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """
    Beafort primitive without any console output, P=C+K
    """
    assert primer.alphabet == ciphertext.alphabet
    key: Sequence = primer.copy()
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        p = (key[j] + ciphertext[j]) % MAX
        output.append(p)
        key.append(p)
    return output


# Vigenere Autokey with custom alphabet


def plaintext_autokey_vigenere_encrypt_with_alphabet(
    plaintext: Sequence,
    primer: Sequence,
    # alphabet: list[int] = range(0, MAX + 1),
    trace: bool = False,
):
    """
    Plain Vigenere C=P+K
    """
    assert primer.alphabet == plaintext.alphabet
    output: list[int] = []
    tr: list[list[int]] = construct_tabula_recta(alphabet)

    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(plaintext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = alphabet.index(plaintext[i])
        c = tr[row_index][column_index]
        output.append(c)
        key.append(c)

    return output
