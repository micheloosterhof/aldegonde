# ABOUTME: Scores a walk key (letter perms + sigma) on a ciphertext with base_0 unknown,
# ABOUTME: using only plaintext unigram frequencies; self-tests on the planted-key corpus.
"""A verifier for the length-clocked walk that needs neither base_0 nor DJU-BEI.

Under the walk, c = base_0( M_w( g_j( p ) ) ) with M_w a KNOWN product once the
letter perms g_j and sigma are fixed. Write u = base_0^-1(c). Then

    p = g_j^-1( M_w^-1( u ) )

so every ciphertext rune value c stands for ONE unknown point u, and all ~447
positions carrying that rune decrypt through known permutations of the same u.
For the right key and the right u those decrypts follow the plaintext unigram
distribution; for a wrong key, or a wrong u, they are flat. So

    S[c][u] = sum over positions i with ciphertext c of  log f( g_j^-1 M_w^-1 (u) )

and the key's score is sum_c max_u S[c][u], reported as nats per rune above the
flat baseline. The argmax over u is base_0^-1 itself, read off for free.

Cost is 29 table lookups per rune and no hill-climb, so a key is verified on a
few hundred words in well under a millisecond of compiled code. The score needs
no repeated phrase, so it does not depend on reading DJU-BEI as a state return.

Run with no arguments for the self-test on `walk_reference.json` (a corpus
enciphered under a known key): the true key must separate from one-swap
neighbours and from random keys without being told base_0, and the recovered
base_0 must match the planted one.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

M = 29
REFERENCE = ROOT / "experiments" / "walk_reference.json"
UNIGRAMS = ROOT / "src" / "aldegonde" / "data" / "ngrams" / "runeglish" / "unigrams.txt"
# the unigram table spells J with a variant glyph
GLYPH_VARIANTS = {"ᛂ": "ᛄ"}


def log_frequencies() -> np.ndarray:
    """Natural-log plaintext unigram frequencies, indexed by rune index."""
    index = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
    counts = np.zeros(M)
    for line in UNIGRAMS.read_text().splitlines():
        rune, count = line.split()
        counts[index[GLYPH_VARIANTS.get(rune, rune)]] += float(count)
    assert (counts > 0).all(), "unigram table does not cover the alphabet"
    return np.log(counts / counts.sum())


def inverse(p: np.ndarray) -> np.ndarray:
    q = np.empty(M, dtype=np.int64)
    q[p] = np.arange(M)
    return q


def powers(g: list[int]) -> list[np.ndarray]:
    """g^0..g^4 as the five letter perms of a fixed-g walk."""
    ga = np.asarray(g)
    out = [np.arange(M)]
    for _ in range(4):
        out.append(ga[out[-1]])
    return out


def score_table(ct_words, letter_perms, sigma, logf, n_words=None) -> np.ndarray:
    """S[c][u]: log-likelihood of ciphertext rune c standing for base_0^-1(c) = u.

    `letter_perms[j % 5]` enciphers within-word position j; the base advances by
    `letter_perms[(L - 1) % 5] . sigma` after a word of length L.
    """
    sig = np.asarray(sigma)
    by_phase = [logf[inverse(np.asarray(g))] for g in letter_perms]
    step_inv = [inverse(np.asarray(g)[sig]) for g in letter_perms]
    table = np.zeros((M, M))
    m_inv = np.arange(M)
    for word in ct_words[:n_words]:
        for j, c in enumerate(word):
            table[c] += by_phase[j % 5][m_inv]
        m_inv = step_inv[(len(word) - 1) % 5][m_inv]
    return table


def score_key(ct_words, letter_perms, sigma, logf, n_words=None):
    """(nats per rune above the flat baseline, recovered base_0^-1)."""
    table = score_table(ct_words, letter_perms, sigma, logf, n_words)
    runes = sum(len(w) for w in ct_words[:n_words])
    best_u = table.argmax(axis=1)
    return (table.max(axis=1).sum() - runes * logf.mean()) / runes, best_u


def swap_two(p: list[int], rng: random.Random) -> list[int]:
    """p with two images exchanged (one transposition away)."""
    q = p[:]
    a, b = rng.sample(range(M), 2)
    q[a], q[b] = q[b], q[a]
    return q


def conjugate_swap(g: list[int], rng: random.Random) -> list[int]:
    """g conjugated by a transposition: same cycle type, nearest neighbour."""
    while True:
        t = list(range(M))
        a, b = rng.sample(range(M), 2)
        t[a], t[b] = b, a
        h = [t[g[t[x]]] for x in range(M)]
        if h != g:  # swapping two fixed points of g changes nothing
            return h


def self_test() -> None:
    with REFERENCE.open() as fh:
        ref = json.load(fh)
    g, sigma, base0 = ref["g"], ref["sigmas"][0], ref["base0"]
    ct = ref["ciphertext_words"]
    logf = log_frequencies()
    rng = random.Random(3301)

    print("planted-key corpus, base_0 withheld; score = nats/rune above flat\n")
    print(
        f"{'words':>6}{'true key':>10}{'1-swap sigma':>22}{'1-conj g':>20}{'random sigma':>22}"
    )
    for n_words in (100, 200, 400, 2928):
        true_score, best_u = score_key(ct, powers(g), sigma, logf, n_words)
        wrong = {"swap": [], "conj": [], "rand": []}
        for _ in range(40):
            wrong["swap"].append(
                score_key(ct, powers(g), swap_two(sigma, rng), logf, n_words)[0]
            )
            wrong["conj"].append(
                score_key(ct, powers(conjugate_swap(g, rng)), sigma, logf, n_words)[0]
            )
            wrong["rand"].append(
                score_key(ct, powers(g), rng.sample(range(M), M), logf, n_words)[0]
            )
        cells = [f"{np.mean(v):.3f} (max {np.max(v):.3f})" for v in wrong.values()]
        print(f"{n_words:>6}{true_score:>10.3f}" + "".join(f"{c:>22}" for c in cells))
        worst = max(max(v) for v in wrong.values())
        spread = max(np.std(v) for v in wrong.values())
        if n_words >= 200:
            assert true_score - worst > 8 * spread, "true key does not separate"
        if n_words == 2928:
            recovered = inverse(best_u)
            agree = int((recovered == np.asarray(base0)).sum())
            print(f"\nbase_0 recovered by argmax alone: {agree}/29 images correct")
            assert agree >= 27, "base_0 not recovered"
    print("self-test passed")


if __name__ == "__main__":
    self_test()
