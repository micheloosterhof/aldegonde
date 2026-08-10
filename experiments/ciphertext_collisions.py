#!/usr/bin/env python3
# ABOUTME: Finds repeated ciphertext substrings in LP 0-9 (state-returns) and
# ABOUTME: reports them as walk constraints on (g, sigma). The cross-word signal.
"""A long repeated ciphertext substring most likely means the same plaintext
under a returned alphabet state (like DJU-BEI). Each genuine state-return gives
base_{w1} = base_{w2}, i.e. the product of walk steps over [w1, w2) is identity:

    prod_{w=w1..w2-1}  g^((L_w - 1) mod 5) o sigma  =  identity

These cross-word equations are the only constraints on the (g, sigma) WIRING
(within-word coincidence fixes only ord(g)=5). We list repeats length>=5, tag
each with word/phase alignment, flag chance vs genuine, and emit the interval
arithmetic (sum(L-1) mod 5, sigma-count = #words in interval).

That arithmetic gives a free-group relation, NOT a filter on concrete
permutations: the real <g,sigma> has abelianization of order 1 or 2, so the
relation collapses into parity (see abelianization_check.py). The testable
content of a genuine repeat is the state return base_i == base_j itself.
"""

from __future__ import annotations

from collections import defaultdict

from experiments.within_word_position_decomposition import load_words

M = 29


def load_tagged() -> tuple[list[int], list[int], list[int], list[list[int]]]:
    """Return (stream, word_index_per_pos, within_word_phase_per_pos, words)."""
    words = load_words()
    stream, widx, phase = [], [], []
    for wi, w in enumerate(words):
        for j, r in enumerate(w):
            stream.append(r)
            widx.append(wi)
            phase.append(j % 5)
    return stream, widx, phase, words


def maximal_repeats(stream: list[int], kmin: int) -> list[tuple[int, list[int]]]:
    """Maximal repeated substrings of length >= kmin. Returns (length, [starts]).
    Seeds on kmin-grams, extends each equivalence class rightward maximally."""
    n = len(stream)
    seed: dict[tuple, list[int]] = defaultdict(list)
    for i in range(n - kmin + 1):
        seed[tuple(stream[i : i + kmin])].append(i)
    out = []
    seen_spans: set[tuple[int, int]] = set()
    for starts in seed.values():
        if len(starts) < 2:
            continue
        # extend the whole group rightward while all agree pairwise-with-first
        L = kmin
        while True:
            base_ends = [s + L for s in starts]
            if any(e >= n for e in base_ends):
                break
            vals = {stream[s + L] for s in starts}
            if len(vals) == 1:
                L += 1
            else:
                break
        # keep only the maximal, dedupe by covered span of the first occurrence
        span = (starts[0], starts[0] + L)
        if span in seen_spans:
            continue
        seen_spans.add(span)
        out.append((L, sorted(starts)))
    out.sort(key=lambda t: (-t[0], -len(t[1])))
    return out


def expected_by_chance(n: int, k: int) -> float:
    return n * n / (2 * M**k)


def main() -> None:
    stream, widx, phase, words = load_tagged()
    n = len(stream)
    print(f"ciphertext 0-9: {n} runes, {len(words)} words\n")

    kmin = 5
    repeats = maximal_repeats(stream, kmin)
    print(f"maximal repeated substrings (length >= {kmin}): {len(repeats)} classes")
    print(
        f"(expected by chance: k=5 ~{expected_by_chance(n, 5):.1f}, "
        f"k=6 ~{expected_by_chance(n, 6):.2f}, k=7 ~{expected_by_chance(n, 7):.3f})\n"
    )

    for L, starts in repeats:
        if L < 6 and len(starts) == 2:
            continue  # k=5 pairs are mostly chance; show only k>=6 or multi
        occ = []
        for s in starts:
            wtag = f"w{widx[s]}:ph{phase[s]}"
            occ.append(f"pos{s}({wtag})")
        chance = expected_by_chance(n, L)
        genuine = "GENUINE" if chance < 0.5 else "chance?"
        # word-boundary / phase alignment across occurrences
        phases = {phase[s] for s in starts}
        wordstart = all(phase[s] == 0 for s in starts)
        note = []
        if wordstart:
            note.append("all word-initial")
        if len(phases) == 1:
            note.append(f"same phase {phases.pop()}")
        print(
            f"  len {L} x{len(starts)} [{genuine}, ~{chance:.3g} exp] {' '.join(note)}"
        )
        print(f"      {'  '.join(occ)}")
        # state-return constraint for the first pair (if word-aligned)
        if len(starts) >= 2 and wordstart:
            w1, w2 = sorted((widx[starts[0]], widx[starts[1]]))
            interval = list(range(w1, w2))
            sig_count = len(interval)
            gpow = sum((len(words[w]) - 1) % 5 for w in interval) % 5
            print(
                f"      => base_w{w1} = base_w{w2}: sigma-count {sig_count}, "
                f"sum(L-1) mod5 = {gpow}  (prod of steps = id)"
            )
    print()

    # whole-word ciphertext repeats (a word's exact ciphertext recurring)
    wordkey: dict[tuple, list[int]] = defaultdict(list)
    for wi, w in enumerate(words):
        if len(w) >= 3:
            wordkey[tuple(w)].append(wi)
    dup = {k: v for k, v in wordkey.items() if len(v) >= 2}
    print(f"identical ciphertext WORDS (len>=3) recurring: {len(dup)} distinct")
    for w, wis in sorted(dup.items(), key=lambda t: -len(t[0]))[:10]:
        print(f"  len {len(w)} at words {wis}")


if __name__ == "__main__":
    main()
