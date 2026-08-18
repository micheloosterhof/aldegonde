# ABOUTME: How many known-plaintext words pin the letter step g? Within-word
# ABOUTME: ciphertext collisions give base-free constraints g^d(a)=b; measured on a planted key.
"""What does a crib actually buy for the KEY, not just for base_0?

`crib_propagation.py` measured the budget to pin `base_0` GIVEN `(g, sigma)`
(median 80 contiguous runes). Nothing measured the budget for `g` itself, which
is what decides whether the ~31 title slots of `rubrication-crib-candidates.md`
are a route to the key or merely a verifier for candidates we cannot generate.

**The channel.** Inside one word the base is constant, so it cancels between two
positions:

    c_j = psi_w(g^(j%5)(p_j)),  c_j' = psi_w(g^(j'%5)(p_j'))
    c_j == c_j'  <=>  g^(j%5)(p_j) = g^(j'%5)(p_j')  <=>  g^d(p_j) = p_j'

with d = (j - j') mod 5. With the plaintext KNOWN this is a direct constraint on
`g` alone -- no base_0, no sigma, no word position. So cribs anywhere in the book
contribute to the same pool, and scattered title cribs are as good as contiguous
ones for this purpose. (d = 0 degenerates to p_j = p_j', the key-free d5 rule of
`d5-partial-alphabet-leak.md`, and carries no information about `g`.)

**Resolution.** g has order 5, so a constraint g^d(a) = b places a and b in one
5-cycle at offset d: union-find with a mod-5 potential. A cycle is solved when
its component holds 5 elements; g^d(a) = a with d != 0 marks a fixed point
(gcd(d,5) = 1 forces g(a) = a).

Everything is measured on `walk_reference.json`, whose planted key makes every
derived constraint checkable against the truth -- the run asserts this.

Non-collisions carry information too (g^d(a) != b) and are ~29x more numerous;
they are counted but not propagated, so the headline number is a LOWER bound on
what a full CSP could extract.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import M, ppow  # noqa: E402

REF = Path(__file__).resolve().parent / "walk_reference.json"


class CycleUnion:
    """Union-find over runes with a mod-5 offset: find(a) returns (root, offset)
    meaning g^offset(root) = a."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.off = [0] * n
        self.fixed: set[int] = set()
        self.contradiction = False

    def find(self, a: int) -> tuple[int, int]:
        if self.parent[a] == a:
            return a, 0
        root, off = self.find(self.parent[a])
        self.parent[a] = root
        self.off[a] = (self.off[a] + off) % 5
        return root, self.off[a]

    def union(self, a: int, b: int, d: int) -> None:
        """Assert g^d(a) = b."""
        ra, oa = self.find(a)
        rb, ob = self.find(b)
        if ra == rb:
            if (oa + d) % 5 != ob:
                self.contradiction = True
            return
        self.parent[rb] = ra
        self.off[rb] = (oa + d - ob) % 5

    def note_fixed(self, a: int) -> None:
        self.fixed.add(a)

    def components(self) -> dict[int, dict[int, int]]:
        comp: dict[int, dict[int, int]] = {}
        for a in range(len(self.parent)):
            r, o = self.find(a)
            comp.setdefault(r, {})[a] = o
        return comp

    def known_g(self) -> dict[int, int]:
        """Points where g(a) is determined: a fixed point, or a component member
        sitting one offset ahead of a."""
        out = {a: a for a in self.fixed}
        for members in self.components().values():
            by_off: dict[int, int] = {}
            for a, o in members.items():
                by_off[o] = a
            for a, o in members.items():
                nxt = by_off.get((o + 1) % 5)
                if nxt is not None and a not in out:
                    out[a] = nxt
        return out


def word_constraints(p: list[int], c: list[int]):
    """(d, a, b) equalities meaning g^d(a)=b, plus the count of inequalities."""
    eqs, neq = [], 0
    for j in range(len(p)):
        for jp in range(len(p)):
            if j == jp:
                continue
            d = (j - jp) % 5
            if d == 0:
                continue
            if c[j] == c[jp]:
                eqs.append((d, p[j], p[jp]))
            else:
                neq += 1
    return eqs, neq


CAP = 2000000


