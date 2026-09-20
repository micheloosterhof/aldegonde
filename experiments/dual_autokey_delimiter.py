# ABOUTME: Dual autokey (lag-1 ciphertext, lag-5 plaintext) with arbitrary permutation
# ABOUTME: taps and a word delimiter that advances the state, against the LP profile.
"""Can a delimiter step rescue the dual autokey?

`dual-autokey-lag1-lag5.md` closed the family on two grounds. Both are narrower than
they look, and this script tests what is left.

1. **The doublet floor of 0.86%.** That was computed for
   `c_j = alpha*p_j + c_{j-1} + gamma*p_{j-5}` under a rune-to-value labelling, where
   the induced plaintext relation is conjugate to multiplication by lambda and its
   cycle type is fixed by ord(lambda) | 28. With ARBITRARY permutation taps

       c_j = a(p_j) + c_{j-1} + b(p_{j-5})     (mod 29)

   the induced relation pi = a^-1(-b(.)) is an arbitrary permutation, so the floor
   argument does not apply and the observed 0.63% is reachable.

2. **Every per-word reset randomises the seam.** The suppression needs the state to
   cancel between adjacent positions, and a reset breaks that cancellation. But a
   reset is not the only delimiter action. If the separator is a position that
   advances the state by a CONSTANT, the cancellation survives -- the constant drops
   out of the seam difference the same way the state does -- while the plaintext tap
   can still be clocked per word.

The doublet condition is `a(p_j) + b(p_{j-5}) = 0`, i.e. `p_j = pi(p_{j-5})`, so the
within-word rate is pi's diagonal on the plaintext distance-5 pair table. The same pi
governs the distance-5 echo, which is what this script measures.

**Result (2026-09-20).** Both objections fall, and the family still fails.

Permutation taps reach a within-word doublet rate of 0.0051 against the LP's 0.0063,
so the 0.86% floor was an artifact of the labelling parametrisation. The delimiter
constant is a free knob on the seam that leaves the within-word rate untouched: over
its 29 values the seam runs from 0.0475 down to 0.0106 while d1 stays at 0.0045. A
per-word RESET still pins the seam at chance (0.0348), so the file's finding holds
for resets and does not extend to a constant step. Tuning both at once reaches
d1 = 0.0051 and seam = 0.0072 against the LP's 0.0063 and 0.0079.

What remains is the period-5 structure, and it is absent at every setting:

    pi fixed points      d1     seam      d2      d4      d5      d6
    0 (tuned)        0.0051   0.0072  0.0355  0.0367  0.0329  0.0343
    29 (identity)    0.0650   0.0222  0.0371  0.0317  0.0320  0.0353
    LP               0.0063   0.0079  0.0347  0.0410  0.0492  0.0245

d4, d5 and d6 sit at chance for every relation pi, under both tap clocks and every
delimiter value. This is the lag theorem of `dual-autokey-lag1-lag5.md`: with a lag-1
feedback, c_j - c_{j-d} is a sum of d plaintext terms, and a sum of two or more terms
mod 29 convolves to uniform. Permutation taps and a delimiter step do not change
that, because the combination is still addition.

Run with no arguments for the self-test (round-trip decryption, the tuned floor, and
the seam behaviour of each delimiter action). `--sweep` reports the profile.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import prose_corpora  # noqa: E402

M = 29
# the LP's clean corpus, for reference
LP_PROFILE = {"d1": 0.0063, "seam": 0.0079, "d4": 0.0410, "d5": 0.0492, "d6": 0.0245}


def encipher(plain, a, b, *, delimiter: int | None, word_tap: bool):
    """c_j = a(p_j) + c_{j-1} + b(p_{j-5}), with a delimiter action at each boundary.

    delimiter   None resets the state at each word; an integer advances it by that
                constant, standing for a separator position whose ciphertext is not
                written. 0 is the continuous recursion.
    word_tap    True clocks the lag-5 plaintext tap inside the word (so it is silent
                for the first five runes); False clocks it over the whole rune stream.
    """
    out, state, stream = [], 0, []
    for word in plain:
        state = 0 if delimiter is None else (state + delimiter) % M
        cipher_word = []
        for j, p in enumerate(word):
            tap = (
                word[j - 5]
                if word_tap and j >= 5
                else (stream[-5] if len(stream) >= 5 else 0)
            )
            state = (a[p] + state + b[tap]) % M
            cipher_word.append(state)
            stream.append(p)
        out.append(cipher_word)
    return out


def decipher(cipher, a, b, *, delimiter: int | None, word_tap: bool):
    """Inverse of `encipher`; 29 is prime so every permutation tap is invertible."""
    a_inv = [0] * M
    for x, y in enumerate(a):
        a_inv[y] = x
    out, state, stream = [], 0, []
    for word in cipher:
        state = 0 if delimiter is None else (state + delimiter) % M
        plain_word = []
        for j, c in enumerate(word):
            tap = (
                plain_word[j - 5]
                if word_tap and j >= 5
                else (stream[-5] if len(stream) >= 5 else 0)
            )
            plain_word.append(a_inv[(c - state - b[tap]) % M])
            stream.append(plain_word[-1])
            state = c
        out.append(plain_word)
    return out


def profile(cipher) -> dict[str, float]:
    """Within-word coincidence at distances 1..6 and the cross-word seam rate."""
    out = {}
    for d in (1, 2, 3, 4, 5, 6):
        hits = total = 0
        for word in cipher:
            for j in range(len(word) - d):
                total += 1
                hits += word[j] == word[j + d]
        out[f"d{d}"] = hits / total if total else float("nan")
    seam = sum(1 for x, y in zip(cipher, cipher[1:]) if x and y and x[-1] == y[0])
    out["seam"] = seam / max(1, len(cipher) - 1)
    return out


def pair_table(plain, *, word_tap: bool, distance: int = 5) -> np.ndarray:
    """P[x][y]: how often the lag-5 tap reads x while the current plaintext rune is y.

    Built with the same clock as the cipher, so that the doublet rate really is this
    table's pi-diagonal: within the word when `word_tap`, over the rune stream if not.
    """
    table = np.zeros((M, M))
    if word_tap:
        for word in plain:
            for j in range(distance, len(word)):
                table[word[j - distance], word[j]] += 1
    else:
        stream = [p for word in plain for p in word]
        for j in range(distance, len(stream)):
            table[stream[j - distance], stream[j]] += 1
    return table / max(1.0, table.sum())


def seam_table(plain, *, word_tap: bool, distance: int = 5) -> np.ndarray:
    """P[x][y]: the lag-5 tap reads x while y opens the next word.

    The seam doublet condition is a(y) + b(x) + delimiter = 0, so the seam rate is a
    diagonal on THIS table while the within-word rate is a diagonal on `pair_table`.
    One relation, two tables: the same split the walk handles with g and sigma.
    """
    table = np.zeros((M, M))
    stream, starts = [], []
    for word in plain:
        starts.append(len(stream))
        stream.extend(word)
    for word, start in zip(plain, starts):
        if not word:
            continue
        if word_tap:
            continue  # the tap is silent at a word start under the per-word clock
        tap = stream[start - distance] if start >= distance else 0
        table[tap, word[0]] += 1
    return table / max(1.0, table.sum())


def tuned_pi(table: np.ndarray, keep: int) -> list[int]:
    """A permutation with `keep` fixed points, otherwise sent to rare partners.

    keep = 29 is the identity, which makes the doublet condition 'the plaintext
    repeats at distance 5'. keep = 0 is the rarest available assignment. The sweep
    walks between them to show that one object sets both the doublet rate and the
    distance-5 echo.
    """
    from scipy.optimize import linear_sum_assignment  # noqa: PLC0415

    cost = table.copy()
    order = np.argsort(-table.diagonal())
    fixed = set(order[:keep].tolist())
    for x in fixed:
        cost[x, :] = 1.0
        cost[x, x] = 0.0
    rows, cols = linear_sum_assignment(cost)
    return [int(c) for c in cols[np.argsort(rows)]]


def random_permutation(rng: random.Random) -> list[int]:
    p = list(range(M))
    rng.shuffle(p)
    return p


def taps_from_pi(pi: list[int], a: list[int]) -> list[int]:
    """The b tap that makes the doublet condition `p_j = pi(p_{j-5})`."""
    return [(-a[pi[x]]) % M for x in range(M)]


def self_test() -> None:
    rng = random.Random(3301)
    plain = prose_corpora(2928, 1)[0]
    a, b = random_permutation(rng), random_permutation(rng)
    for delimiter in (None, 0, 7):
        for word_tap in (True, False):
            cipher = encipher(plain, a, b, delimiter=delimiter, word_tap=word_tap)
            back = decipher(cipher, a, b, delimiter=delimiter, word_tap=word_tap)
            assert back == plain, f"round trip failed for {delimiter}, {word_tap}"
    print("round-trip decryption holds for every delimiter action")

    # The doublet rate must be the tuned relation's diagonal on the tap's own table.
    table = pair_table(plain, word_tap=False)
    pi = tuned_pi(table, keep=0)
    b_low = taps_from_pi(pi, a)
    predicted = float(sum(table[x, pi[x]] for x in range(M)))
    got = profile(encipher(plain, a, b_low, delimiter=0, word_tap=False))
    print(
        f"within-word d1: predicted {predicted:.4f} from the table, measured {got['d1']:.4f}"
    )
    assert abs(predicted - got["d1"]) < 0.004, "the doublet rate is not pi's diagonal"

    # The 0.86% floor of the linear family does not apply to permutation taps.
    assert predicted < 0.0063, (
        f"tuned relation should beat the LP's 0.0063, got {predicted:.4f}"
    )
    print(
        f"a tuned permutation relation reaches {predicted:.4f}, under the LP's 0.0063"
    )

    # The delimiter constant is a knob on the seam that leaves the within-word rate
    # alone; a reset gives no knob and pins the seam at chance.
    seams = []
    for delimiter in range(M):
        cipher = encipher(plain, a, b_low, delimiter=delimiter, word_tap=False)
        seams.append(profile(cipher))
    within = {round(s["d1"], 4) for s in seams}
    assert len(within) == 1, (
        f"the delimiter should not move the within-word rate: {within}"
    )
    low = min(s["seam"] for s in seams)
    high = max(s["seam"] for s in seams)
    print(
        f"over 29 delimiter values: within-word d1 fixed at {within.pop():.4f}, seam {low:.4f} to {high:.4f}"
    )
    assert low < 0.015, "the delimiter should be able to suppress the seam"

    reset = [profile(encipher(plain, a, b_low, delimiter=None, word_tap=False))["seam"]]
    print(
        f"with a per-word reset the seam is {reset[0]:.4f} against chance {1 / M:.4f}"
    )
    assert reset[0] > 0.025, "a reset should leave the seam at chance"
    print("self-test passed")


def sweep(draws: int = 6) -> None:
    """d1 and the distance-5 echo as the relation pi moves from tuned to identity.

    pi sets the doublet rate. The question is whether anything in the family sets the
    echo independently, under either tap clock and with the delimiter free.
    """
    rng = random.Random(3301)
    corpora = prose_corpora(2928, draws)
    print("LP: " + "  ".join(f"{k} {v:.4f}" for k, v in LP_PROFILE.items()))
    print(f"mean of {draws} prose corpora; chance is {1 / M:.4f}\n")
    for word_tap in (False, True):
        clock = "tap clocked per word" if word_tap else "tap clocked over the stream"
        print(f"--- {clock}")
        print(
            f"{'pi fixed points':>16}{'d1':>9}{'seam*':>9}{'d2':>9}{'d4':>9}{'d5':>9}{'d6':>9}"
        )
        for keep in (0, 5, 10, 20, 25, 29):
            rows = []
            for plain in corpora:
                a = random_permutation(rng)
                pi = tuned_pi(pair_table(plain, word_tap=word_tap), keep)
                b = taps_from_pi(pi, a)
                best = None
                for delimiter in range(M):
                    got = profile(
                        encipher(plain, a, b, delimiter=delimiter, word_tap=word_tap)
                    )
                    if best is None or abs(got["seam"] - LP_PROFILE["seam"]) < abs(
                        best["seam"] - LP_PROFILE["seam"]
                    ):
                        best = got
                rows.append(best)
            cells = "".join(
                f"{sum(r[k] for r in rows) / len(rows):>9.4f}"
                for k in ("d1", "seam", "d2", "d4", "d5", "d6")
            )
            print(f"{keep:>16}{cells}", flush=True)
        print()
    print("* seam: the best of the 29 delimiter values against the LP's 0.0079")


if __name__ == "__main__":
    if "--sweep" in sys.argv:
        sweep()
    else:
        self_test()
