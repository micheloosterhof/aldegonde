# ABOUTME: Tests whether a word's alphabet is keyed by the previous word's last
# ABOUTME: rune, by conditioning word-pair agreement on that seam rune matching.
"""Is the per-word alphabet an autokey on the previous word's last rune?

If the key for word w is a function of the last rune of word w-1, then two
words whose preceding rune is the same share an alphabet. That has a sharp,
directly observable consequence.

Compare two words at the SAME position k. The walk gives c_k = base_w(g^k(p_k)),
so if the two bases are equal the ciphertext runes agree exactly when the
plaintext runes agree. Agreement therefore jumps from the flat 1/29 = 0.0345
to the plaintext coincidence rate of runeglish, roughly 0.06.

So:

    base keyed by the seam rune  ->  agreement | seams match   ~ 0.06
                                     agreement | seams differ  ~ 0.0345
    base not keyed by it         ->  both ~ 0.0345

This is far more sensitive than the identical-word depth test. It uses every
pair of words rather than only pairs that happen to be the same word, and
conditioning on the seam concentrates the signal 29-fold. It also degrades
gracefully: if the seam rune is only PART of the key, matched-seam pairs still
show partial elevation, so the test bounds how much the seam can contribute.

Three taps are tried, so a null cannot be blamed on picking the wrong one:
the previous word's last rune (the proposal), its first rune, and the last
rune of the word two back.

Null: shuffle the tap runes across words, which preserves every marginal and
breaks only the association between a word and its tap.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = "-.%&$"
N_RUNES = 29
MAX_POS = 5          # positions 0..4 hold almost all the mass
TRIALS = 2000
SEED = 3301


def words() -> list[tuple[int, ...]]:
    text = "$".join(CORPUS.read_text().split("$")[:10])
    index: dict[str, int] = {}
    out: list[tuple[int, ...]] = []
    cur: list[int] = []
    for char in text:
        if RUNE.match(char):
            cur.append(index.setdefault(char, len(index)))
        elif char in BOUNDARY and cur:
            out.append(tuple(cur))
            cur = []
    if cur:
        out.append(tuple(cur))
    return out


def taps(ws: list[tuple[int, ...]], kind: str) -> list[int | None]:
    """The keying rune proposed for each word, or None where undefined."""
    out: list[int | None] = []
    for i, _ in enumerate(ws):
        if kind == "prev_last":
            out.append(ws[i - 1][-1] if i >= 1 else None)
        elif kind == "prev_first":
            out.append(ws[i - 1][0] if i >= 1 else None)
        else:  # two words back, last rune
            out.append(ws[i - 2][-1] if i >= 2 else None)
    return out


def agreement(ws: list[tuple[int, ...]], tap: list[int | None]) -> tuple[float, float]:
    """Position-agreement rate for pairs whose tap matches, and whose differs."""
    m_agree = m_pairs = a_agree = a_pairs = 0
    for k in range(MAX_POS):
        by_tap: dict[int, Counter[int]] = defaultdict(Counter)
        overall: Counter[int] = Counter()
        n = 0
        for w, t in zip(ws, tap):
            if len(w) <= k or t is None:
                continue
            by_tap[t][w[k]] += 1
            overall[w[k]] += 1
            n += 1
        a_agree += sum(v * (v - 1) // 2 for v in overall.values())
        a_pairs += n * (n - 1) // 2
        for counts in by_tap.values():
            size = sum(counts.values())
            m_agree += sum(v * (v - 1) // 2 for v in counts.values())
            m_pairs += size * (size - 1) // 2
    matched = m_agree / m_pairs
    other = (a_agree - m_agree) / (a_pairs - m_pairs)
    return matched, other


def main() -> None:
    rng = random.Random(SEED)
    ws = words()
    print(f"clean corpus: {len(ws)} words, positions 0-{MAX_POS - 1}")
    print(f"flat baseline 1/29 = {1 / N_RUNES:.4f}; a shared alphabet would lift")
    print("matched-tap agreement to the runeglish plaintext rate, about 0.06\n")

    print(f"{'tap':>12}{'matched':>10}{'differs':>10}{'lift':>9}"
          f"{'null lift':>12}{'sd':>8}{'z':>8}")
    for kind, label in (("prev_last", "prev last"), ("prev_first", "prev first"),
                        ("two_back", "two back")):
        tap = taps(ws, kind)
        matched, other = agreement(ws, tap)
        lift = matched - other

        defined = [t for t in tap if t is not None]
        null = []
        for _ in range(TRIALS):
            rng.shuffle(defined)
            it = iter(defined)
            shuffled = [None if t is None else next(it) for t in tap]
            m, o = agreement(ws, shuffled)
            null.append(m - o)
        mu, sd = statistics.mean(null), statistics.pstdev(null)
        z = (lift - mu) / sd if sd else float("nan")
        print(f"{label:>12}{matched:>10.4f}{other:>10.4f}{lift:>+9.4f}"
              f"{mu:>+12.4f}{sd:>8.4f}{z:>+8.2f}")

    predicted = 0.06 - 1 / N_RUNES
    tap = taps(ws, "prev_last")
    lift = (lambda m, o: m - o)(*agreement(ws, tap))
    defined = [t for t in tap if t is not None]
    null = []
    for _ in range(TRIALS):
        rng.shuffle(defined)
        it = iter(defined)
        m, o = agreement(ws, [None if t is None else next(it) for t in tap])
        null.append(m - o)
    sd = statistics.pstdev(null)
    print(f"\nfull seam keying predicts a lift of ~{predicted:+.4f} "
          f"(0.06 - {1 / N_RUNES:.4f}), which is")
    print(f"{predicted / sd:.0f} sigma away. Observed for the proposed tap: "
          f"{lift:+.4f}.")
    print(f"\nbound on partial keying: the lift is at most {lift + 2 * sd:+.4f} "
          f"at 2 sigma, so the seam")
    print(f"rune can determine at most {(lift + 2 * sd) / predicted:.1%} of the "
          "alphabet selection.")


if __name__ == "__main__":
    main()
