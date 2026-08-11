# ABOUTME: Generative test of the per-word period-5 mixed-alphabet hypothesis for
# ABOUTME: the unsolved Liber Primus: does it reproduce the full d1..d5 fingerprint?
"""Does a per-word period-5 mixed-alphabet cipher reproduce the LP fingerprint?

The corrected mechanism (shared alphabet at positions n and n+5, not a copy):
each word is enciphered by 5 mixed substitution alphabets cycling with period 5,
re-keyed per word. Prediction: positions 5 apart share an alphabet, so plaintext
d5 coincidences leak at the English rate; positions 1..4 apart use different
alphabets, so those coincidences are scrambled to chance; and because the key
varies per word, the columns are flat.

This generates English-like runeglish (order-2 Markov from the repo trigram
table), cuts it into words with the observed LP length distribution, enciphers
under several models, and measures the within-word coincidence rate at each
distance plus the column IoC. Target (unsolved corpus): unigram IoC 1.00,
within-word d1 0.66%, d5 4.9%, d2/3/4 ~3.4% (chance), columns flat.

Two cipher models are compared:
  positional : 5 fixed alphabets, phase = position mod 5 (no per-word reset)
  perword    : 5 fixed alphabets, phase re-randomized per word
  wordkey    : 5 fresh random alphabets per word
The doublet suppression is deliberately NOT modelled here -- if d1 comes out at
chance, that confirms it is a separate overlay, not part of the period-5 scheme.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict

from aldegonde import c3301

ALPH = c3301.CICADA_ALPHABET
M = 29
R2I = {r: i for i, r in enumerate(ALPH)}
SEED = 3301

# observed LP clean-corpus word-length distribution (length: count)
LEN_DIST = {
    1: 99,
    2: 465,
    3: 726,
    4: 514,
    5: 318,
    6: 252,
    7: 214,
    8: 159,
    9: 77,
    10: 51,
    11: 28,
    12: 18,
    13: 4,
    14: 3,
}


def load_trigram() -> dict[tuple[int, int], list[float]]:
    """Order-2 Markov transition weights from the runeglish trigram table."""
    trans: dict[tuple[int, int], list[float]] = defaultdict(lambda: [0.0] * M)
    with open("src/aldegonde/data/ngrams/runeglish/trigrams.txt") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2:
                continue
            tri, cnt = parts
            if len(tri) == 3 and all(ch in ALPH for ch in tri):
                a, b, c = (R2I[ch] for ch in tri)
                trans[(a, b)][c] += float(cnt)
    return trans


def gen_plaintext(trans, n: int, rng: random.Random) -> list[int]:
    """Generate n runeglish indices by sampling the order-2 Markov model."""
    keys = list(trans)
    a, b = rng.choice(keys)
    out = [a, b]
    for _ in range(n - 2):
        w = trans.get((a, b))
        if not w or sum(w) == 0:
            a, b = rng.choice(keys)
            w = trans[(a, b)]
        c = rng.choices(range(M), weights=w, k=1)[0]
        out.append(c)
        a, b = b, c
    return out


def cut_words(stream: list[int], rng: random.Random) -> list[list[int]]:
    """Cut a stream into words with the observed LP length distribution."""
    lengths = list(LEN_DIST)
    weights = [LEN_DIST[k] for k in lengths]
    words: list[list[int]] = []
    i = 0
    while i < len(stream):
        length = rng.choices(lengths, weights=weights, k=1)[0]
        if i + length > len(stream):
            break
        words.append(stream[i : i + length])
        i += length
    return words


def random_alphabet(rng: random.Random) -> list[int]:
    """A random mixed substitution alphabet (permutation of the 29 runes)."""
    perm = list(range(M))
    rng.shuffle(perm)
    return perm


def encipher(words, model: str, rng: random.Random) -> list[list[int]]:
    """Encipher words under a period-5 mixed-alphabet model."""
    fixed = [random_alphabet(rng) for _ in range(5)]
    out = []
    for w in words:
        if model == "positional":
            alphs, phase = fixed, 0
        elif model == "perword":
            alphs, phase = fixed, rng.randrange(5)
        elif model == "wordkey":
            alphs, phase = [random_alphabet(rng) for _ in range(5)], 0
        else:
            raise ValueError(model)
        out.append([alphs[(j + phase) % 5][w[j]] for j in range(len(w))])
    return out


def ioc(seq) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def measure(words) -> dict:
    """Unigram IoC, within-word d1..6 coincidence rate, and column IoCs."""
    stream = [x for w in words for x in w]
    rates = {}
    for d in range(1, 7):
        elig = match = 0
        for w in words:
            for i in range(len(w) - d):
                elig += 1
                if w[i] == w[i + d]:
                    match += 1
        rates[d] = match / elig if elig else 0.0
    cols = []
    for j in range(3):
        col = [w[j] for w in words if len(w) > j]
        cols.append(ioc(col))
    return {"uni_ioc": ioc(stream), "rates": rates, "cols": cols}


def show(label: str, m: dict) -> None:
    r = m["rates"]
    print(
        f"{label:<12} uniIoC={m['uni_ioc']:.3f}  "
        f"d1={r[1]:.4f} d2={r[2]:.4f} d3={r[3]:.4f} "
        f"d4={r[4]:.4f} d5={r[5]:.4f} d6={r[6]:.4f}  "
        f"cols={[round(c, 2) for c in m['cols']]}"
    )


def main() -> None:
    rng = random.Random(SEED)
    trans = load_trigram()
    stream = gen_plaintext(trans, 40000, rng)
    words = cut_words(stream, rng)
    print(f"generated {len(words)} words, {sum(len(w) for w in words)} runes\n")
    print(
        "TARGET (unsolved LP): uniIoC=1.00  d1=0.0066 d5=0.0492 "
        "d2/3/4~0.034 (chance)  cols flat (~1.0)\n"
    )
    show("PLAINTEXT", measure(words))
    for model in ("positional", "perword", "wordkey"):
        show(model, measure(encipher(words, model, rng)))


if __name__ == "__main__":
    main()
