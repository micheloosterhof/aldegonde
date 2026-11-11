# ABOUTME: Tests keyed and content rules for null positions: under a perfect preventer with
# ABOUTME: inserted nulls, the rule's null positions must touch every one of the 86 doublets.
"""Does any keyed rule put a null beside every doublet?

`doublets-are-new-adjacencies.md`: if the preventer is perfect and the 86 doublets were
made by nulls inserted afterwards, every doublet has a null as one of its two runes. A
rule that says where the nulls are is therefore tested exactly: it covers all 86, or it
is wrong. A wrong rule that touches a share t of the adjacent pairs covers all 86 with
probability t^86, about 1e-60 at the t = 0.19 the doublet count implies.

`new_adjacency_probes.py` tried 288 fixed positional rules. This is the keyed family: a
reader who must remove the nulls needs a rule he can compute from a key or from the text.

  shifted sets     position i is a null when i + c is prime (or semiprime), every shift c
  residues         i = r mod m, every m to 60 and every r
  keyed residues   G(i + c) = r mod m for a number sequence G, every m to 30, r, start c
  keyed gaps       the nulls are spaced by gaps g = (G(n) mod m) + 1, from start term c
  content          the null is the rune after (or before) a member of a rune set X; the
                   smallest X that covers every doublet, by exact minimum vertex cover

Positions are counted in runes or in runes and separators, from the start of the body or
of each section or page.

Each rule is scored by the binomial tail of its cover given the share of ALL pairs it
touches. The control builds a strict no-repeat random stream of the body's length,
inserts random nulls where a keyed-gap rule says, and must get that rule back at full
cover.

    python experiments/keyed_null_cover.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
from slip_tolerant_keystream import CONSTANT_DIGITS, constant_digits  # noqa: E402

from aldegonde.maths import phi_func, primes  # noqa: E402

M = 29
SEED = 20261114
SHIFTS = 2_000_000
STARTS = 1000
RESIDUE_MODULI = range(2, 61)
KEYED_MODULI = range(2, 31)
GAP_MODULI = range(4, 31)
MAX_TOUCH = (
    0.75  # a rule touching more of the pairs than this cannot be told from chance
)


def log_tail(covered: int, total: int, t: float) -> float:
    """log10 of P(X >= covered) for X ~ Binomial(total, t)."""
    if t <= 0:
        return 0.0 if covered == 0 else -math.inf
    if t >= 1:
        return 0.0
    terms = [
        math.lgamma(total + 1)
        - math.lgamma(k + 1)
        - math.lgamma(total - k + 1)
        + k * math.log(t)
        + (total - k) * math.log(1 - t)
        for k in range(covered, total + 1)
    ]
    top = max(terms)
    return (top + math.log(sum(math.exp(x - top) for x in terms))) / math.log(10)


def index_rules(tok) -> dict[str, np.ndarray]:
    n = len(tok.stream)
    word = np.array(tok.word)
    runes = np.arange(n)
    with_sep = runes + word

    def restart(label, idx):
        out = np.zeros(n, dtype=np.int64)
        start = 0
        for i in range(n):
            if i and label[i] != label[i - 1]:
                start = idx[i]
            out[i] = idx[i] - start
        return out

    out = {"runes, body": runes, "runes+separators, body": with_sep}
    for name, label in (
        ("section", np.array(tok.section)),
        ("page", np.array(tok.page)),
    ):
        out[f"runes, {name}"] = restart(label, runes)
        out[f"runes+separators, {name}"] = restart(label, with_sep)
    return out


def raw_sequences(count: int) -> dict[str, np.ndarray]:
    """Number sequences as integers (not residues), `count` terms each."""
    p = np.array(primes(count * 14)[: count + 1], dtype=np.int64)
    n = np.arange(1, count + 1, dtype=np.int64)
    fib = [1, 1]
    while len(fib) < count:
        fib.append((fib[-1] + fib[-2]) % (2**40))
    out = {
        "n": n,
        "prime(n)": p[:count],
        "prime gap": np.diff(p),
        "totient(n)": np.array([phi_func(int(i)) for i in n], dtype=np.int64),
        "n^2": n * n,
        "triangular": n * (n + 1) // 2,
        "fibonacci": np.array(fib[:count], dtype=np.int64),
        "3301*n": 3301 * n,
    }
    for name in CONSTANT_DIGITS:
        out[f"{name}, base-29 digits"] = constant_digits(name, count)
    return out


class Cover:
    """Scores rules against one set of doublets and keeps the best."""

    def __init__(self, n: int, doublets: np.ndarray) -> None:
        self.n = n
        self.d = doublets  # index of the second rune of each doublet
        self.total = len(doublets)
        self.best = (0.0, "", 0, 0.0)  # log10 tail, rule, covered, touch share
        self.full: list[tuple[str, float]] = []
        self.count = 0

    def offer(self, name: str, covered: int, touch: float) -> None:
        self.count += 1
        if touch > MAX_TOUCH:
            return
        lt = log_tail(covered, self.total, touch)
        if lt < self.best[0]:
            self.best = (lt, name, covered, touch)
        if covered == self.total:
            self.full.append((name, touch))

    def rule(self, name: str, is_null: np.ndarray) -> None:
        """One rule given as a boolean per rune."""
        touch = is_null[1:] | is_null[:-1]
        self.offer(name, int(touch[self.d - 1].sum()), float(touch.mean()))

    def shifted(
        self, name: str, member: np.ndarray, idx: np.ndarray, shifts: int
    ) -> None:
        """Every rule 'rune i is a null when member[idx[i] + c]', c = 0..shifts-1.

        The cover is counted for every shift; the forty best are scored exactly, since
        the binomial tail needs the share of all pairs the rule touches."""
        cov = np.zeros(shifts, dtype=np.int64)
        for i in self.d:
            a, b = int(idx[i - 1]), int(idx[i])
            cov += member[a : a + shifts] | member[b : b + shifts]
        order = np.argsort(-cov)[:40]
        self.count += shifts - len(order)
        for c in order:
            is_null = member[idx + int(c)]
            exact = is_null[1:] | is_null[:-1]
            self.offer(f"{name}, shift {int(c)}", int(cov[c]), float(exact.mean()))


def keyed(cover: Cover, seqs, idx_map) -> None:
    for gname, g in seqs.items():
        for m in KEYED_MODULI:
            res = g % m
            for r in range(m):
                member = res == r
                if not member.any():
                    continue
                for iname, idx in idx_map.items():
                    cover.shifted(
                        f"{gname} = {r} mod {m}; {iname}", member, idx, STARTS
                    )


def gaps(cover: Cover, seqs, n: int, idx_map) -> None:
    """Null positions are partial sums of g = (G mod m) + 1 from start term c."""
    for gname, g in seqs.items():
        for m in GAP_MODULI:
            step = g % m + 1
            if step.mean() < 3:
                continue
            for c in range(0, STARTS, 1):
                pos = np.cumsum(step[c:]) - 1
                pos = pos[pos < 2 * n]
                member = np.zeros(2 * n, dtype=bool)
                member[pos] = True
                for iname, idx in idx_map.items():
                    if not iname.endswith("body"):
                        continue
                    cover.rule(
                        f"gaps ({gname} mod {m}) + 1 from term {c}; {iname}",
                        member[idx],
                    )


def minimum_cover(edges: list[tuple[int, int]]) -> int:
    """Size of the smallest rune set meeting every (a, b) clause, a == b allowed."""
    forced = {a for a, b in edges if a == b}
    rest = [(a, b) for a, b in edges if a != b and a not in forced and b not in forced]
    best = [len(forced) + len({x for e in rest for x in e})]

    def solve(chosen: int, remaining: list[tuple[int, int]]) -> None:
        if chosen >= best[0]:
            return
        if not remaining:
            best[0] = chosen
            return
        a, b = remaining[0]
        for pick in (a, b):
            solve(chosen + 1, [e for e in remaining if pick not in e])

    solve(len(forced), rest)
    return best[0]


def content(stream: np.ndarray, doublets: np.ndarray) -> None:
    print("content rules: the smallest rune set X that covers every doublet")
    share = len(doublets) / (len(stream) - 1) * M / 2
    for label, first, second in (
        ("the null is the rune AFTER a member of X", -1, -2),
        ("the null is the rune BEFORE a member of X", 1, 0),
    ):
        edges = []
        for i in doublets:
            # the null is rune i (its marker is at i + first) or rune i - 1 (at i + second)
            a = int(stream[i + first]) if 0 <= i + first < len(stream) else -1
            b = int(stream[i + second]) if 0 <= i + second < len(stream) else -1
            edges.append((a, b))
        size = minimum_cover(edges)
        print(
            f"  {label}: |X| >= {size}, so nulls are at least {size / M:.2f} of the runes "
            f"against the {share:.3f} the doublets imply"
        )
    print()


def planted(n: int, rng: random.Random, member: np.ndarray) -> np.ndarray:
    """A strict no-repeat random stream with random nulls at the rule's positions."""
    out: list[int] = []
    prev = -1
    for i in range(n):
        if member[i]:
            out.append(rng.randrange(M))
            continue
        r = rng.randrange(M)
        base_prev = prev
        while r == base_prev:
            r = rng.randrange(M)
        out.append(r)
        prev = r
    return np.array(out)


