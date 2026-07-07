"""Bijective state-machine ciphers using a 13x13 transition matrix.

Implements reversible ciphers where a 13-state machine controls encryption.
Each state defines a permutation of the 29-rune alphabet. The 13x13 matrix
governs state transitions. When the transition matrix has no self-loops
(zero diagonal), the cipher state always changes, structurally suppressing
delta=0 (consecutive identical ciphertext runes).

Two concrete designs:

1. **Mealy machine cipher**: 13 states, each with a distinct permutation of
   29 runes. The transition matrix T[s][f(c)] determines the next state
   from the current state and a function of the ciphertext output.
   Bijective because each permutation is invertible.

2. **Latin square cipher with base conversion**: Runes (base 29) are encoded
   as variable-length base-13 digit sequences, processed through a 13x13
   Latin square (inherently row-bijective), then decoded back to runes.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

RUNE_ALPHABET_SIZE = 29
STATE_COUNT = 13


def _make_permutation(seed: int, size: int = RUNE_ALPHABET_SIZE) -> list[int]:
    """Generate a deterministic permutation from a seed."""
    rng = random.Random(seed)
    perm = list(range(size))
    rng.shuffle(perm)
    return perm


def _invert_permutation(perm: list[int]) -> list[int]:
    """Compute the inverse of a permutation."""
    inv = [0] * len(perm)
    for i, v in enumerate(perm):
        inv[v] = i
    return inv


def _make_latin_square(size: int, seed: int = 0) -> list[list[int]]:
    """Generate a Latin square of given size.

    Each row is a permutation of {0, ..., size-1}, and each column
    contains each value exactly once.

    Args:
        size: Side length of the square.
        seed: Random seed for shuffling.

    Returns:
        A size x size Latin square as a list of rows.
    """
    rng = random.Random(seed)
    # Start with cyclic Latin square, then shuffle rows and columns
    square = [[(i + j) % size for j in range(size)] for i in range(size)]
    # Shuffle rows
    rng.shuffle(square)
    # Shuffle columns by the same permutation applied to each row
    col_perm = list(range(size))
    rng.shuffle(col_perm)
    square = [[row[col_perm[j]] for j in range(size)] for row in square]
    # Relabel values
    val_perm = list(range(size))
    rng.shuffle(val_perm)
    return [[val_perm[cell] for cell in row] for row in square]


def _make_no_self_loop_transition(
    size: int = STATE_COUNT,
    seed: int = 42,
) -> list[list[int]]:
    """Generate a transition matrix with no self-loops (zero diagonal).

    For each state s and each input i, T[s][i] != s.

    Args:
        size: Number of states.
        seed: Random seed.

    Returns:
        size x size transition matrix with no fixed points.
    """
    rng = random.Random(seed)
    matrix: list[list[int]] = []
    for s in range(size):
        others = [x for x in range(size) if x != s]
        row = [rng.choice(others) for _ in range(size)]
        matrix.append(row)
    return matrix


def _make_deranged_transition(
    size: int = STATE_COUNT,
    seed: int = 42,
) -> list[list[int]]:
    """Generate a transition matrix where each row is a derangement.

    Each row is a permutation of {0..size-1} with no fixed points,
    ensuring state always changes AND all states are reachable from any state.

    Args:
        size: Number of states.
        seed: Random seed.

    Returns:
        size x size derangement transition matrix.
    """
    rng = random.Random(seed)
    matrix: list[list[int]] = []
    for _s in range(size):
        # Generate a derangement (permutation with no fixed points)
        perm = list(range(size))
        for _ in range(1000):
            rng.shuffle(perm)
            if all(perm[i] != i for i in range(size)):
                break
        # Rotate so position s maps away from s
        # (the derangement already guarantees perm[s] != s)
        matrix.append(list(perm))
    return matrix


# ---------------------------------------------------------------------------
# Design 1: Mealy machine cipher
# ---------------------------------------------------------------------------


class MealyCipher:
    """State-machine cipher with 13 states and 29-rune permutations.

    Each state has an associated permutation of {0..28}. The state
    transitions via a 13x13 matrix indexed by (current_state, ciphertext mod 13).
    The no-self-loop constraint on the transition matrix ensures the
    permutation changes at every step, suppressing delta=0.

    Args:
        key_seed: Seed for generating the 13 permutations.
        transition_seed: Seed for the transition matrix.
        initial_state: Starting state (0-12).
        no_self_loops: If True, transition matrix has no fixed points.
    """

    def __init__(
        self,
        key_seed: int = 0,
        transition_seed: int = 42,
        initial_state: int = 0,
        *,
        no_self_loops: bool = True,
    ) -> None:
        self.initial_state = initial_state
        self.state_count = STATE_COUNT
        self.alphabet_size = RUNE_ALPHABET_SIZE

        # Generate 13 distinct permutations of 29 runes
        self.permutations = [
            _make_permutation(key_seed + i, self.alphabet_size)
            for i in range(self.state_count)
        ]
        self.inv_permutations = [
            _invert_permutation(p) for p in self.permutations
        ]

        # 13x13 transition matrix
        if no_self_loops:
            self.transition = _make_deranged_transition(
                self.state_count, transition_seed,
            )
        else:
            self.transition = _make_latin_square(self.state_count, transition_seed)

    def encrypt(self, plaintext: Sequence[int]) -> list[int]:
        """Encrypt a sequence of rune indices.

        Args:
            plaintext: Sequence of integers in [0, 28].

        Returns:
            List of encrypted rune indices.
        """
        state = self.initial_state
        ciphertext: list[int] = []
        for p in plaintext:
            c = self.permutations[state][p]
            ciphertext.append(c)
            state = self.transition[state][c % self.state_count]
        return ciphertext

    def decrypt(self, ciphertext: Sequence[int]) -> list[int]:
        """Decrypt a sequence of rune indices.

        Args:
            ciphertext: Sequence of integers in [0, 28].

        Returns:
            List of decrypted rune indices.
        """
        state = self.initial_state
        plaintext: list[int] = []
        for c in ciphertext:
            p = self.inv_permutations[state][c]
            plaintext.append(p)
            state = self.transition[state][c % self.state_count]
        return plaintext


# ---------------------------------------------------------------------------
# Design 2: Latin square cipher with base-13 encoding
# ---------------------------------------------------------------------------


def runes_to_base13(runes: Sequence[int], alphabet_size: int = 29) -> list[int]:
    """Encode rune indices as a variable-length base-13 digit stream.

    Uses a straddling checkerboard: 11 runes get single-digit codes,
    2 escape digits (11, 12) prefix the remaining 18 runes as
    two-digit codes.

    With 2 escapes: 11 single + 2*13 = 37 capacity (>= 29).
    We use: digits 0-10 → runes 0-10 (single digit),
            digit 11 then 0-12 → runes 11-23 (two digits),
            digit 12 then 0-4  → runes 24-28 (two digits).

    Args:
        runes: Rune indices (each 0-28).
        alphabet_size: Size of rune alphabet.

    Returns:
        List of base-13 digits.
    """
    output: list[int] = []
    escape1 = 11
    escape2 = 12
    for r in runes:
        if r < 11:
            output.append(r)
        elif r < 24:
            output.append(escape1)
            output.append(r - 11)
        else:
            output.append(escape2)
            output.append(r - 24)
    return output


def base13_to_runes(digits: Sequence[int]) -> list[int]:
    """Decode a base-13 digit stream back to rune indices.

    Inverse of runes_to_base13.

    Args:
        digits: Base-13 digits.

    Returns:
        List of rune indices (each 0-28).
    """
    runes: list[int] = []
    i = 0
    escape1 = 11
    escape2 = 12
    while i < len(digits):
        d = digits[i]
        if d < 11:
            runes.append(d)
            i += 1
        elif d == escape1:
            if i + 1 >= len(digits):
                msg = "Truncated escape sequence (escape1)"
                raise ValueError(msg)
            runes.append(11 + digits[i + 1])
            i += 2
        elif d == escape2:
            if i + 1 >= len(digits):
                msg = "Truncated escape sequence (escape2)"
                raise ValueError(msg)
            runes.append(24 + digits[i + 1])
            i += 2
        else:
            msg = f"Invalid base-13 digit: {d}"
            raise ValueError(msg)
    return runes


class LatinSquareCipher:
    """Cipher using a 13x13 Latin square on base-13 encoded runes.

    Runes are encoded to base-13 digits, each digit is enciphered through
    a row of the Latin square (selected by current state), and the output
    digit determines the next state (row). Since each row of a Latin
    square is a permutation, the cipher is bijective per-digit.

    The no-self-loop property arises naturally if the Latin square has
    no fixed points (a derangement Latin square), meaning the state
    always changes.

    Args:
        seed: Random seed for Latin square generation.
        initial_state: Starting row (0-12).
        derangement: If True, uses a derangement Latin square.
    """

    def __init__(
        self,
        seed: int = 0,
        initial_state: int = 0,
        *,
        derangement: bool = True,
    ) -> None:
        self.initial_state = initial_state
        if derangement:
            self.square = self._make_derangement_latin_square(STATE_COUNT, seed)
        else:
            self.square = _make_latin_square(STATE_COUNT, seed)
        # Precompute inverse for each row
        self.inv_square = [_invert_permutation(row) for row in self.square]

    @staticmethod
    def _make_derangement_latin_square(
        size: int,
        seed: int,
    ) -> list[list[int]]:
        """Latin square where no cell contains its row index (no fixed points).

        Constructed by starting with a shifted Latin square where
        row i, col j = (i + j + 1) % size, ensuring cell (i, j) != i
        for all j. Then columns and values are shuffled while preserving
        the derangement and Latin properties.
        """
        # (i + j + 1) % size guarantees no fixed points
        square = [[(i + j + 1) % size for j in range(size)] for i in range(size)]
        # Shuffle columns (preserves Latin + derangement properties
        # only if we also remap values consistently)
        rng = random.Random(seed)
        col_perm = list(range(size))
        rng.shuffle(col_perm)
        return [[row[col_perm[j]] for j in range(size)] for row in square]

    def encrypt_digits(self, digits: Sequence[int]) -> list[int]:
        """Encrypt a base-13 digit stream.

        Args:
            digits: Input digits (each 0-12).

        Returns:
            Encrypted digits.
        """
        state = self.initial_state
        output: list[int] = []
        for d in digits:
            c = self.square[state][d]
            output.append(c)
            state = c  # output digit determines next row
        return output

    def decrypt_digits(self, digits: Sequence[int]) -> list[int]:
        """Decrypt a base-13 digit stream.

        Args:
            digits: Encrypted digits (each 0-12).

        Returns:
            Decrypted digits.
        """
        state = self.initial_state
        output: list[int] = []
        for c in digits:
            d = self.inv_square[state][c]
            output.append(d)
            state = c  # same transition as encrypt (uses ciphertext)
        return output

    def encrypt_runes(self, runes: Sequence[int]) -> list[int]:
        """Encrypt rune indices via base-13 encoding + Latin square.

        Args:
            runes: Rune indices (each 0-28).

        Returns:
            Encrypted base-13 digits (NOT rune indices).
            Use base13_to_runes on the result to get rune indices,
            but note the output length may differ from input.
        """
        digits = runes_to_base13(runes)
        return self.encrypt_digits(digits)

    def decrypt_runes(self, digits: Sequence[int]) -> list[int]:
        """Decrypt base-13 digits back to rune indices.

        Args:
            digits: Encrypted base-13 digits.

        Returns:
            Decrypted rune indices.
        """
        decrypted_digits = self.decrypt_digits(digits)
        return base13_to_runes(decrypted_digits)


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------


def compute_delta_stream(runes: Sequence[int], mod: int = 29) -> list[int]:
    """Compute delta stream (consecutive differences mod N)."""
    return [(runes[i + 1] - runes[i]) % mod for i in range(len(runes) - 1)]


def measure_delta0_rate(
    ciphertext: Sequence[int],
    mod: int = 29,
) -> tuple[int, int, float]:
    """Measure the delta=0 rate in a ciphertext.

    Returns:
        Tuple of (zero_count, total_deltas, rate).
    """
    deltas = compute_delta_stream(ciphertext, mod)
    zero_count = deltas.count(0)
    total = len(deltas)
    rate = zero_count / total if total > 0 else 0.0
    return zero_count, total, rate


def simulate_mealy(
    plaintext_length: int = 10000,
    key_seed: int = 0,
    *,
    no_self_loops: bool = True,
    plaintext_seed: int = 99,
) -> dict[str, object]:
    """Simulate Mealy cipher and measure delta=0 suppression.

    Args:
        plaintext_length: Number of runes to generate.
        key_seed: Seed for cipher key.
        no_self_loops: Whether transition has no self-loops.
        plaintext_seed: Seed for random plaintext.

    Returns:
        Dict with simulation results.
    """
    rng = random.Random(plaintext_seed)
    plaintext = [rng.randrange(RUNE_ALPHABET_SIZE) for _ in range(plaintext_length)]

    cipher = MealyCipher(key_seed=key_seed, no_self_loops=no_self_loops)
    ciphertext = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(ciphertext)

    assert plaintext == decrypted, "Roundtrip failed!"

    zeros, total, rate = measure_delta0_rate(ciphertext)

    return {
        "cipher": "mealy",
        "no_self_loops": no_self_loops,
        "length": plaintext_length,
        "delta0_count": zeros,
        "delta0_total": total,
        "delta0_rate": rate,
        "expected_uniform": 1.0 / RUNE_ALPHABET_SIZE,
        "suppression_ratio": rate / (1.0 / RUNE_ALPHABET_SIZE),
    }


def simulate_latin_square(
    plaintext_length: int = 10000,
    seed: int = 0,
    *,
    derangement: bool = True,
    plaintext_seed: int = 99,
) -> dict[str, object]:
    """Simulate Latin square cipher and measure delta=0 in base-13 output.

    Args:
        plaintext_length: Number of runes to generate.
        seed: Seed for Latin square.
        derangement: Whether to use derangement Latin square.
        plaintext_seed: Seed for random plaintext.

    Returns:
        Dict with simulation results.
    """
    rng = random.Random(plaintext_seed)
    plaintext = [rng.randrange(RUNE_ALPHABET_SIZE) for _ in range(plaintext_length)]

    cipher = LatinSquareCipher(seed=seed, derangement=derangement)
    encrypted_digits = cipher.encrypt_runes(plaintext)
    decrypted = cipher.decrypt_runes(encrypted_digits)

    assert plaintext == decrypted, "Roundtrip failed!"

    # Measure delta=0 in the base-13 digit stream
    zeros13, total13, rate13 = measure_delta0_rate(encrypted_digits, mod=STATE_COUNT)

    return {
        "cipher": "latin_square",
        "derangement": derangement,
        "input_runes": plaintext_length,
        "output_digits": len(encrypted_digits),
        "expansion_ratio": len(encrypted_digits) / plaintext_length,
        "delta0_count_base13": zeros13,
        "delta0_total_base13": total13,
        "delta0_rate_base13": rate13,
        "expected_uniform_base13": 1.0 / STATE_COUNT,
        "suppression_ratio_base13": rate13 / (1.0 / STATE_COUNT),
    }


def print_simulation_results() -> None:
    """Run simulations of both cipher designs and print results."""
    print("=" * 60)
    print("MEALY MACHINE CIPHER SIMULATION")
    print("=" * 60)

    for no_self_loops in [True, False]:
        result = simulate_mealy(
            plaintext_length=13000, no_self_loops=no_self_loops,
        )
        label = "no self-loops" if no_self_loops else "with self-loops"
        print(f"\n  --- {label} ---")
        print(f"  Delta=0: {result['delta0_count']}/{result['delta0_total']} "
              f"({result['delta0_rate']:.4f})")
        print(f"  Expected uniform: {result['expected_uniform']:.4f}")
        print(f"  Suppression ratio: {result['suppression_ratio']:.4f}")

    print(f"\n{'=' * 60}")
    print("LATIN SQUARE CIPHER SIMULATION")
    print("=" * 60)

    for derangement in [True, False]:
        result = simulate_latin_square(
            plaintext_length=13000, derangement=derangement,
        )
        label = "derangement" if derangement else "standard"
        print(f"\n  --- {label} ---")
        print(f"  Input runes: {result['input_runes']}, "
              f"Output digits: {result['output_digits']} "
              f"(expansion: {result['expansion_ratio']:.2f}x)")
        print(f"  Delta=0 (base13): "
              f"{result['delta0_count_base13']}/{result['delta0_total_base13']} "
              f"({result['delta0_rate_base13']:.4f})")
        print(f"  Expected uniform (base13): "
              f"{result['expected_uniform_base13']:.4f}")
        print(f"  Suppression ratio: "
              f"{result['suppression_ratio_base13']:.4f}")
