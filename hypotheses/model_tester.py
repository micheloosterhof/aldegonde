# ABOUTME: Flexible cipher model tester for Liber Primus unsolved sections.
# ABOUTME: Tries decryption models with parameter sweeps, scores by IOC and quadgrams.

"""Flexible cipher model tester for Liber Primus unsolved sections.

Each decryption model is a function:
    (ct: list[int], **params) -> list[int] | None

Models are registered with their parameter spaces. The runner tries all
parameter combinations, scores the output, and reports the best candidates.

Usage:
    python hypotheses/model_tester.py                    # run all models
    python hypotheses/model_tester.py beaufort_ct_autokey # run one model
    python hypotheses/model_tester.py --list              # list models
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product

sys.path.insert(0, "src")

from aldegonde import c3301
from aldegonde.stats.ioc import ioc as compute_ioc

ALPHABET = c3301.CICADA_ALPHABET
N = len(ALPHABET)  # 29
ENGLISH_LETTERS = c3301.CICADA_ENGLISH_ALPHABET

# Precompute modular inverses for GF(29)
_INVERSES = [0] * N
for _i in range(1, N):
    # Fermat's little theorem: a^(-1) = a^(p-2) mod p
    _INVERSES[_i] = pow(_i, N - 2, N)


def mod_inv(a: int) -> int:
    """Modular inverse in GF(29). Raises ValueError for 0."""
    a = a % N
    if a == 0:
        msg = "zero has no inverse"
        raise ValueError(msg)
    return _INVERSES[a]


# ---- Data Loading ----


def load_ciphertext(filepath: str = "data/page0-58.txt") -> list[int]:
    """Load ciphertext as a list of rune indices (0-28)."""
    with open(filepath) as f:
        raw = f.read()
    return [c3301.r2i(c) for c in raw if c in ALPHABET]


# ---- Scoring ----


def score_ioc(pt: Sequence[int]) -> float:
    """Index of Coincidence. English runeglish IOC >> 1/29 = 0.0345."""
    if len(pt) < 2:
        return 0.0
    return compute_ioc(list(pt))


def score_quadgram(pt: Sequence[int]) -> float:
    """Quadgram score using runeglish ngram data. Higher = more English-like."""
    rune_str = "".join(c3301.i2r(i) for i in pt)
    return c3301.quadgramscore(rune_str)


def plaintext_summary(pt: Sequence[int], n: int = 40) -> str:
    """First n plaintext runes as English letter equivalents."""
    return "".join(ENGLISH_LETTERS[p] for p in pt[:n])


# ---- Decryption Models ----
#
# Convention: all models operate on 0-based rune indices (F=0, EA=28).
# Models that assume 1-based indexing (EA=identity) just interpret index 28
# as the identity element.
#
# Each function signature: (ct: list[int], **params) -> list[int] | None
# Returns None if the model is inconsistent for these parameters.


def beaufort_ct_autokey(ct: list[int], *, primer: int) -> list[int]:
    """Standard Beaufort ciphertext autokey.

    P[i] = (C[i-1] - C[i]) mod 29
    Identity element: index 0 (F).
    """
    pt = []
    prev_c = primer
    for c in ct:
        pt.append((prev_c - c) % N)
        prev_c = c
    return pt


def vigenere_ct_autokey(ct: list[int], *, primer: int) -> list[int]:
    """Standard Vigenere ciphertext autokey.

    P[i] = (C[i] - C[i-1]) mod 29
    Identity element: index 0 (F).
    """
    pt = []
    prev_c = primer
    for c in ct:
        pt.append((c - prev_c) % N)
        prev_c = c
    return pt


def first_difference(ct: list[int], *, primer: int) -> list[int]:
    """First-difference cipher (cumulative sum).

    C[i] = P[i] - P[i-1] mod 29.  Decrypt: P[i] = (P[i-1] + C[i]) mod 29.
    """
    pt = []
    prev_p = primer
    for c in ct:
        p = (prev_p + c) % N
        pt.append(p)
        prev_p = p
    return pt


def _nonzero_k(state: int, offset: int) -> int:
    """Map state to a non-zero multiplier in {1, ..., 28}.

    Uses (state + offset) % 28 + 1 to guarantee non-zero output.
    """
    return (state + offset) % (N - 1) + 1


def beaufort_mult_prev_pt(
    ct: list[int], *, primer_c: int, primer_p: int, offset: int = 0,
) -> list[int]:
    """Beaufort autokey with multiplicative previous-plaintext factor.

    k[i] = ((P[i-1] + offset) % 28) + 1   (always in {1..28})
    C[i] = C[i-1] - P[i] * k[i] mod 29
    Preserves EA identity: P[i]=0 => C[i]=C[i-1] regardless of k.
    """
    pt = []
    prev_c = primer_c
    prev_p = primer_p
    for c in ct:
        k = _nonzero_k(prev_p, offset)
        p = ((prev_c - c) * _INVERSES[k]) % N
        pt.append(p)
        prev_c = c
        prev_p = p
    return pt


def beaufort_mult_running_ct(
    ct: list[int], *, primer: int, offset: int = 0,
) -> list[int]:
    """Beaufort autokey with multiplier from running ciphertext sum.

    S[i] = (primer + C[0] + ... + C[i-1]) mod 29
    k[i] = ((S[i] + offset) % 28) + 1
    C[i] = C[i-1] - P[i] * k[i] mod 29
    Preserves EA identity. S is known from ciphertext alone.
    """
    pt = []
    prev_c = primer
    running = primer
    for c in ct:
        k = _nonzero_k(running, offset)
        p = ((prev_c - c) * _INVERSES[k]) % N
        pt.append(p)
        running = (running + c) % N
        prev_c = c
    return pt


def beaufort_mult_running_pt(
    ct: list[int], *, primer_c: int, primer_s: int, offset: int = 0,
) -> list[int]:
    """Beaufort autokey with multiplier from running plaintext sum.

    S[i] = (primer_s + P[0] + ... + P[i-1]) mod 29
    k[i] = ((S[i] + offset) % 28) + 1
    C[i] = C[i-1] - P[i] * k[i] mod 29
    Preserves EA identity. S depends on plaintext (unknown a priori).
    """
    pt = []
    prev_c = primer_c
    running = primer_s
    for c in ct:
        k = _nonzero_k(running, offset)
        p = ((prev_c - c) * _INVERSES[k]) % N
        pt.append(p)
        running = (running + p) % N
        prev_c = c
    return pt


def beaufort_two_ct_feedback(
    ct: list[int], *, primer: int,
) -> list[int]:
    """Beaufort autokey using two previous ciphertext runes.

    P[i] = (C[i-1] + C[i-2] - C[i]) mod 29
    Uses C[i-1] + C[i-2] as the key instead of just C[i-1].
    """
    pt = []
    prev2 = primer
    prev1 = primer
    for i, c in enumerate(ct):
        key = (prev1 + prev2) % N
        pt.append((key - c) % N)
        prev2 = prev1
        prev1 = c
    return pt


def beaufort_mult_ct2(
    ct: list[int], *, primer: int, offset: int = 0,
) -> list[int]:
    """Beaufort autokey with multiplicative C[i-2] factor.

    k[i] = ((C[i-2] + offset) % 28) + 1
    C[i] = C[i-1] - P[i] * k[i] mod 29
    Preserves EA identity. Defeats C[i-1]-only split test because
    the multiplier varies within each C[i-1] group.
    """
    pt = []
    prev1 = primer
    prev2 = primer
    for c in ct:
        k = _nonzero_k(prev2, offset)
        p = ((prev1 - c) * _INVERSES[k]) % N
        pt.append(p)
        prev2 = prev1
        prev1 = c
    return pt


def beaufort_mult_ct2_sum(
    ct: list[int], *, primer: int, offset: int = 0,
) -> list[int]:
    """Beaufort autokey with multiplier from C[i-2] + C[i-3].

    k[i] = ((C[i-2] + C[i-3] + offset) % 28) + 1
    C[i] = C[i-1] - P[i] * k[i] mod 29
    Window w=3. Preserves EA identity.
    """
    pt = []
    prev1 = primer
    prev2 = primer
    prev3 = primer
    for c in ct:
        k = _nonzero_k((prev2 + prev3) % N, offset)
        p = ((prev1 - c) * _INVERSES[k]) % N
        pt.append(p)
        prev3 = prev2
        prev2 = prev1
        prev1 = c
    return pt


def beaufort_mult_ct2_prod(
    ct: list[int], *, primer: int, offset: int = 0,
) -> list[int]:
    """Beaufort autokey with multiplier from C[i-2] * C[i-1].

    k[i] = ((C[i-2] * C[i-1] + offset) % 28) + 1
    C[i] = C[i-1] - P[i] * k[i] mod 29
    Uses product of two preceding CT runes. Preserves EA identity.
    """
    pt = []
    prev1 = primer
    prev2 = primer
    for c in ct:
        k = _nonzero_k((prev2 * prev1) % N, offset)
        p = ((prev1 - c) * _INVERSES[k]) % N
        pt.append(p)
        prev2 = prev1
        prev1 = c
    return pt


def vigenere_mult_prev_pt(
    ct: list[int], *, primer_c: int, primer_p: int, offset: int = 0,
) -> list[int]:
    """Vigenere autokey with multiplicative previous-plaintext factor.

    k[i] = ((P[i-1] + offset) % 28) + 1
    C[i] = P[i] * k[i] + C[i-1] mod 29
    P[i] = (C[i] - C[i-1]) * inverse(k[i]) mod 29
    """
    pt = []
    prev_c = primer_c
    prev_p = primer_p
    for c in ct:
        k = _nonzero_k(prev_p, offset)
        p = ((c - prev_c) * _INVERSES[k]) % N
        pt.append(p)
        prev_c = c
        prev_p = p
    return pt


# ---- Periodic models ----


def periodic_beaufort(
    ct: list[int], *, k0: int, k1: int = 0, k2: int = 0, period: int = 2,
) -> list[int]:
    """Periodic Beaufort (non-autokey).

    P[i] = (K[i mod L] - C[i]) mod 29
    Standard periodic cipher, no feedback.
    """
    key = [k0, k1, k2][:period]
    return [(key[i % period] - c) % N for i, c in enumerate(ct)]


def periodic_vigenere(
    ct: list[int], *, k0: int, k1: int = 0, k2: int = 0, period: int = 2,
) -> list[int]:
    """Periodic Vigenere (non-autokey).

    P[i] = (C[i] - K[i mod L]) mod 29
    """
    key = [k0, k1, k2][:period]
    return [(c - key[i % period]) % N for i, c in enumerate(ct)]


def periodic_mult_autokey(
    ct: list[int], *, primer: int,
    k0: int, k1: int = 1, k2: int = 1, period: int = 2,
) -> list[int]:
    """Beaufort ciphertext autokey with periodic multiplier.

    K[i] = key[i mod L]   (each in {1..28}, non-zero)
    C[i] = C[i-1] - P[i] * K[i] mod 29
    P[i] = (C[i-1] - C[i]) * inverse(K[i]) mod 29

    Preserves EA identity: P[i]=0 => C[i]=C[i-1] regardless of K.
    Friedman test cannot detect the period (autokey feedback dominates).
    """
    key = [k0, k1, k2][:period]
    pt = []
    prev_c = primer
    for i, c in enumerate(ct):
        k = key[i % period]
        p = ((prev_c - c) * _INVERSES[k]) % N
        pt.append(p)
        prev_c = c
    return pt


def periodic_add_autokey(
    ct: list[int], *, primer: int,
    k0: int, k1: int = 0, k2: int = 0, period: int = 2,
) -> list[int]:
    """Beaufort ciphertext autokey with periodic additive key.

    C[i] = C[i-1] - P[i] + K[i mod L] mod 29
    P[i] = (C[i-1] - C[i] + K[i mod L]) mod 29

    Does NOT preserve EA identity (C[i] = C[i-1] + K, not C[i-1]).
    Friedman test cannot detect the period.
    """
    key = [k0, k1, k2][:period]
    pt = []
    prev_c = primer
    for i, c in enumerate(ct):
        p = (prev_c - c + key[i % period]) % N
        pt.append(p)
        prev_c = c
    return pt


# ---- Model Registry ----


@dataclass
class Model:
    """A decryption model with its parameter search space."""

    name: str
    func: Callable[..., list[int] | None]
    params: dict[str, list[int]]
    description: str


def _r(start_or_n: int, stop: int | None = None) -> list[int]:
    """Shorthand for list(range(...)). _r(n) or _r(start, stop)."""
    if stop is None:
        return list(range(start_or_n))
    return list(range(start_or_n, stop))


MODELS: list[Model] = [
    Model(
        "beaufort_ct_autokey",
        beaufort_ct_autokey,
        {"primer": _r(N)},
        "Beaufort ciphertext autokey (baseline, disproved)",
    ),
    Model(
        "vigenere_ct_autokey",
        vigenere_ct_autokey,
        {"primer": _r(N)},
        "Vigenere ciphertext autokey (baseline, disproved)",
    ),
    Model(
        "first_difference",
        first_difference,
        {"primer": _r(N)},
        "First-difference / cumulative sum cipher",
    ),
    Model(
        "beaufort_mult_prev_pt",
        beaufort_mult_prev_pt,
        {"primer_c": _r(N), "primer_p": _r(N), "offset": _r(N - 1)},
        "Beaufort * ((prev_pt + offset) % 28 + 1), EA-preserving",
    ),
    Model(
        "beaufort_mult_running_ct",
        beaufort_mult_running_ct,
        {"primer": _r(N), "offset": _r(N - 1)},
        "Beaufort * ((running_ct_sum + offset) % 28 + 1), EA-preserving",
    ),
    Model(
        "beaufort_mult_running_pt",
        beaufort_mult_running_pt,
        {"primer_c": _r(N), "primer_s": _r(N), "offset": _r(N - 1)},
        "Beaufort * ((running_pt_sum + offset) % 28 + 1), EA-preserving",
    ),
    Model(
        "beaufort_two_ct",
        beaufort_two_ct_feedback,
        {"primer": _r(N)},
        "Beaufort with C[i-1]+C[i-2] as key",
    ),
    Model(
        "vigenere_mult_prev_pt",
        vigenere_mult_prev_pt,
        {"primer_c": _r(N), "primer_p": _r(N), "offset": _r(N - 1)},
        "Vigenere * ((prev_pt + offset) % 28 + 1), EA-preserving",
    ),
    # ---- Window-2 and window-3 multiplicative autokey ----
    Model(
        "beaufort_mult_ct2",
        beaufort_mult_ct2,
        {"primer": _r(N), "offset": _r(N - 1)},
        "Beaufort * ((C[i-2] + offset) % 28 + 1), w=2, EA-preserving",
    ),
    Model(
        "beaufort_mult_ct2_sum",
        beaufort_mult_ct2_sum,
        {"primer": _r(N), "offset": _r(N - 1)},
        "Beaufort * ((C[i-2]+C[i-3] + offset) % 28 + 1), w=3, EA-preserving",
    ),
    Model(
        "beaufort_mult_ct2_prod",
        beaufort_mult_ct2_prod,
        {"primer": _r(N), "offset": _r(N - 1)},
        "Beaufort * ((C[i-2]*C[i-1] + offset) % 28 + 1), w=2, EA-preserving",
    ),
    # ---- Periodic non-autokey ----
    Model(
        "periodic_beaufort_L2",
        lambda ct, **kw: periodic_beaufort(ct, period=2, **kw),
        {"k0": _r(N), "k1": _r(N)},
        "Periodic Beaufort, period 2 (non-autokey, Friedman-disproved baseline)",
    ),
    Model(
        "periodic_beaufort_L3",
        lambda ct, **kw: periodic_beaufort(ct, period=3, **kw),
        {"k0": _r(N), "k1": _r(N), "k2": _r(N)},
        "Periodic Beaufort, period 3 (non-autokey)",
    ),
    # ---- Periodic multiplicative autokey (EA-preserving) ----
    Model(
        "periodic_mult_autokey_L2",
        lambda ct, **kw: periodic_mult_autokey(ct, period=2, **kw),
        {"primer": _r(N), "k0": _r(1, N), "k1": _r(1, N)},
        "Beaufort autokey * periodic key, L=2, EA-preserving",
    ),
    Model(
        "periodic_mult_autokey_L3",
        lambda ct, **kw: periodic_mult_autokey(ct, period=3, **kw),
        {"primer": _r(N), "k0": _r(1, N), "k1": _r(1, N), "k2": _r(1, N)},
        "Beaufort autokey * periodic key, L=3, EA-preserving",
    ),
    # ---- Periodic additive autokey ----
    Model(
        "periodic_add_autokey_L2",
        lambda ct, **kw: periodic_add_autokey(ct, period=2, **kw),
        {"primer": _r(N), "k0": _r(N), "k1": _r(N)},
        "Beaufort autokey + periodic key, L=2 (no EA identity)",
    ),
    Model(
        "periodic_add_autokey_L3",
        lambda ct, **kw: periodic_add_autokey(ct, period=3, **kw),
        {"primer": _r(N), "k0": _r(N), "k1": _r(N), "k2": _r(N)},
        "Beaufort autokey + periodic key, L=3 (no EA identity)",
    ),
]


# ---- Runner ----


def param_space_size(params: dict[str, list[int]]) -> int:
    """Total number of parameter combinations."""
    size = 1
    for v in params.values():
        size *= len(v)
    return size


def run_model(
    model: Model, ct: list[int], top_n: int = 5, quadgram_top: int = 5,
) -> None:
    """Try all parameter combinations, report top results by IOC."""
    total = param_space_size(model.params)
    print(f"\n{'=' * 70}")
    print(f"Model: {model.name}")
    print(f"  {model.description}")
    print(f"  Params: {', '.join(model.params.keys())} ({total} combinations)")

    param_names = sorted(model.params.keys())
    param_values = [model.params[k] for k in param_names]

    results: list[tuple[float, dict[str, int], list[int]]] = []
    failed = 0

    t0 = time.time()
    for combo in product(*param_values):
        params = dict(zip(param_names, combo))
        pt = model.func(ct, **params)
        if pt is None:
            failed += 1
            continue
        results.append((score_ioc(pt), params, pt))
    elapsed = time.time() - t0

    print(f"  Completed in {elapsed:.1f}s "
          f"({len(results)} ok, {failed} inconsistent)")

    if not results:
        print("  No consistent results.")
        return

    results.sort(key=lambda x: -x[0])

    iocs = [r[0] for r in results]
    print(f"  IOC range: {min(iocs):.6f} - {max(iocs):.6f} "
          f"(random: {1/N:.6f})")

    print(f"\n  Top {top_n} by IOC:")
    header = f"  {'#':>3} {'IOC':>10}"
    if quadgram_top > 0:
        header += f" {'Quadgram':>10}"
    header += f"  {'Params':<30} {'Plaintext (first 40 runes)'}"
    print(header)
    print(f"  {'-' * 95}")

    for i, (ioc_val, params, pt) in enumerate(results[:top_n]):
        qg_str = ""
        if i < quadgram_top:
            qg = score_quadgram(pt)
            qg_str = f" {qg:>10.1f}"
        else:
            qg_str = f" {'':>10}"
        param_str = ", ".join(f"{k}={v}" for k, v in sorted(params.items()))
        eng = plaintext_summary(pt)
        print(f"  {i+1:>3} {ioc_val:>10.6f}{qg_str}  {param_str:<30} {eng}")


def list_models() -> None:
    """Print available models and their parameter spaces."""
    print("Available models:\n")
    for m in MODELS:
        total = param_space_size(m.params)
        params = ", ".join(f"{k}[{len(v)}]" for k, v in m.params.items())
        print(f"  {m.name}")
        print(f"    {m.description}")
        print(f"    Params: {params} = {total} combinations")
        print()


def main() -> None:
    args = sys.argv[1:]

    if "--list" in args:
        list_models()
        return

    ct = load_ciphertext()
    print(f"Ciphertext: {len(ct)} runes")
    print(f"Ciphertext IOC: {score_ioc(ct):.6f} (random: {1/N:.6f})")

    requested = [a for a in args if not a.startswith("-")]
    top_n = 10

    for model in MODELS:
        if requested and model.name not in requested:
            continue
        # Skip very large param spaces unless explicitly requested
        total = param_space_size(model.params)
        if not requested and total > 30000:
            print(f"\n  Skipping {model.name} ({total} combinations). "
                  f"Run explicitly: python {sys.argv[0]} {model.name}")
            continue
        run_model(model, ct, top_n=top_n)


if __name__ == "__main__":
    main()
