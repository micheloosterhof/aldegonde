# ABOUTME: Tests whether the per-word alphabet is keyed by any simple function
# ABOUTME: of the preceding text, by conditioning word-pair agreement on that tap.
"""Is the per-word alphabet chosen by some function of what came before?

A word-level autokey picks word w's alphabet from a "tap" -- some function of
the preceding text. The last rune of the previous word is one candidate; so are
its rune sum mod 29, its product, its length, a running accumulator, and so on.

The test does not care which. Whatever the tap is, two words with the SAME tap
value get the SAME alphabet, and that has one observable consequence.

Compare two words at the same position k. The walk gives c_k = base_w(g^k(p_k)),
so if the bases are equal the ciphertext runes agree exactly when the plaintext
runes agree. Agreement therefore lifts from the flat 1/29 = 0.0345 to the
runeglish plaintext coincidence rate, about 0.06:

    alphabet keyed by the tap  ->  agree | tap matches  ~ 0.06
                                   agree | tap differs  ~ 0.0345
    not keyed by it            ->  both ~ 0.0345

Two properties make this worth running over a whole family:

  * It uses EVERY word pair, not only pairs that are the same word, so it is
    far more sensitive than an identical-word repeat census.
  * It degrades gracefully. If a tap is only PART of the key, matched-tap
    pairs still lift in proportion, so a flat result bounds the tap's share
    rather than merely failing to confirm it.

Power depends on how many classes a tap has: too few and it cannot select
among many alphabets, too many and there are no matched pairs left. The class
count and matched-pair count are reported so a null can be read correctly.

A random tap is included as a negative control, and the whole battery is
scanned, so per-tap significance is corrected for the number of taps tried.

Null: shuffle the tap values across words, preserving every marginal and
breaking only the association between a word and its tap.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import Counter, defaultdict
from math import prod
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = "①-.%&$"
N_RUNES = 29
MAX_POS = 5          # positions 0..4 carry almost all the mass
TRIALS = 1000
SEED = 3301
PLAINTEXT_RATE = 0.06


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


def build_taps(ws: list[tuple[int, ...]], rng: random.Random) -> dict[str, list[int | None]]:
    """Candidate keying functions of the preceding text, one value per word."""
    gp = [c3301.r2v(r) for r in c3301.CICADA_ALPHABET]
    running, starts = [], []
    total = 0
    for w in ws:
        running.append(total)
        starts.append(total)
        total += len(w)

    def prev(i: int) -> tuple[int, ...] | None:
        return ws[i - 1] if i >= 1 else None

    taps: dict[str, list[int | None]] = {
        "prev last rune": [p[-1] if (p := prev(i)) else None for i in range(len(ws))],
        "prev first rune": [p[0] if (p := prev(i)) else None for i in range(len(ws))],
        "prev sum mod 29": [sum(p) % N_RUNES if (p := prev(i)) else None
                            for i in range(len(ws))],
        "prev product mod 29": [prod(x + 1 for x in p) % N_RUNES if (p := prev(i))
                                else None for i in range(len(ws))],
        "prev GP sum mod 29": [sum(gp[x] for x in p) % N_RUNES if (p := prev(i))
                               else None for i in range(len(ws))],
        "prev GP product 29": [prod(gp[x] for x in p) % N_RUNES if (p := prev(i))
                               else None for i in range(len(ws))],
        "prev alt sum mod 29": [sum(x * (-1) ** j for j, x in enumerate(p)) % N_RUNES
                                if (p := prev(i)) else None for i in range(len(ws))],
        "prev length": [len(p) if (p := prev(i)) else None for i in range(len(ws))],
        "prev length mod 5": [len(p) % 5 if (p := prev(i)) else None
                              for i in range(len(ws))],
        "prev 2 words sum": [(sum(ws[i - 1]) + sum(ws[i - 2])) % N_RUNES if i >= 2
                             else None for i in range(len(ws))],
        "accumulated sum": [sum(sum(w) for w in ws[:i]) % N_RUNES if i >= 1 else None
                            for i in range(len(ws))],
        "rune offset mod 29": [starts[i] % N_RUNES if i >= 1 else None
                               for i in range(len(ws))],
        "word index mod 29": [i % N_RUNES if i >= 1 else None for i in range(len(ws))],
        "random (control)": [rng.randrange(N_RUNES) if i >= 1 else None
                             for i in range(len(ws))],
    }
    return taps


def agreement(ws: list[tuple[int, ...]], tap: list[int | None]) -> tuple[float, float, int]:
    """Agreement rate when the tap matches, when it differs, and matched pairs."""
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
    if not m_pairs or a_pairs == m_pairs:
        return float("nan"), float("nan"), m_pairs
    return m_agree / m_pairs, (a_agree - m_agree) / (a_pairs - m_pairs), m_pairs


def main() -> None:
    rng = random.Random(SEED)
    ws = words()
    taps = build_taps(ws, rng)
    predicted = PLAINTEXT_RATE - 1 / N_RUNES
    print(f"clean corpus: {len(ws)} words, positions 0-{MAX_POS - 1}")
    print(f"flat baseline 1/29 = {1 / N_RUNES:.4f}; a shared alphabet lifts "
          f"matched-tap agreement")
    print(f"to the runeglish plaintext rate ~{PLAINTEXT_RATE}, a gap of "
          f"{predicted:+.4f}\n")

    print(f"{'tap':>22}{'classes':>9}{'matched':>11}{'agree':>9}{'differs':>9}"
          f"{'gap':>9}{'sd':>8}{'z':>7}{'share':>8}")
    results = []
    for name, tap in taps.items():
        matched, other, m_pairs = agreement(ws, tap)
        classes = len({t for t in tap if t is not None})
        gap = matched - other

        defined = [t for t in tap if t is not None]
        null = []
        for _ in range(TRIALS):
            rng.shuffle(defined)
            it = iter(defined)
            m, o, _ = agreement(ws, [None if t is None else next(it) for t in tap])
            null.append(m - o)
        mu, sd = statistics.mean(null), statistics.pstdev(null)
        z = (gap - mu) / sd if sd else float("nan")
        share = (gap + 2 * sd) / predicted
        results.append((name, z))
        print(f"{name:>22}{classes:>9}{m_pairs:>11}{matched:>9.4f}{other:>9.4f}"
              f"{gap:>+9.4f}{sd:>8.4f}{z:>+7.2f}{share:>7.1%}")

    print("\nclasses = distinct tap values; matched = pairs sharing one.")
    print("share = the tap's maximum contribution to alphabet selection, from")
    print("the 2-sigma upper edge of the gap divided by the full-keying gap.")
    worst = max(results, key=lambda r: abs(r[1]))
    print(f"\n{len(taps)} taps scanned; largest |z| is {worst[0]} at "
          f"{worst[1]:+.2f}, which needs")
    print(f"|z| > {2.7:.1f} to clear the scan. A tap that keyed the alphabet "
          f"would sit at z ~ {predicted / 0.0003:.0f}.")


if __name__ == "__main__":
    main()
