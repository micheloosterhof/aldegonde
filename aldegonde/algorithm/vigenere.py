from ..structures.alphabet import Alphabet
from ..structures.sequence import Sequence


def variant_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence, trace: bool = False
) -> Sequence:
    """
    Variant Beaufort C=P-K
    Note: this is the same as vigenere_decrypt() !!
    """
    output: Sequence = Sequence(alphabet=plaintext.alphabet)
    for i in range(0, len(plaintext)):
        output.append((plaintext[i] - primer[i % len(primer)]) % len(output.alphabet))
    return output


def variant_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence, trace: bool = False
) -> Sequence:
    """
    Plain Beaufort P=C+K
    Note: this is the same as vigenere_encrypt() !!
    """
    output: Sequence = Sequence(alphabet=ciphertext.alphabet)
    for i in range(0, len(ciphertext)):
        output.append((ciphertext[i] + primer[i % len(primer)]) % len(output.alphabet))
    return output


def beaufort_encrypt(
    plaintext: Sequence, primer: Sequence, trace: bool = False
) -> Sequence:
    """
    Plain Beaufort C=K-P
    Note: this is the same as beaufort_decrypt() !!
    """
    output: Sequence = Sequence(alphabet=plaintext.alphabet)
    for i in range(0, len(plaintext)):
        output.append((primer[i % len(primer)] - plaintext[i]) % len(output.alphabet))
    return output


def beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence, trace: bool = False
) -> Sequence:
    """
    Plain Beaufort P=K-P
    Note: this is the same as beaufort_encrypt() !!
    """
    output: Sequence = Sequence(alphabet=ciphertext.alphabet)
    for i in range(0, len(ciphertext)):
        output.append((primer[i % len(primer)] - ciphertext[i]) % len(output.alphabet))
    return output


def vigenere_encrypt(
    plaintext: Sequence, primer: Sequence, trace: bool = False
) -> Sequence:
    """
    Plain Vigenere C=P+K
    """
    output: Sequence = Sequence(alphabet=plaintext.alphabet)
    print(output)
    print(repr(output))
    for i in range(0, len(plaintext)):
        output.append((plaintext[i] + primer[i % len(primer)]) % len(output.alphabet))
    return output


def vigenere_decrypt(
    ciphertext: Sequence, primer: Sequence, trace: bool = False
) -> Sequence:
    """
    Plain Vigenere P=C-K
    """
    output: Sequence = Sequence(alphabet=ciphertext.alphabet)
    for i in range(0, len(ciphertext)):
        output.append((ciphertext[i] - primer[i % len(primer)]) % len(output.alphabet))
    return output


def construct_tabula_recta(alphabet: Alphabet, trace: bool = True):
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


def vigenere_encrypt_with_alphabet(
    plaintext: Sequence,
    primer: Sequence,
    alphabet: list[int],
    trace: bool = False,
) -> Sequence:
    """
    Plain Vigenere C=P+K
    """
    output: Sequence = Sequence()
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


def vigenere_decrypt_with_alphabet(
    ciphertext: Sequence,
    primer: Sequence,
    alphabet: list[int],
    trace: bool = False,
) -> Sequence:
    """
    Plain Vigenere C=P+K
    """
    output: Sequence = Sequence()
    if not alphabet:
        alphabet = list(range(0, len(ciphertext.alphabet) + 1))
    tr: list[list[int]] = construct_tabula_recta(alphabet)

    for i in range(0, len(ciphertext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = row.index(ciphertext[i])
        output.append(alphabet[column_index])

    return output


def combo_autokey_vigenere_encrypt(
    plaintext: Sequence, primer: Sequence, mode: int = 1
) -> Sequence:
    """
    Combo vigenere that combines plaintext + ciphertext
    """
    plain_key: Sequence = primer + plaintext
    cipher_key: Sequence = primer
    output: Sequence = Sequence(alphabet=plaintext.alphabet)
    for j in range(0, len(plaintext)):
        if mode == 1:
            c = (plaintext[j] + plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 2:
            c = (plaintext[j] + plain_key[j] - cipher_key[j]) % len(output.alphabet)
        elif mode == 3:
            c = (plaintext[j] - plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 4:
            c = (plaintext[j] - plain_key[j] - cipher_key[j]) % len(output.alphabet)
        elif mode == 5:
            c = (-plaintext[j] + plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 6:
            c = (-plaintext[j] + plain_key[j] - cipher_key[j]) % len(output.alphabet)
        elif mode == 7:
            c = (-plaintext[j] - plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 8:
            c = (-plaintext[j] - plain_key[j] - cipher_key[j]) % len(output.alphabet)
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
    plain_key: Sequence = primer
    cipher_key: Sequence = primer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    for j in range(0, len(ciphertext)):
        # TODO encrypt and decrypt modes don't match
        if mode == 1:
            p = (ciphertext[j] + plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 2:
            p = (ciphertext[j] + plain_key[j] - cipher_key[j]) % len(output.alphabet)
        elif mode == 3:
            p = (ciphertext[j] - plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 4:
            p = (ciphertext[j] - plain_key[j] - cipher_key[j]) % len(output.alphabet)
        elif mode == 5:
            p = (-ciphertext[j] + plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 6:
            p = (-ciphertext[j] + plain_key[j] - cipher_key[j]) % len(output.alphabet)
        elif mode == 7:
            p = (-ciphertext[j] - plain_key[j] + cipher_key[j]) % len(output.alphabet)
        elif mode == 8:
            p = (-ciphertext[j] - plain_key[j] - cipher_key[j]) % len(output.alphabet)
        else:
            raise Exception
        plain_key.append(p)
        output.append(p)
    return output