def count_completions(known: dict[int, int], cap: int = CAP) -> int:
    """Order-5 permutations (type 5^5 1^4) agreeing with the pinned points.

    Counts from the pinned VALUES only, ignoring the residual offset relations
    the union-find also knows, so it is an upper bound on the true residual."""
    g = [-1] * M
    used = [False] * M
    for a, b in known.items():
        g[a], used[b] = b, True
    unknown = [a for a in range(M) if g[a] == -1]

    def cycle_ok(full: list[int]) -> bool:
        seen = [False] * M
        for s in range(M):
            if seen[s]:
                continue
            n, x = 0, s
            while not seen[x]:
                seen[x] = True
                x = full[x]
                n += 1
            if n not in (1, 5):
                return False
        return True

    # chain bookkeeping so a bad cycle length is rejected at assignment time
    # rather than at the leaf -- without this the search is (29-P)! wide
    end_of = {}  # chain start -> chain end
    start_of = {}  # chain end -> chain start
    length = {}  # chain start -> number of edges
    for a in range(M):
        end_of[a], start_of[a], length[a] = a, a, 0
    for a, b in known.items():
        sa, eb = start_of[a], end_of[b]
        if sa == b:  # closes a cycle
            continue
        length[sa] = length[sa] + length[b] + 1
        end_of[sa], start_of[eb] = eb, sa

    total = 0

    def rec(i: int) -> None:
        nonlocal total
        if total >= cap:
            return
        if i == len(unknown):
            if cycle_ok(g):
                total += 1
            return
        a = unknown[i]
        sa = start_of[a]
        for b in range(M):
            if used[b]:
                continue
            eb = end_of[b]
            if b == sa:  # closing this chain into a cycle
                if length[sa] + 1 not in (1, 5):
                    continue
            elif length[sa] + length[b] + 1 > 4:
                continue
            saved = (end_of[sa], start_of[eb], length[sa])
            used[b], g[a] = True, b
            if b != sa:
                length[sa] += length[b] + 1
                end_of[sa], start_of[eb] = eb, sa
            rec(i + 1)
            if b != sa:
                end_of[sa], start_of[eb], length[sa] = saved
            g[a], used[b] = -1, False
            if total >= cap:
                return

    rec(0)
    return total


def solve(words: list[int], pt, ct, true_g) -> dict:
    u = CycleUnion(M)
    neq = 0
    n_eq = 0
    runes = 0
    for w in words:
        p, c = pt[w], ct[w]
        runes += len(p)
        eqs, nq = word_constraints(p, c)
        neq += nq
        for d, a, b in eqs:
            n_eq += 1
            # the planted key makes every constraint checkable
            assert ppow(true_g, d)[a] == b, "derived a false constraint"
            if a == b:
                u.note_fixed(a)
            else:
                u.union(a, b, d)
    known = u.known_g()
    for a, ga in known.items():
        assert true_g[a] == ga, "resolution disagrees with the planted g"
    return {
        "runes": runes,
        "equalities": n_eq,
        "inequalities": neq,
        "pinned": len(known),
        "known": known,
        "contradiction": u.contradiction,
    }


def main() -> None:
    ref = json.loads(REF.read_text())
    pt, ct = ref["plaintext_words"], ref["ciphertext_words"]
    true_g = np.array(ref["g"])
    n = len(pt)
    print(f"planted corpus: {n} words, {sum(len(w) for w in pt)} runes")
    print(
        f"true g: {(true_g != np.arange(M)).sum()} moving points, "
        f"{(true_g == np.arange(M)).sum()} fixed\n"
    )

    rng = random.Random(20260818)
    print("known words |  runes | equalities | inequalities | g points pinned /29")
    for k in (5, 10, 25, 50, 100, 200, 400, 800, 1600, n):
        trials = []
        for _ in range(5 if k < n else 1):
            words = rng.sample(range(n), k) if k < n else list(range(n))
            trials.append(solve(words, pt, ct, true_g))

        def avg(key: str, trials=trials) -> float:
            return sum(t[key] for t in trials) / len(trials)

        print(
            f"{k:11} | {avg('runes'):6.0f} | {avg('equalities'):10.1f} | "
            f"{avg('inequalities'):12.0f} | {avg('pinned'):5.1f}"
        )

    print("\nPer-word yield and the implied budget:")
    full = solve(list(range(n)), pt, ct, true_g)
    rate = full["equalities"] / full["runes"]
    print(
        f"  {rate:.4f} equality constraints per crib rune ({1 / rate:.0f} runes each)"
    )
    print(f"  whole corpus as a crib pins {full['pinned']}/29 points of g")
    print(f"  inequalities available but NOT propagated: {full['inequalities']:,}")

    print("\nresidual g candidates once the crib is spent:")
    for k in (100, 200, 300, 350, 400, 500, 800, 1600, n):
        words = rng.sample(range(n), k) if k < n else list(range(n))
        r = solve(words, pt, ct, true_g)
        c = count_completions(r["known"])
        shown = f"{c:,}" if c < CAP else f">{CAP:,}"
        print(
            f"  {k:5} words ({r['runes']:6} runes): {r['pinned']:2}/29 pinned "
            f"-> {shown} order-5 completions"
        )


if __name__ == "__main__":
    main()
