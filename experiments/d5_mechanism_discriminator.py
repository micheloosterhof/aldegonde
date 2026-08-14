# ABOUTME: Tests whether the d5 excess is a plaintext echo or a manufactured repeat,
# ABOUTME: using cross-word d5 and the XY...XY digram-repeat rate.
"""Does d5 echo plaintext, or is the repeat manufactured?

Every model in this repo reads the within-word d5 excess as `g^0 = identity`, so
`c_j = c_{j+5} <=> p_j = p_{j+5}` -- the plaintext showing through. That is an
ASSUMPTION of the walk, not a measurement, and Michel's ciphertext autokey at lag 5
manufactures the same excess by a completely different route:

    c_j = v(p_j) + c_{j-5}    =>    c_j = c_{j-5}  <=>  v(p_j) = 0

Here d5 fires when p_j is one specific letter -- the one labelled 0 -- and p_{j-5}
is irrelevant. Pick a letter of frequency ~4.9% and the cell lands on the observed
0.0492 with no plaintext echo anywhere. The two mechanisms are indistinguishable
from the d5 rate alone, which is all anyone has looked at.

They separate on two other statistics.

1. CROSS-WORD d5. The walk changes base at every word, so cross-word d5 must be
   flat. A ciphertext feedback running continuously across words does not care
   about boundaries: it fires on `v(p_j) = 0` wherever it is, so cross-word d5
   must EQUAL within-word d5.

2. XY...XY -- a digram repeated at distance 5, i.e. d5 firing at j and j+1 both.
     walk:            needs p_j = p_{j+5} AND p_{j+1} = p_{j+6}
     lag-5 autokey:   needs v(p_j) = 0 AND v(p_{j+1}) = 0, i.e. p_j = p_{j+1} = x
                      -- a plaintext DOUBLET of one specific letter
   Plaintext doublets are suppressed and one letter carries only ~5% of the text,
   so the autokey predicts this pattern to be far rarer than the walk does. This
   is the statistic that tells a real echo from a manufactured one.

Models simulated on real runeglish at the LP's word-length histogram, each tuned
so its d5 matches the observed 0.0492, then judged on the statistics it was NOT
tuned to.
"""

from __future__ import annotations

import random
from collections import Counter

from experiments.d5_unit_model import dict_words
from experiments.walk_verifier import load_words

M = 29
FLAT = 1.0 / M
SEED = 3301


def lp_stats(words: list[list[int]]) -> dict:
    """Within-word d5, cross-word d5, and XY...XY count on a word list."""
    within_h = within_n = 0
    xy = 0
    for w in words:
        for i in range(len(w) - 5):
            within_n += 1
            within_h += w[i] == w[i + 5]
        for i in range(len(w) - 6):
            if w[i] == w[i + 5] and w[i + 1] == w[i + 6]:
                xy += 1
    stream, wid = [], []
    for k, w in enumerate(words):
        for r in w:
            stream.append(r)
            wid.append(k)
    cross_h = cross_n = 0
    for i in range(len(stream) - 5):
        if wid[i] != wid[i + 5]:
            cross_n += 1
            cross_h += stream[i] == stream[i + 5]
    return {
        "within": (within_h, within_n),
        "cross": (cross_h, cross_n),
        "xy": xy,
        "xy_opps": sum(max(0, len(w) - 6) for w in words),
    }


def build_plain(rng: random.Random, reps: int) -> list[list[int]]:
    lp_hist = Counter(len(w) for w in load_words())
    by_len = dict_words()
    out = []
    for _ in range(reps):
        for length, count in lp_hist.items():
            pool = by_len.get(length)
            if pool:
                out += [pool[rng.randrange(len(pool))] for _ in range(count)]
    rng.shuffle(out)
    return out


def enc_walk(words, v, rng):
    """The walk: base changes per word, g = identity for the d5 cell's purposes.

    Only the d5-relevant structure matters here, so use a random base per word and
    let plaintext equality at distance 5 pass through unchanged.
    """
    out = []
    for w in words:
        base = list(range(M))
        rng.shuffle(base)
        out.append([base[r] for r in w])
    return out


def enc_lag5_autokey(words, zero_letter, *, continuous):
    """c_j = v(p_j) + c_{j-5}, with v chosen so v(zero_letter) = 0."""
    v = [((r - zero_letter) % M) for r in range(M)]
    out = []
    carry: list[int] = []
    for w in words:
        c: list[int] = []
        ctx = carry if continuous else []
        for j, r in enumerate(w):
            prev = None
            if j >= 5:
                prev = c[j - 5]
            elif continuous and len(ctx) + j >= 5:
                prev = ctx[len(ctx) + j - 5]
            c.append((v[r] + prev) % M if prev is not None else v[r])
        out.append(c)
        carry = (carry + c)[-5:]
    return out


def report(name: str, st: dict, scale: float) -> None:
    wh, wn = st["within"]
    ch, cn = st["cross"]
    w_rate = wh / wn
    c_rate = ch / cn
    xy_rate = st["xy"] / st["xy_opps"] if st["xy_opps"] else 0.0
    print(
        f"{name:>28}{w_rate:>11.4f}{c_rate:>11.4f}"
        f"{xy_rate * 1000:>12.3f}{xy_rate * st['xy_opps'] * scale:>12.1f}"
    )


def main() -> None:
    lp = load_words()
    st = lp_stats(lp)
    wh, wn = st["within"]
    ch, cn = st["cross"]
    print(f"LP: within-word d5 {wh}/{wn} = {wh / wn:.4f}")
    print(f"    cross-word  d5 {ch}/{cn} = {ch / cn:.4f}")
    print(f"    XY...XY {st['xy']} in {st['xy_opps']} opportunities\n")

    se_w = (wh / wn * (1 - wh / wn) / wn) ** 0.5
    se_c = (ch / cn * (1 - ch / cn) / cn) ** 0.5
    z = (wh / wn - ch / cn) / (se_w**2 + se_c**2) ** 0.5
    print(f"within vs cross d5: z = {z:+.2f}")
    print("   a CONTINUOUS lag-5 feedback predicts these EQUAL (z = 0)")
    print("   the walk predicts cross-word flat at 0.0345\n")

    rng = random.Random(SEED)
    plain = build_plain(rng, reps=12)
    scale = st["xy_opps"] / sum(max(0, len(w) - 6) for w in plain)

    freq = Counter(r for w in plain for r in w)
    tot = sum(freq.values())
    target = wh / wn
    zero_letter = min(freq, key=lambda r: abs(freq[r] / tot - target))
    print(
        f"lag-5 autokey tuned: letter {zero_letter} has frequency "
        f"{freq[zero_letter] / tot:.4f}, closest to the observed d5\n"
    )

    print(
        f"{'model':>28}{'within d5':>11}{'cross d5':>11}"
        f"{'XY/1000':>12}{'XY expected':>12}"
    )
    report("LP OBSERVED", st, 1.0)
    report("walk (plaintext echo)", lp_stats(enc_walk(plain, None, rng)), scale)
    report(
        "lag-5 autokey, continuous",
        lp_stats(enc_lag5_autokey(plain, zero_letter, continuous=True)),
        scale,
    )
    report(
        "lag-5 autokey, per-word",
        lp_stats(enc_lag5_autokey(plain, zero_letter, continuous=False)),
        scale,
    )

    print("\nXY expected = the count each model predicts at the LP's corpus size,")
    print("against the LP's observed", st["xy"], "-- none of these models was")
    print("tuned to XY, so it is the honest test.")


if __name__ == "__main__":
    main()
