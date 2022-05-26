def variant_beaufort_encrypt(
    plaintext: list[int], primer: list[int] = [0], trace: bool = False
):
    """
    Variant Beaufort C=P-K
    Note: this is the same as vigenere_decrypt() !!
    """
    output: list[int] = []
    for i in range(0, len(plaintext)):
        output.append((plaintext[i] - primer[i % len(primer)]) % MAX)
    return output


def variant_beaufort_decrypt(
    ciphertext: list[int], primer: list[int] = [0], trace: bool = False
):
    """
    Plain Beaufort P=C+K
    Note: this is the same as vigenere_encrypt() !!
    """
    output: list[int] = []
    for i in range(0, len(ciphertext)):
        output.append((ciphertext[i] + primer[i % len(primer)]) % MAX)
    return output


def beaufort_encrypt(
    plaintext: list[int], primer: list[int] = [0], trace: bool = False
):
    """
    Plain Beaufort C=K-P
    Note: this is the same as beaufort_decrypt() !!
    """
    output: list[int] = []
    for i in range(0, len(plaintext)):
        output.append((primer[i % len(primer)] - plaintext[i]) % MAX)
    return output


def beaufort_decrypt(
    ciphertext: list[int], primer: list[int] = [0], trace: bool = False
):
    """
    Plain Beaufort P=K-P
    Note: this is the same as beaufort_encrypt() !!
    """
    output: list[int] = []
    for i in range(0, len(ciphertext)):
        output.append((primer[i % len(primer)] - ciphertext[i]) % MAX)
    return output


def vigenere_decrypt(
    ciphertext: list[int], primer: list[int] = [0], trace: bool = False
):
    """
    Plain Vigenere P=C-K
    """
    output: list[int] = []
    for i in range(0, len(ciphertext)):
        output.append((ciphertext[i] - primer[i % len(primer)]) % MAX)
    return output


def vigenere_encrypt(
    plaintext: list[int], primer: list[int] = [0], trace: bool = False
):
    """
    Plain Vigenere C=P+K
    """
    output: list[int] = []
    for i in range(0, len(plaintext)):
        output.append((plaintext[i] + primer[i % len(primer)]) % MAX)
    return output


def construct_tabula_recta(
    alphabet: list[int] = list(range(0, MAX)), trace: bool = True
):
    """
    construct a tabula recta based on custom alphabet.
    output is a MAX*MAX matrix
    """
    output: list[list[int]] = []
    for shift in range(0, MAX):
        output.append(alphabet[shift:] + alphabet[:shift])
    if trace:
        print(repr(output))
    return output


def vigenere_encrypt_with_alphabet(
    plaintext: list[int],
    primer: list[int] = [0],
    alphabet: list[int] = range(0, MAX + 1),
    trace: bool = False,
):
    """
    Plain Vigenere C=P+K
    """
    output: list[int] = []
    tr: list[list[int]] = construct_tabula_recta(alphabet)

    for i in range(0, len(plaintext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = alphabet.index(plaintext[i])
        output.append(tr[row_index][column_index])

    return output


def vigenere_decrypt_with_alphabet(
    ciphertext: list[int],
    primer: list[int] = [0],
    alphabet: list[int] = range(0, MAX + 1),
    trace: bool = False,
):
    """
    Plain Vigenere C=P+K
    """
    output: list[int] = []
    tr: list[list[int]] = construct_tabula_recta(alphabet)

    for i in range(0, len(ciphertext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = row.index(ciphertext[i])
        output.append(alphabet[column_index])

    return output


def combo_autokey_vigenere_encrypt(
    plaintext: list[int], primer: list[int] = [0], mode: int = 1
) -> list[int]:
    """
    Combo vigenere that combines plaintext + ciphertext
    """
    plain_key: list[int] = primer + plaintext
    cipher_key: list[int] = primer
    output: list[int] = []
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
    ciphertext: list[int], primer: list[int] = [0], mode: int = 1
) -> list[int]:
    """
    Vigenere primitive without any console output, C=P+K
    """
    plain_key: list[int] = primer
    cipher_key: list[int] = primer + ciphertext
    output: list[int] = []
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
