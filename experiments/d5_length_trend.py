# ABOUTME: Measures the d5 echo against word length and simulates what the separator-loss
# ABOUTME: merge model predicts, showing the trend does not discriminate the two readings.
"""Does the d5 echo weaken in long words, and would that mean anything?

`two-rune-deficit.md` proposed this as the test that would separate a transcriptional
explanation of the 2-rune deficit from a register one: a merged word carries an
internal base change, so a within-word d5 pair spanning it should see two alphabets
and lose the echo. Merged words being the longer ones, the echo should weaken with
length.

The first half works. The body's echo does rise with word length, 1.15x chance at
lengths 6-7 to 1.81x at 10+, trend z = +1.68 over 2,073 pairs, where the author's own
plaintext shows none.

The second half does not. Simulating the merge model directly -- 280 selective merges
on the LP's own word-length distribution, with the author's measured d5 echo inside
each original segment and chance across every seam -- gives a median trend of z = -0.23
and reaches z > 1.96 in 2% of runs. Merges put a diluted seam into words of EVERY
length, and the larger pair counts of long merged words cancel the higher per-pair
dilution of short ones.

So the gradient is real-ish and worth recording, and it is not evidence about
separator loss in either direction.

    python d5_length_trend.py [--runs 40]
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29


def body_words() -> list[list[int]]:
    stream, wid = load_clean()
    out: list[list[int]] = []
    cur: list[int] = []
    last = wid[0]
    for r, w in zip(stream, wid):
        if w != last:
            out.append(cur)
            cur = []
            last = w
        cur.append(r)
    out.append(cur)
    return out


def trend_z(words: list[list[int]]) -> float:
    data = [
        (len(w), 1 if w[i] == w[i + 5] else 0) for w in words for i in range(len(w) - 5)
    ]
    n = len(data)
    if n < 2:
        return 0.0
    mx = sum(d[0] for d in data) / n
    my = sum(d[1] for d in data) / n
    sxy = sum((x - mx) * (y - my) for x, y in data)
    sxx = sum((x - mx) ** 2 for x, _ in data)
    syy = sum((y - my) ** 2 for _, y in data)
    return (sxy / math.sqrt(sxx * syy)) * math.sqrt(n - 1) if sxx * syy else 0.0


def echo_of(words: list[list[int]]) -> float:
    h = p = 0
    for w in words:
        for i in range(len(w) - 5):
            p += 1
            h += w[i] == w[i + 5]
    return (h / p) * M if p else 0.0


def simulate(rng: random.Random, lens: list[int], echo: float, merges: int):
    """Ciphertext words carrying `echo` inside each original segment, chance across seams."""
    seq = [[rng.randrange(M) for _ in range(rng.choice(lens))] for _ in range(3208)]
    segs = [[len(x)] for x in seq]
    done = guard = 0
    while done < merges and guard < 20 * merges:
        guard += 1
        i = rng.randrange(len(seq) - 1)
        if not (len(seq[i]) == 2 or len(seq[i + 1]) == 2):
            continue
        segs[i] = segs[i] + segs[i + 1]
        seq[i] = seq[i] + seq[i + 1]
        del seq[i + 1], segs[i + 1]
        done += 1
    for w, sg in zip(seq, segs):
        bounds, t = [], 0
        for x in sg:
            t += x
            bounds.append(t)
        for i in range(len(w) - 5):
            if (
                all(not (i < b <= i + 5) for b in bounds[:-1])
                and rng.random() < echo / M
            ):
                w[i + 5] = w[i]
    return seq


def main() -> None:
    runs = 40
    for i, a in enumerate(sys.argv):
        if a == "--runs" and i + 1 < len(sys.argv):
            runs = int(sys.argv[i + 1])

    body = body_words()
    plain = corpus()
    echo = echo_of(plain)
    print(f"plaintext d5 echo {echo:.2f}x chance\n")
    print(f"{'corpus':<16}{'lengths':>9}{'pairs':>7}{'x chance':>10}")
    for label, words in (("body", body), ("LP plaintext", plain)):
        for lo, hi, nm in ((6, 7, "6-7"), (8, 9, "8-9"), (10, 99, "10+")):
            sel = [w for w in words if lo <= len(w) <= hi]
            h = p = 0
            for w in sel:
                for i in range(len(w) - 5):
                    p += 1
                    h += w[i] == w[i + 5]
            if p >= 10:
                print(f"{label:<16}{nm:>9}{p:>7}{(h / p) * M:>10.2f}")
    print(
        f"\ntrend of match against length: body {trend_z(body):+.2f}, "
        f"plaintext {trend_z(plain):+.2f}"
    )

    rng = random.Random(3301)
    lens = [len(w) for w in plain]
    zs = sorted(trend_z(simulate(rng, lens, echo, 280)) for _ in range(runs))
    hits = sum(1 for z in zs if z > 1.96) / len(zs)
    print(
        f"\nmerge model, {runs} runs: median {zs[len(zs) // 2]:+.2f}, "
        f"range {zs[0]:+.2f} to {zs[-1]:+.2f}, z>1.96 in {hits:.0%}"
    )
    print("So the trend does not discriminate separator loss; the test is retracted.")


if __name__ == "__main__":
    main()
