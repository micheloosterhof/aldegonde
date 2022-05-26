# ciphertext autokey variations
# we can do 3 operations, 2 subtractions and 1 addition, addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P


def ciphertext_autokey_vigenere_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Vigenere primitive without any console output, C=P+K
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] + key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_vigenere_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Vigenere primitive without any console output, P=C-K
    """
    key: list[int] = primer + ciphertext
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] - key[j]) % MAX)
    return output


def ciphertext_autokey_minuend_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Minuend primitive without any console output, C=K-P
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (key[j] - plaintext[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_minuend_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Minuend primitive without any console output, P=K-C
    """
    key: list[int] = primer + ciphertext
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        output.append((key[j] - ciphertext[j]) % MAX)
    return output


def ciphertext_autokey_beaufort_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Beafort primitive without any console output, C=P-K
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_beaufort_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Beafort primitive without any console output, P=C+K
    """
    key: list[int] = primer + ciphertext
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] + key[j]) % MAX)
    return output


# plaintext autokey variations
# we can do 3 operations, 2 subtractions and 1 addition, addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P


def combo_autokey_vigenere_encrypt(
    plaintext: list[int], primer: list[int] = [0], mode: int = 1
) -> list[int]:
    """
    Vigenere primitive without any console output, C=P+K
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


def plaintext_autokey_vigenere_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Vigenere primitive without any console output, C=P+K
    """
    key: list[int] = primer + plaintext
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] + key[j]) % MAX
        output.append(c)
    return output


def plaintext_autokey_vigenere_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Vigenere primitive without any console output, P=C-K
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        c = (ciphertext[j] - key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_minuend_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Minuend primitive without any console output, C=K-P
    """
    key: list[int] = primer + plaintext
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (key[j] - plaintext[j]) % MAX
        output.append(c)
    return output


def plaintext_autokey_minuend_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Minuend primitive without any console output, P=K-C
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        c = (key[j] - ciphertext[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_beaufort_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Beafort primitive without any console output, C=P-K
    """
    key: list[int] = primer + plaintext
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j]) % MAX
        output.append(c)
    return output


def plaintext_autokey_beaufort_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    Beafort primitive without any console output, P=C+K
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        p = (key[j] + ciphertext[j]) % MAX
        output.append(p)
        key.append(p)
    return output
