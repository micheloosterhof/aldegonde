# ABOUTME: Runs the standing LP measurements over a surrogate corpus that keeps
# ABOUTME: every boundary and mark but randomises the runes, to expose artifacts.
"""Which of our measurements fire on text that provably has nothing in it?

Every statistic in this repo is quoted against some null. When the null is
wrong the statistic manufactures signal, and this project has produced several:
a plain shuffle made the corpus look underdispersed at z = -5.7
(`cross-product-sum-flat.md`), a naive standard error turned a p = 0.03 section
effect into z = +53, a linearised model prediction created the d4/d6 "puzzle"
(`d4_d6_prediction.py`), and a seam tap read z = +1.33 until a random control
showed that was the noise floor (`word_key_tap_battery.py`).

The common fix is a negative control: run the identical pipeline on a corpus
that carries no cipher structure and check the measurement returns nothing.

The surrogate here keeps the real text's word boundaries, sentence marks, line
wraps and page breaks EXACTLY, and replaces only the rune values, drawn with
`c3301.low_doublet_null()` so the observed doublet rate is preserved too. So it
holds fixed everything the layout and the doublet constraint supply, and
removes everything else. Any measurement that separates the real corpus from
this surrogate is measuring cipher structure; any that does not, is not.

Two things this cannot test, because rune shuffling leaves them untouched:
word-length statistics (the short-word deficit, sentence-final lengths) and
anything computed from boundaries alone. Those need a surrogate that shuffles
the length sequence instead — the approach `within_word_phase_profile.py`
already uses.

Reported per measurement: the real value, the surrogate mean and sd, and z.
A large |z| means the measurement discriminates. A z near zero on a claim the
repo treats as a finding is the thing to look at.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import Counter
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = "-.%&$"
N_RUNES = 29
DRAWS = 200
SEED = 3301


def load() -> tuple[list[int], list[list[int]], list[list[int]]]:
    """Rune stream, words, and lines, from sections 0-9."""
    text = "$".join(CORPUS.read_text().split("$")[:10])
    idx = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
    stream: list[int] = []
    words: list[list[int]] = []
    lines: list[list[int]] = []
    cur: list[int] = []
    line: list[int] = []
    for ch in text:
        if RUNE.match(ch):
            stream.append(idx[ch])
            cur.append(idx[ch])
            line.append(idx[ch])
        elif ch in BOUNDARY:
            if cur:
                words.append(cur)
                cur = []
        elif ch in "/\n":
            if line:
                lines.append(line)
                line = []
    if cur:
        words.append(cur)
    if line:
        lines.append(line)
    return stream, words, lines


def recut(stream: list[int], words: list[list[int]], lines: list[list[int]]):
    """Re-impose the real word and line shapes on a new rune stream."""
    out_w, out_l, i = [], [], 0
    for w in words:
        out_w.append(stream[i:i + len(w)])
        i += len(w)
    i = 0
    for line in lines:
        out_l.append(stream[i:i + len(line)])
        i += len(line)
    return out_w, out_l


def measure(stream, words, lines) -> dict[str, float]:
    """The standing measurements, all on one corpus."""
    n = len(stream)
    counts = Counter(stream)
    ioc = sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) * N_RUNES

    doublets = sum(1 for i in range(n - 1) if stream[i] == stream[i + 1]) / (n - 1)

    within = {}
    for d in (1, 2, 3, 4, 5, 6):
        m = e = 0
        for w in words:
            for i in range(len(w) - d):
                e += 1
                m += w[i] == w[i + d]
        within[d] = m / e if e else 0.0

    # cross-word distance 5: pairs 5 apart that straddle a boundary
    starts, pos = [], 0
    for w in words:
        starts.append(pos)
        pos += len(w)
    wid = [0] * n
    for k, w in enumerate(words):
        for j in range(len(w)):
            wid[starts[k] + j] = k
    cm = ce = 0
    for i in range(n - 5):
        if wid[i] != wid[i + 5]:
            ce += 1
            cm += stream[i] == stream[i + 5]
    cross5 = cm / ce if ce else 0.0

    match5 = [stream[i] == stream[i + 5] for i in range(n - 5)]
    pair1 = sum(1 for i in range(len(match5) - 1) if match5[i] and match5[i + 1])
    pair4 = sum(1 for i in range(len(match5) - 4) if match5[i] and match5[i + 4])

    seam = sum(1 for k in range(len(words) - 1) if words[k][-1] == words[k + 1][0])

    first = Counter(line[0] for line in lines if line)
    exp = len(lines) / N_RUNES
    chi2 = sum((first.get(r, 0) - exp) ** 2 / exp for r in range(N_RUNES))

    three = [tuple(w) for w in words if len(w) == 3]
    full3 = sum(v * (v - 1) // 2 for v in Counter(three).values())

    return {
        "unigram IoC x29": ioc,
        "doublet rate": doublets,
        "within-word d1": within[1],
        "within-word d4": within[4],
        "within-word d5": within[5],
        "within-word d6": within[6],
        "cross-word d5": cross5,
        "lag5 pairs sep 1": float(pair1),
        "lag5 pairs sep 4": float(pair4),
        "seam doublets": float(seam),
        "line-initial chi2": chi2,
        "3-rune full agree": float(full3),
    }


def main() -> None:
    rng = random.Random(SEED)
    stream, words, lines = load()
    print(f"clean corpus: {len(stream)} runes, {len(words)} words, {len(lines)} lines")
    print("surrogate: same boundaries, marks and line shapes; runes redrawn at the")
    print(f"observed doublet rate ({DRAWS} draws)\n")

    real = measure(stream, words, lines)
    model = c3301.low_doublet_null()
    draws: list[dict[str, float]] = []
    for _ in range(DRAWS):
        surr = list(model(stream, random.Random(rng.randrange(2**32))))
        sw, sl = recut(surr, words, lines)
        draws.append(measure(surr, sw, sl))

    print(f"{'measurement':>22}{'real':>12}{'surrogate':>12}{'sd':>10}{'z':>9}")
    for key in real:
        vals = [d[key] for d in draws]
        mu, sd = statistics.mean(vals), statistics.pstdev(vals)
        z = (real[key] - mu) / sd if sd else float("nan")
        flag = "" if abs(z) >= 2 or sd == 0 else "   <- does not discriminate"
        print(f"{key:>22}{real[key]:>12.4f}{mu:>12.4f}{sd:>10.4f}{z:>+9.2f}{flag}")

    print("\nA measurement with |z| < 2 here does not separate the real corpus from")
    print("text with no cipher structure, once boundaries and doublets are held fixed.")


if __name__ == "__main__":
    main()
