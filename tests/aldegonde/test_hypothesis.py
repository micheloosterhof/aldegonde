"""Property-based tests using Hypothesis."""

from hypothesis import given, settings
from hypothesis import strategies as st

from aldegonde import masc, pasc

# Standard English alphabet for testing
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@given(st.text(alphabet=ABC, min_size=1, max_size=100))
@settings(max_examples=100)
def test_caesar_roundtrip(plaintext: str) -> None:
    """Test that Caesar cipher encryption and decryption are inverse operations."""
    for shift in [1, 3, 13, 25]:
        key = masc.shiftedkey(ABC, shift=shift)
        ciphertext = list(masc.masc_encrypt(plaintext, key=key))
        decrypted = list(masc.masc_decrypt(ciphertext, key=key))
        assert list(plaintext) == decrypted


@given(st.text(alphabet=ABC, min_size=1, max_size=100))
@settings(max_examples=100)
def test_atbash_roundtrip(plaintext: str) -> None:
    """Test that Atbash cipher is its own inverse."""
    key = masc.atbashkey(ABC)
    ciphertext = list(masc.masc_encrypt(plaintext, key=key))
    decrypted = list(masc.masc_decrypt(ciphertext, key=key))
    assert list(plaintext) == decrypted


@given(st.text(alphabet=ABC, min_size=1, max_size=100))
@settings(max_examples=100)
def test_random_masc_roundtrip(plaintext: str) -> None:
    """Test that random monoalphabetic substitution encrypts and decrypts correctly."""
    key = masc.randomkey(ABC)
    ciphertext = list(masc.masc_encrypt(plaintext, key=key))
    decrypted = list(masc.masc_decrypt(ciphertext, key=key))
    assert list(plaintext) == decrypted


@given(
    st.text(alphabet=ABC, min_size=1, max_size=100),
    st.text(alphabet=ABC, min_size=1, max_size=10),
)
@settings(max_examples=100)
def test_vigenere_roundtrip(plaintext: str, keyword: str) -> None:
    """Test that Vigenere cipher encryption and decryption are inverse operations."""
    if not keyword:  # Hypothesis may generate empty string despite min_size
        return
    tr = pasc.vigenere_tr(ABC)
    ciphertext = list(pasc.pasc_encrypt(plaintext, keyword=keyword, tr=tr))
    decrypted = list(pasc.pasc_decrypt(ciphertext, keyword=keyword, tr=tr))
    assert list(plaintext) == decrypted


@given(
    st.text(alphabet=ABC, min_size=1, max_size=100),
    st.text(alphabet=ABC, min_size=1, max_size=10),
)
@settings(max_examples=100)
def test_beaufort_roundtrip(plaintext: str, keyword: str) -> None:
    """Test that Beaufort cipher encryption and decryption are inverse operations."""
    if not keyword:
        return
    tr = pasc.beaufort_tr(ABC)
    ciphertext = list(pasc.pasc_encrypt(plaintext, keyword=keyword, tr=tr))
    decrypted = list(pasc.pasc_decrypt(ciphertext, keyword=keyword, tr=tr))
    assert list(plaintext) == decrypted


@given(st.text(alphabet=ABC, min_size=1, max_size=100))
@settings(max_examples=50)
def test_masc_encrypt_preserves_length(plaintext: str) -> None:
    """Test that monoalphabetic substitution preserves text length."""
    key = masc.randomkey(ABC)
    ciphertext = list(masc.masc_encrypt(plaintext, key=key))
    assert len(ciphertext) == len(plaintext)


@given(
    st.text(alphabet=ABC, min_size=1, max_size=100),
    st.text(alphabet=ABC, min_size=1, max_size=10),
)
@settings(max_examples=50)
def test_pasc_encrypt_preserves_length(plaintext: str, keyword: str) -> None:
    """Test that polyalphabetic substitution preserves text length."""
    if not keyword:
        return
    tr = pasc.vigenere_tr(ABC)
    ciphertext = list(pasc.pasc_encrypt(plaintext, keyword=keyword, tr=tr))
    assert len(ciphertext) == len(plaintext)


@given(st.integers(min_value=0, max_value=25))
def test_shifted_key_periodicity(shift: int) -> None:
    """Test that shifted key with shift N is same as shift N+26."""
    key1 = masc.shiftedkey(ABC, shift=shift)
    key2 = masc.shiftedkey(ABC, shift=shift + 26)
    assert key1 == key2


@given(st.integers(min_value=1, max_value=25))
def test_shifted_key_inverse(shift: int) -> None:
    """Test that shift N and shift -N are inverses."""
    key_forward = masc.shiftedkey(ABC, shift=shift)
    key_backward = masc.shiftedkey(ABC, shift=-shift)
    # Composing forward and backward should give identity
    for c in ABC:
        assert key_backward[key_forward[c]] == c