def run(stream: np.ndarray, idx_map, seqs, *, quick: bool) -> Cover:
    n = len(stream)
    doublets = np.flatnonzero(stream[1:] == stream[:-1]) + 1
    cover = Cover(n, doublets)
    if not quick:
        limit = SHIFTS + 2 * n + 10
        is_prime = np.zeros(limit, dtype=bool)
        is_prime[primes(limit)] = True
        small = np.flatnonzero(is_prime[: int(limit**0.5) + 1])
        semi = np.zeros(limit, dtype=bool)
        for p in small:
            q = np.flatnonzero(is_prime[p : limit // p + 1]) + p
            semi[p * q[p * q < limit]] = True
        for iname in ("runes, body", "runes+separators, body"):
            cover.shifted(f"i + c prime; {iname}", is_prime, idx_map[iname], SHIFTS)
            cover.shifted(f"i + c semiprime; {iname}", semi, idx_map[iname], SHIFTS)
        for m in RESIDUE_MODULI:
            for r in range(m):
                for iname, idx in idx_map.items():
                    cover.rule(f"i = {r} mod {m}; {iname}", idx % m == r)
        keyed(cover, seqs, idx_map)
    gaps(cover, seqs, n, idx_map)
    return cover


def main() -> None:
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    stream = np.array(tok.stream)
    n = len(stream)
    idx_map = index_rules(tok)
    seqs = raw_sequences(2 * n + STARTS + 10)

    # control
    g = seqs["pi, base-29 digits"]
    step = g % 20 + 1
    pos = np.cumsum(step[123:]) - 1
    member = np.zeros(2 * n, dtype=bool)
    member[pos[pos < 2 * n]] = True
    fake = planted(n, rng, member)
    ctrl = run(fake, {"runes, body": np.arange(n)}, seqs, quick=True)
    fd = int((fake[1:] == fake[:-1]).sum())
    control_ok = any(
        "pi, base-29 digits mod 20) + 1 from term 123" in name for name, _ in ctrl.full
    )
    print(
        f"control: nulls at gaps (pi digits mod 20) + 1 from term 123 in a no-repeat "
        f"stream: {fd} doublets; rules at full cover: {len(ctrl.full)} of {ctrl.count:,} "
        f"({'the planted rule among them' if control_ok else 'the planted rule is MISSING'}); "
        f"best tail 1e{ctrl.best[0]:.0f}\n"
    )

    doublets = np.flatnonzero(stream[1:] == stream[:-1]) + 1
    content(stream, doublets)
    cover = run(stream, idx_map, seqs, quick=False)
    lt, name, covered, touch = cover.best
    bonferroni = lt + math.log10(cover.count)
    print(f"the body: {cover.count:,} rules, {len(doublets)} doublets")
    print(
        f"  best rule: {name}: covers {covered} of {len(doublets)} while touching "
        f"{touch:.3f} of all pairs; tail 1e{lt:.1f}, times the rules 1e{bonferroni:.1f}"
    )
    print(
        f"  rules at full cover touching under {MAX_TOUCH} of the pairs: {len(cover.full)}"
    )
    if not control_ok:
        print("VERDICT: the control lost its planted rule; the negative means nothing.")
    elif cover.full or bonferroni < -3:
        print("VERDICT: a rule stands out. Strip its nulls and test the remainder.")
    else:
        print(
            "VERDICT: no keyed or content rule puts a null beside every doublet. Nulls "
            "inserted after a perfect preventer would have to be placed by a rule "
            "outside these families, or at random, which the reader could not undo."
        )


if __name__ == "__main__":
    main()
