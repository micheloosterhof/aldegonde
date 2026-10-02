# ABOUTME: Tests whether the separators' DOT COUNTS drive the key, a visible state variable
# ABOUTME: the word-state sweep never included because it only ever counted words.
"""The separators are not all one dot, and nobody has tried using the others.

`rotor-machine-compact-state.md` sweeps thirteen word-level state variables -- word
index, cumulative rune count, section, line, sentence, the word's own length -- and finds
none that indexes the alphabet. Every one of them counts something the text makes
obvious. None of them counts DOTS.

The Liber Primus separates words with groups of dots, and the transcription preserves the
count: 2,718 single dots, but also 136 fours, 25 thirteens, four threes and two tens.
`marks-are-not-one-glyph` records that the four-dot and thirteen-dot marks behave
oppositely on an unrelated statistic, so the count carries information.

A dot group is a natural hand instruction: advance the alphabet by as many steps as
there are dots. That state is

    S_w = sum of the dot counts of every separator before word w

which is the word index perturbed by 734 extra steps spread over 167 marks. It is close
enough to the plain word counter that a test of `w` would see a diluted version of it,
and far enough that the dilution matters -- which is exactly the shape of a near miss.
`word_state_sweep.py` reports `w` at nIoC 1.018 and `A+w` at 1.033, its two best cells.

The test is the one that framework uses: if a state fully indexes the alphabet, two runes
sharing (state, phase) share an alphabet and coincide at the plaintext rate, about 1.74
normalised, rather than at 1.0.

    python dot_count_clock.py [--periods 120] [--control]
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

DATA = ROOT / "data" / "page0-56.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
M = 29
WRAP = "/\n"
DOTS = {chr(0x2460 + i): i + 1 for i in range(20)}  # circled 1..20 are dot groups


def load() -> tuple[list[int], list[int], list[int], list[int]]:
    """(stream, word id, within-word position, dot count of the separator AFTER each word)."""
    text = DATA.read_text()
    sections = [s for s in text.split("$") if RUNE.search(s)][:10]
    stream: list[int] = []
    wid: list[int] = []
    pos: list[int] = []
    dots: list[int] = []
    w, j = 0, 0
    for s in sections:
        started = False
        for ch in s:
            if RUNE.match(ch):
                stream.append(IDX[ch])
                wid.append(w)
                pos.append(j)
                j += 1
                started = True
            elif ch in WRAP:
                continue
            elif started and ch in c3301.WORD_BOUNDARY:
                dots.append(DOTS.get(ch, 1))
                w += 1
                j = 0
                started = False
        if started:
            dots.append(1)
            w += 1
            j = 0
    while len(dots) < w + 1:
        dots.append(1)
    return stream, wid, pos, dots


def states(wid: list[int], dots: list[int]) -> dict[str, list[int]]:
    """Candidate clocks, one value per rune."""
    cum = [0]
    for d in dots:
        cum.append(cum[-1] + d)
    marked = [0]
    for d in dots:
        marked.append(marked[-1] + (1 if d == 1 else 2))
    extra = [0]
    for d in dots:
        extra.append(extra[-1] + (d - 1))
    return {
        "dot count": [cum[w] for w in wid],
        "extra dots only": [extra[w] for w in wid],
        "marked words (1 or 2)": [marked[w] for w in wid],
        "word index (control)": list(wid),
    }


def pooled_ioc(stream: list[int], keys: list[tuple[int, int]]) -> tuple[float, int]:
    """Normalised IoC pooled over buckets, and the pair count."""
    buckets: dict[tuple[int, int], collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for r, k in zip(stream, keys):
        buckets[k][r] += 1
    hits = pairs = 0
    for c in buckets.values():
        n = sum(c.values())
        if n < 2:
            continue
        pairs += n * (n - 1) // 2
        hits += sum(v * (v - 1) // 2 for v in c.values())
    return (M * hits / pairs if pairs else 0.0), pairs


def scan(stream, pos, st, periods):
    best = []
    for p in range(2, periods + 1):
        for phase in (True, False):
            keys = [(s % p, (i % 5) if phase else 0) for s, i in zip(st, pos)]
            ioc, pairs = pooled_ioc(stream, keys)
            if pairs < 3000:
                continue
            best.append((ioc, p, phase, pairs))
    best.sort(reverse=True)
    return best


def main() -> None:
    periods = 120
    for i, a in enumerate(sys.argv):
        if a == "--periods" and i + 1 < len(sys.argv):
            periods = int(sys.argv[i + 1])

    stream, wid, pos, dots = load()
    counts = collections.Counter(dots)
    print(f"{len(stream):,} runes, {max(wid) + 1:,} words")
    print(f"separator dot counts: {sorted(counts.items())}")
    print(
        f"total dots {sum(dots):,} against {len(dots):,} words "
        f"({sum(dots) - len(dots):,} extra steps)\n"
    )

    if "--control" in sys.argv:
        import random  # noqa: PLC0415

        from lp_plaintext_register import corpus  # noqa: PLC0415

        rng = random.Random(5)
        words = corpus()
        st_all = states(wid, dots)["dot count"]
        period = 37
        alph = [rng.sample(range(M), M) for _ in range(period * 5)]
        cs, cp, cst = [], [], []
        for k, w in enumerate(wid):
            word = words[w % len(words)]
            i = pos[k]
            if i >= len(word):
                continue
            a = alph[(st_all[k] % period) * 5 + i % 5]
            cs.append(a[word[i]])
            cp.append(i)
            cst.append(st_all[k])
        got = scan(cs, cp, cst, periods)[0]
        print(
            f"PLANTED dot clock at period {period}: best nIoC {got[0]:.3f} "
            f"at period {got[1]}"
        )
        return

    # empirical null: the same scan on a shuffled stream, which carries no state
    # dependence but the same unigrams and the same bucket sizes. A binomial SE on
    # pooled coincidences is not valid here -- the pairs share runes.
    import random  # noqa: PLC0415

    rng = random.Random(3301)
    nulls = []
    for _ in range(12):
        sh = stream[:]
        rng.shuffle(sh)
        nulls.append(scan(sh, pos, list(wid), periods)[0][0])
    mu = sum(nulls) / len(nulls)
    sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
    print(f"surrogate scan maximum: {mu:.4f} +- {sd:.4f} over {len(nulls)} shuffles\n")

    print(
        f"{'state':<24}{'best nIoC':>11}{'z vs surrogate':>16}{'period':>8}{'phase':>7}"
    )
    for name, st in states(wid, dots).items():
        ioc, p, phase, _pairs = scan(stream, pos, st, periods)[0]
        print(f"{name:<24}{ioc:>11.3f}{(ioc - mu) / sd:>+16.2f}{p:>8}{str(phase):>7}")
    print(
        "\nA state that fully indexes the alphabet gives nIoC 1.74 by construction"
        "\n(the LP's own plaintext coincidence), and the planted control above reads"
        "\n2.64. These are the best cells of "
        f"{(periods - 1) * 2} per state, so the comparison that matters is"
        "\nthe effect size, not the significance."
    )


if __name__ == "__main__":
    main()
