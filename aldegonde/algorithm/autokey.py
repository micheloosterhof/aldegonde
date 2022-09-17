"""
ciphertext autokey variations
"""

from typing import Callable

from ..structures.sequence import Sequence


def ciphertext_autokey_encrypt(
    plaintext: Sequence, primer: Sequence, encryptf: Callable[[int, int], int]
) -> Sequence:
    """
    Ciphertext Autokey Encryption primitive C[i] = EF(P[i], C[i-1])
    """
    assert primer.alphabet == plaintext.alphabet
    key: Sequence = primer.copy()
    output = Sequence(alphabet=plaintext.alphabet)
    MAX = len(plaintext.alphabet)
    for i, e in enumerate(plaintext):
        c = encryptf(e, key[i]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_decrypt(
    ciphertext: Sequence, primer: Sequence, decryptf: Callable[[int, int], int]
) -> Sequence:
    """
    Ciphertext Autokey Decryption primitive C[i] = DF(P[i], C[i-1])
    """
    assert primer.alphabet == ciphertext.alphabet
    MAX = len(ciphertext.alphabet)
    key = primer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    for i, e in enumerate(ciphertext):
        output.append(decryptf(e, key[i]) % MAX)
    return output


# we can do 3 operations, 2 subtractions and 1 addition
# addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P


def vigenere_encrypt(plain: int, key: int) -> int:
    """ """
    return plain + key


def vigenere_decrypt(cipher: int, key: int) -> int:
    """ """
    return cipher - key


def beaufort_encrypt(plain: int, key: int) -> int:
    """ """
    return key - plain


def beaufort_decrypt(cipher: int, key: int) -> int:
    """ """
    return key - cipher


def variant_beaufort_encrypt(plain: int, key: int) -> int:
    """ """
    return plain - key


def variant_beaufort_decrypt(cipher: int, key: int) -> int:
    """ """
    return cipher + key


# Utility Functions


def ciphertext_autokey_vigenere_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return ciphertext_autokey_encrypt(plaintext, primer, vigenere_encrypt)


def ciphertext_autokey_vigenere_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return ciphertext_autokey_decrypt(ciphertext, primer, vigenere_decrypt)


def ciphertext_autokey_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return ciphertext_autokey_encrypt(plaintext, primer, beaufort_encrypt)


def ciphertext_autokey_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return ciphertext_autokey_decrypt(ciphertext, primer, beaufort_decrypt)


def ciphertext_autokey_variant_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return ciphertext_autokey_encrypt(plaintext, primer, variant_beaufort_encrypt)


def ciphertext_autokey_variant_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return ciphertext_autokey_decrypt(ciphertext, primer, variant_beaufort_decrypt)


def plaintext_autokey_encrypt(
    plaintext: Sequence, primer: Sequence, encryptf: Callable[[int, int], int]
) -> Sequence:
    """
    Plaintext Autokey Encryption primitive C[i] = EF(P[i], P[i-1])
    """
    assert primer.alphabet == plaintext.alphabet
    key = primer + plaintext
    MAX = len(plaintext.alphabet)
    output = Sequence(alphabet=plaintext.alphabet)
    for i, e in enumerate(plaintext):
        c = encryptf(e, key[i]) % MAX
        output.append(c)
    return output


def plaintext_autokey_decrypt(
    ciphertext: Sequence, primer: Sequence, decryptf: Callable[[int, int], int]
) -> Sequence:
    """
    Plaintext Autokey Decryption primitive P[i] = DF(C[i], P[i-1])
    """
    assert primer.alphabet == ciphertext.alphabet
    key: Sequence = primer.copy()
    MAX = len(ciphertext.alphabet)
    output = Sequence(alphabet=ciphertext.alphabet)
    for i, e in enumerate(ciphertext):
        c = decryptf(e, key[i]) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_vigenere_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return plaintext_autokey_encrypt(plaintext, primer, vigenere_encrypt)


def plaintext_autokey_vigenere_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return plaintext_autokey_decrypt(ciphertext, primer, vigenere_decrypt)


def plaintext_autokey_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return plaintext_autokey_encrypt(plaintext, primer, beaufort_encrypt)


def plaintext_autokey_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return plaintext_autokey_decrypt(ciphertext, primer, beaufort_decrypt)


def plaintext_autokey_variant_beaufort_encrypt(
    plaintext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return plaintext_autokey_encrypt(plaintext, primer, variant_beaufort_encrypt)


def plaintext_autokey_variant_beaufort_decrypt(
    ciphertext: Sequence, primer: Sequence
) -> Sequence:
    """ """
    return plaintext_autokey_decrypt(ciphertext, primer, variant_beaufort_decrypt)


def plaintext_autokey_vigenere_encrypt_with_alphabet(
    plaintext: Sequence,
    primer: Sequence,
    alphabet: list[int],
    trace: bool = False,
) -> Sequence:
    """ """
    assert primer.alphabet == plaintext.alphabet
    key = primer + plaintext
    MAX = len(plaintext.alphabet)
    output: Sequence = Sequence()

    if not alphabet:
        alphabet = list(range(0, MAX + 1))
    tr: list[list[int]] = construct_tabula_recta(alphabet)
    abc = list(alphabet)

    for i, e in enumerate(plaintext):
        row_index = abc.index(key[i])
        row = tr[row_index]
        column_index = abc.index(e)
        output.append(tr[row_index][column_index])

    return output


def plaintext_autokey_vigenere_encrypt_with_alphabet(
    plaintext: Sequence,
    primer: Sequence,
    # alphabet: list[int] = range(0, MAX + 1),
    trace: bool = False,
) -> Sequence:
    """
    Vigenere Autokey with custom alphabet
    """
    assert primer.alphabet == plaintext.alphabet
    output = Sequence(alphabet=plaintext.alphabet)
    tr: list[list[int]] = construct_tabula_recta(alphabet)

    key: list[int] = primer.copy()
    for j in range(0, len(plaintext)):
        row_index = alphabet.index(primer[i % len(primer)])
        row = tr[row_index]
        column_index = alphabet.index(plaintext[j])
        c = tr[row_index][column_index]
        output.append(c)
        key.append(c)

    return output


def detect_plaintext_autokey(
    ciphertext: list[int],
    minkeysize: int = 1,
    maxkeysize: int = 20,
    trace: bool = False,
) -> None:
    """
    the way Caesar generalizes to Vigenere,
    a single-letter autokey generalizes to a multi-letter autokey
    to solve it, split it into multiple slices.
    """
    if trace is True:
        print(f"test for plaintext autokey, samplesize={len(ciphertext)}")
        print("#######################################################\n")

    for keysize in range(minkeysize, maxkeysize + 1):
        slices = {}
        vigiocs: float = 0
        miniocs: float = 0
        beaiocs: float = 0
        for start in range(0, keysize):
            slices[start] = ciphertext[start::keysize]
            if trace is True:
                print(f"\nslice={start}: ", end="")
            # Bruteforce Vigenere introductory key at this position
            for key in range(0, MAX):
                plain = plaintext_autokey_vigenere_decrypt(slices[start], [key])
                vigiocs += normalized_ioc(plain)
                if normalized_ioc(plain) > 1.3:
                    if trace is True:
                        print(f"vigenere ioc={normalized_ioc(plain):.2f} ", end="")
            # Bruteforce Beaufort introductory key at this position
            for key in range(0, MAX):
                plain = plaintext_autokey_beaufort_decrypt(slices[start], [key])
                beaiocs += normalized_ioc(plain)
                if normalized_ioc(plain) > 1.3:
                    if trace is True:
                        print(f"beaufort ioc={normalized_ioc(plain):.2f} ", end="")
            # Bruteforce Minuend introductory key at this position
            for key in range(0, MAX):
                plain = plaintext_autokey_beaufort_decrypt(slices[start], [key])
                miniocs += normalized_ioc(plain)
                if normalized_ioc(plain) > 1.3:
                    if trace is True:
                        print(f"minuend ioc={normalized_ioc(plain):.2f} ", end="")
        vigiocavg = vigiocs / MAX / keysize
        miniocavg = miniocs / MAX / keysize
        beaiocavg = beaiocs / MAX / keysize
        if trace is True:
            print(f"\nvigenere keysize={keysize} avgioc = {vigiocavg:0.3f}")
            print(f"\nbeaufort keysize={keysize} avgioc = {beaiocavg:0.3f}")
            print(f"\nminuend  keysize={keysize} avgioc = {miniocavg:0.3f}")
        if vigiocavg > 1.2 or miniocavg > 1.2 or beaiocavg > 1.2:
            print("Attempting bruteforce...")
            if keysize < 4:
                bruteforce_autokey(
                    ciphertext,
                    minkeylength=keysize,
                    maxkeylength=keysize,
                    iocthreshold=1.3,
                )


def detect_ciphertext_autokey_vigenere(
    ciphertext: list[int],
    minkeysize: int = 1,
    maxkeysize: int = 10,
    trace: bool = False,
) -> None:
    """
    the way Caesar generalizes to Vigenere,
    a single-letter autokey generalizes to a multi-letter autokey
    to solve it, split it into multiple segments

    split by previous letter and create MAX alphabets. run bigram/ioc on these
    """
    if trace is True:
        print(f"test for ciphertext autokey, samplesize={len(ciphertext)}")
        print("#######################################################\n")

    # length of autokey introductory key
    for a in range(minkeysize, maxkeysize + 1):
        if trace is True:
            print(f"Checking key size {a}")

        alphabet: dict[int, list[int]] = {}
        for i in range(0, MAX):
            alphabet[i] = []

        for i in range(0, len(ciphertext) - a - 1):
            alphabet[ciphertext[i]].append(ciphertext[i + a])

        tot = 0.0
        for k, v in alphabet.items():
            tot += normalized_ioc(v)
            if trace is True:
                print(f"IOC: key={k} {normalized_ioc(v):.3f}")
            # dist(v)
            # bigram_diagram(v)
        print(f"key={a} avgioc={tot/MAX:.3f}")


"""
Combo autokey combines both the plaintext and ciphertext algorithms
"""


def combo_autokey_vigenere_encrypt(
    plaintext: Sequence, plainprimer: Sequence, cipherprimer: Sequence, mode: int = 1
) -> Sequence:
    """
    Vigenere primitive without any console output, C=P+K
    """
    assert cipherprimer.alphabet == plaintext.alphabet
    assert plainprimer.alphabet == plaintext.alphabet
    plain_key: Sequence = plainprimer + plaintext
    cipher_key: Sequence = cipherprimer
    output = Sequence(alphabet=plaintext.alphabet)
    MAX = len(plaintext.alphabet)
    for i, e in enumerate(plaintext):
        if mode == 1:
            c = (e + plain_key[i] + cipher_key[i]) % MAX
        elif mode == 2:
            c = (e + plain_key[i] - cipher_key[i]) % MAX
        elif mode == 3:
            c = (e - plain_key[i] + cipher_key[i]) % MAX
        elif mode == 4:
            c = (e - plain_key[i] - cipher_key[i]) % MAX
        elif mode == 5:
            c = (-e + plain_key[i] + cipher_key[i]) % MAX
        elif mode == 6:
            c = (-e + plain_key[i] - cipher_key[i]) % MAX
        elif mode == 7:
            c = (-e - plain_key[i] + cipher_key[i]) % MAX
        elif mode == 8:
            c = (-e - plain_key[i] - cipher_key[i]) % MAX
        else:
            raise Exception
        cipher_key.append(c)
        output.append(c)
    return output


def combo_autokey_vigenere_decrypt(
    ciphertext: Sequence, plainprimer: Sequence, cipherprimer: Sequence, mode: int = 1
) -> Sequence:
    """
    Vigenere primitive without any console output, C=P+K
    """
    assert plainprimer.alphabet == ciphertext.alphabet
    assert cipherprimer.alphabet == ciphertext.alphabet
    plain_key: Sequence = plainprimer
    cipher_key: Sequence = cipherprimer + ciphertext
    output = Sequence(alphabet=ciphertext.alphabet)
    MAX = len(ciphertext.alphabet)
    for i, e in enumerate(ciphertext):
        if mode == 1:
            p = (e - plain_key[i] - cipher_key[i]) % MAX
        elif mode == 2:
            p = (e - plain_key[i] + cipher_key[i]) % MAX
        elif mode == 3:
            p = (e + plain_key[i] - cipher_key[i]) % MAX
        elif mode == 4:
            p = (e + plain_key[i] + cipher_key[i]) % MAX
        elif mode == 5:
            p = (-e + plain_key[i] + cipher_key[i]) % MAX
        elif mode == 6:
            p = (-e + plain_key[i] - cipher_key[i]) % MAX
        elif mode == 7:
            p = (-e - plain_key[i] + cipher_key[i]) % MAX
        elif mode == 8:
            p = (-e - plain_key[i] - cipher_key[i]) % MAX
        else:
            raise Exception
        plain_key.append(p)
        output.append(p)
    return output


# assume 1 letter cipher autokey
# split by next letter and create MAX alphabets. run bigram on these
def run_test2a(ciphertext):

    for a in range(1, 20):
        alphabet = {}
        for i in range(0, MAX):
            alphabet[i] = []

        for i in range(0 + a, len(ciphertext)):
            alphabet[ciphertext[i]].append(ciphertext[i - a])

        tot = 0
        for i in alphabet.keys():
            tot += normalized_ioc(alphabet[i])
            # bigram_diagram(alphabet[i])
            # print("key={}: ioc of runes before {} = {}".format(a, i, ioc(alphabet[i])))
        print(f"key={a} avgioc={tot/MAX:.3f}")
