from typing import List


def variant_beaufort_encrypt(
    plaintext: List[int], primer: List[int] = [0], trace: bool = False
):
    """
    Variant Beaufort C=P-K
    Note: this is the same as vigenere_decrypt() !!
    """
    output: List[int] = []
    for i in range(0, len(plaintext)):
        output.append((plaintext[i] - primer[i % len(primer)]) % MAX)
    return output


def variant_beaufort_decrypt(
    ciphertext: List[int], primer: List[int] = [0], trace: bool = False
):
    """
    Plain Beaufort P=C+K
    Note: this is the same as vigenere_encrypt() !!
    """
    output: List[int] = []
    for i in range(0, len(ciphertext)):
        output.append((ciphertext[i] + primer[i % len(primer)]) % MAX)
    return output


def beaufort_encrypt(
    plaintext: List[int], primer: List[int] = [0], trace: bool = False
):
    """
    Plain Beaufort C=K-P
    Note: this is the same as beaufort_decrypt() !!
    """
    output: List[int] = []
    for i in range(0, len(plaintext)):
        output.append((primer[i % len(primer)] - plaintext[i]) % MAX)
    return output


def beaufort_decrypt(
    ciphertext: List[int], primer: List[int] = [0], trace: bool = False
):
    """
    Plain Beaufort P=K-P
    Note: this is the same as beaufort_encrypt() !!
    """
    output: List[int] = []
    for i in range(0, len(ciphertext)):
        output.append((primer[i % len(primer)] - ciphertext[i]) % MAX)
    return output


def vigenere_decrypt(
    ciphertext: List[int], primer: List[int] = [0], trace: bool = False
):
    """
    Plain Vigenere P=C-K
    """
    output: List[int] = []
    for i in range(0, len(ciphertext)):
        output.append((ciphertext[i] - primer[i % len(primer)]) % MAX)
    return output


def vigenere_encrypt(
    plaintext: List[int], primer: List[int] = [0], trace: bool = False
):
    """
    Plain Vigenere C=P+K
    """
    output: List[int] = []
    for i in range(0, len(plaintext)):
        output.append((plaintext[i] + primer[i % len(primer)]) % MAX)
    return output


def construct_tabula_recta(
    alphabet: List[int] = list(range(0, MAX)), trace: bool = True
):
    """
    construct a tabula recta based on custom alphabet.
    output is a MAX*MAX matrix
    """
    output: List[List[int]] = []
    for shift in range(0, MAX):
        output.append(alphabet[shift:] + alphabet[:shift])
    if trace:
        print(repr(output))
    return output


def vigenere_encrypt_with_alphabet(
    plaintext: List[int],
    primer: List[int] = [0],
    alphabet: List[int] = range(0, MAX + 1),
    trace: bool = False,
):
    """
    Plain Vigenere C=P+K
    """
    output: List[int] = []
    tr: List[List[int]] = construct_tabula_recta(alphabet)

    for i in range(0, len(plaintext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = alphabet.index(plaintext[i])
        output.append(tr[row_index][column_index])

    return output


def vigenere_decrypt_with_alphabet(
    ciphertext: List[int],
    primer: List[int] = [0],
    alphabet: List[int] = range(0, MAX + 1),
    trace: bool = False,
):
    """
    Plain Vigenere C=P+K
    """
    output: List[int] = []
    tr: List[List[int]] = construct_tabula_recta(alphabet)

    for i in range(0, len(ciphertext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = row.index(ciphertext[i])
        output.append(alphabet[column_index])

    return output

def combo_autokey_vigenere_encrypt(
    plaintext: List[int], primer: List[int] = [0], mode: int = 1
) -> List[int]:
    """
    Combo vigenere that combines plaintext + ciphertext
    """
    plain_key: List[int] = primer + plaintext
    cipher_key: List[int] = primer
    output: List[int] = []
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
    ciphertext: List[int], primer: List[int] = [0], mode: int = 1
) -> List[int]:
    """
    Vigenere primitive without any console output, C=P+K
    """
    plain_key: List[int] = primer
    cipher_key: List[int] = primer + ciphertext
    output: List[int] = []
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
