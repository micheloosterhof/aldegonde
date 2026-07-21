#!/usr/bin/env python3
# ABOUTME: The length-clocked progressive substitution (order-5-g model) with a
# ABOUTME: matching decryption and a round-trip test. Shared infra for attacks.
"""Model (see hypotheses/length-clocked-walk.md), per word w, position j (0-idx):

    c[j] = base_w( g^(j mod 5)( p[j] ) )
    base_{w+1} = base_w ∘ g^((L_w - 1) mod 5) ∘ σ

Key = (base_0, g, σ): g an order-5 permutation, σ a general permutation, base_0
a general permutation, all on 0..M-1. The per-word base is a deterministic walk
clocked by the PUBLIC word lengths, so decryption is exact given the key:

    p[j] = g^-(j mod 5)( base_w^-1( c[j] ) )

Permutations are lists p with p[i] = image of i. compose(a,b)[i] = a[b[i]].
"""

from __future__ import annotations

M = 29


def compose(a: list[int], b: list[int]) -> list[int]:
    """(a ∘ b)[i] = a[b[i]]."""
    return [a[b[i]] for i in range(len(b))]


def inverse(p: list[int]) -> list[int]:
    inv = [0] * len(p)
    for i, x in enumerate(p):
        inv[x] = i
    return inv


def powers(p: list[int], upto: int) -> list[list[int]]:
    """[p^0, p^1, ..., p^(upto-1)]."""
    out = [list(range(len(p)))]
    for _ in range(1, upto):
        out.append(compose(p, out[-1]))
    return out


def bases(base0: list[int], g: list[int], sigma: list[int],
          lengths: list[int]) -> list[list[int]]:
    """The per-word base_w for w = 0..len(lengths)-1 (base for the LAST word is
    not stepped past). base_{w+1} = base_w ∘ g^((L_w-1) mod 5) ∘ σ."""
    gp = powers(g, 5)
    out = [base0]
    base = base0
    for L in lengths[:-1]:
        base = compose(compose(base, gp[(L - 1) % 5]), sigma)
        out.append(base)
    return out


def encrypt(words: list[list[int]], base0: list[int], g: list[int],
            sigma: list[int]) -> list[list[int]]:
    gp = powers(g, 5)
    lengths = [len(w) for w in words]
    ct = []
    for base_w, w in zip(bases(base0, g, sigma, lengths), words):
        ct.append([base_w[gp[j % 5][p]] for j, p in enumerate(w)])
    return ct


def decrypt(ct: list[list[int]], base0: list[int], g: list[int],
            sigma: list[int]) -> list[list[int]]:
    gip = [inverse(p) for p in powers(g, 5)]  # g^-(k)
    lengths = [len(w) for w in ct]
    pt = []
    for base_w, cw in zip(bases(base0, g, sigma, lengths), ct):
        bi = inverse(base_w)
        pt.append([gip[j % 5][bi[c]] for j, c in enumerate(cw)])
    return pt


# ---------- key construction ----------

def order5_from_grid(order25: list[int], fixed4: list[int]) -> list[int]:
    """g = five 5-cycles (columns of a 5x5 grid) + 4 fixed. order25 is 25 runes
    row-major; column k is a 5-cycle."""
    g = list(range(M))
    for col in range(5):
        cells = [order25[row * 5 + col] for row in range(5)]
        for row in range(5):
            g[cells[row]] = cells[(row + 1) % 5]
    return g


def _selftest() -> None:
    import random

    rng = random.Random(3301)
    # random order-5 g (five 5-cycles + 4 fixed) via a shuffled grid
    perm = list(range(M))
    rng.shuffle(perm)
    g = order5_from_grid(perm[:25], perm[25:])
    assert powers(g, 6)[5] == list(range(M)), "g must have order 5 (g^5=id)"
    sigma = list(range(M))
    rng.shuffle(sigma)
    base0 = list(range(M))
    rng.shuffle(base0)

    words = [[rng.randrange(M) for _ in range(rng.randint(1, 12))]
             for _ in range(500)]
    ct = encrypt(words, base0, g, sigma)
    rec = decrypt(ct, base0, g, sigma)
    assert rec == words, "round-trip failed"
    # a wrong key must NOT decrypt
    bad = base0[:]
    bad[0], bad[1] = bad[1], bad[0]
    assert decrypt(ct, bad, g, sigma) != words, "wrong key decrypted (bug)"
    print("round-trip OK: encrypt/decrypt inverse on 500 words; wrong key fails")


if __name__ == "__main__":
    _selftest()
