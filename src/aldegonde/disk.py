"""disk cipher variations: Wheatstone Cryptograph, Wadsworth cipher
disk, Urkryptografen"""

from collections.abc import Generator, Iterable, Sequence

from aldegonde.exceptions import CipherError, InvalidInputError
from aldegonde.pasc import T
from aldegonde.validation import validate_alphabet, validate_text_sequence

"""
From: https://eprint.iacr.org/2020/1492.pdf

Generalized cipher clock

We can generalize the class of cipher clocks, in which the plaintext
alphabet has m characters, while the ciphertext alphabet has n
characters. We could also set the number of steps for the ciphertext
hand to be an integral multiple r of the number of steps taken by
the plaintext hand (for the obvious reason, r and n must be coprime);
however, this is equivalent to a reordering of the key, so without
loss of generality we set r = 1.  The nature of the cipher varies
according to the relationship between m and n. We can identify five
main categories of devices:

n = m: In this case, the cipher degenerates to a monoalphabetic
substitution. This case is not interesting to us, since its solution
is already available (Jakobsen 1995). Such a device would have only
one pointer (if any). Examples of single-handed cipher clocks are
the Hicks cipher disk (Brisson 2020), the Regensburg Verschlusselung
disk (Simpson 2020), and a disk used during the American Civil War.
There is even a two-handed disk (the relative position of the hands
is locked), patented by Lewis (1903).

n = m−1: The Wheatstone Cryptograph and Urkryptografen fall into
this category. It is impossible for two adjacent characters in the
ciphertext to be deciphered to two of the same letter in the
plaintext, so we must disguise all double letters before encryption.
While inconvenient, this is not an unreasonable complication. This
case has the weakness that when double letters appear in the
ciphertext, it indicates that the plaintext letters are adjacent
in the plaintext alphabet, since decrypting the second of two of
the same letter requires turning the hands n steps, so that the
plaintext hand then points one letter earlier on its ring (Friedman
1918).

n < m−1: When n is too small, we not only need to avoid double
letters, but there are additional constraints on the plaintext,
such as a proscription on alphabetically adjacent pairs. This renders
the cipher impractical, and this case should not be used by
cipher-clock designers.  We also do not test our attack with this
class of device.

n = m+1: In this case, double letters do not occur in the ciphertext
but are permitted in the plaintext.  All other digrams are possible
in the ciphertext. We are unaware of any historical devices in this
category.

n > m+1: The Wadsworth cipher disk is in this catergory. Here also,
double letters in the plaintext are not a worry, and we do not have
to disguise them as we did with the Wheatstone Cryptograph, but
double letters cannot occur in ciphertexts. However, there is a new
weakness: other digrams are also not allowed in the ciphertext.
When encrypting a letter, the hands of the device move at most m
steps, so that some letters on the ciphertext ring cannot be reached.
For a sufficiently long ciphertext (a few times m×n) we can use
this fact to reconstruct the mixed alphabet key, by tabulating the
digrams present and noting which are missing; the missing digrams
give us information about consecutive letters in the key. For shorter
ciphertexts, this weakness puts constraints on the key and can help
with a pen-andpaper attack. Our attack, as we see below, is effective
for ciphertexts as short as 250 characters.
"""


def disk_encrypt(
    plaintext: Iterable[T],
    plainabc: Sequence[T],
    cipherabc: Sequence[T],
) -> Generator[T, None, None]:
    """Disk Encryption using cipher disk algorithm.

    Args:
        plaintext: Text to encrypt
        plainabc: Plaintext alphabet
        cipherabc: Ciphertext alphabet

    Yields:
        Encrypted characters

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If encryption fails

    Algorithm:
    1. Calculate xi = (pi − I) modulo m
    2. If xi = 0, then set xi = m
    3. Add xi to I
    4. Output yi = I modulo n
    """
    plaintext_seq = (
        list(plaintext) if not isinstance(plaintext, Sequence) else plaintext
    )
    validate_text_sequence(plaintext_seq)
    validate_alphabet(plainabc)
    validate_alphabet(cipherabc)

    try:
        state: int = 0
        for e in plaintext_seq:
            if e not in plainabc:
                msg = f"Plaintext character '{e}' not found in plaintext alphabet"
                raise CipherError(msg, cipher_type="disk")

            x = (plainabc.index(e) - state) % len(plainabc)
            if x == 0:
                x = len(plainabc)
            state += x
            yield cipherabc[state % len(cipherabc)]

    except Exception as exc:
        if isinstance(exc, CipherError | InvalidInputError):
            raise
        msg = f"Disk encryption failed: {exc}"
        raise CipherError(msg, cipher_type="disk") from exc


def disk_decrypt(
    ciphertext: Iterable[T],
    plainabc: Sequence[T],
    cipherabc: Sequence[T],
) -> Generator[T, None, None]:
    """Disk Decryption using cipher disk algorithm.

    Args:
        ciphertext: Text to decrypt
        plainabc: Plaintext alphabet
        cipherabc: Ciphertext alphabet

    Yields:
        Decrypted characters

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If decryption fails
    """
    ciphertext_seq = (
        list(ciphertext) if not isinstance(ciphertext, Sequence) else ciphertext
    )
    validate_text_sequence(ciphertext_seq)
    validate_alphabet(plainabc)
    validate_alphabet(cipherabc)

    try:
        state: int = 0
        for e in ciphertext_seq:
            if e not in cipherabc:
                msg = f"Ciphertext character '{e}' not found in ciphertext alphabet"
                raise CipherError(msg, cipher_type="disk")

            y = (cipherabc.index(e) - state) % len(cipherabc)
            if y == 0:
                y = len(cipherabc)
            state += y
            yield plainabc[state % len(plainabc)]

    except Exception as exc:
        if isinstance(exc, CipherError | InvalidInputError):
            raise
        msg = f"Disk decryption failed: {exc}"
        raise CipherError(msg, cipher_type="disk") from exc
