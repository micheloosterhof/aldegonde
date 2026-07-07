#!/usr/bin/env python3
"""Census of word-aligned phrase repeats in the unsolved LP.

A phrase repeat = two or more consecutive words whose concatenated ciphertext
appears again with identical internal word boundaries. Compared against a
Monte Carlo null: uniform random runes with the same word-length structure
(doublet suppression irrelevant for cross-position repeats, but we use the
Markov null anyway for rigor).

Also: word-suffix + next-word matches (like the IA / MNGYAC case).
"""

from collections import Counter, defaultdict

import numpy as np

from anomaly_scan import parse

N = 29


def word_pair_repeats(words):
    """Count repeated adjacent word pairs (and longer runs)."""
    seen = defaultdict(list)
    for i in range(len(words) - 1):
        key = (tuple(words[i]), tuple(words[i + 1]))
        seen[key].append(i)
    reps = {k: v for k, v in seen.items() if len(v) > 1}
    pairs = sum(len(v) * (len(v) - 1) // 2 for v in reps.values())
    return pairs, reps


def suffix_word_repeats(words, min_suffix=1, min_total=5):
    """Matches of (suffix of word k, all of word k+1 prefix>=...) — looser:
    count repeated (last rune of word k + word k+1) combos of total length
    >= min_total."""
    seen = defaultdict(list)
    for i in range(len(words) - 1):
        key = (words[i][-1], tuple(words[i + 1]))
        if 1 + len(words[i + 1]) >= min_total:
            seen[key].append(i)
    reps = {k: v for k, v in seen.items() if len(v) > 1}
    pairs = sum(len(v) * (len(v) - 1) // 2 for v in reps.values())
    return pairs, reps


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    # cipher words only
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= len(stream) - nplain:
            cw.append(w)
        total += len(w)
    words = cw
    print(f"{len(words)} cipher words")

    obs_pairs, reps = word_pair_repeats(words)
    print(f"\nobserved repeated adjacent word pairs: {obs_pairs}")
    for k, v in reps.items():
        from aldegonde import c3301
        w1 = "".join(c3301.CICADA_ALPHABET[x] for x in k[0])
        w2 = "".join(c3301.CICADA_ALPHABET[x] for x in k[1])
        print(f"  {w1}-{w2} (len {len(k[0])}+{len(k[1])}) at word idx {v}, "
              f"word-dist {[v[j+1]-v[j] for j in range(len(v)-1)]}")

    obs_sw, reps_sw = suffix_word_repeats(words)
    print(f"\nobserved suffix+word repeats (total len>=5): {obs_sw}")

    # Monte Carlo null: same word-length structure, Markov-null runes
    lens = [len(w) for w in words]
    n = sum(lens)
    rng = np.random.default_rng(7)
    SAMPLES = 300
    mc_pairs = []
    mc_sw = []
    p_dd = 0.00675
    for _ in range(SAMPLES):
        # markov stream
        out = np.empty(n, dtype=np.int64)
        out[0] = rng.integers(0, N)
        same = rng.random(n) < p_dd
        jump = rng.integers(0, N - 1, n)
        for i in range(1, n):
            if same[i]:
                out[i] = out[i - 1]
            else:
                j = jump[i]
                out[i] = j if j < out[i - 1] else j + 1
        ws = []
        k = 0
        for L in lens:
            ws.append(out[k : k + L].tolist())
            k += L
        p, _ = word_pair_repeats(ws)
        s, _ = suffix_word_repeats(ws)
        mc_pairs.append(p)
        mc_sw.append(s)
    mc_pairs = np.array(mc_pairs)
    mc_sw = np.array(mc_sw)
    print(f"\nMC null ({SAMPLES} samples):")
    print(f"  adjacent word-pair repeats: mean={mc_pairs.mean():.3f} "
          f"sd={mc_pairs.std():.3f} max={mc_pairs.max()}  "
          f"P(>= {obs_pairs}) = {(mc_pairs >= obs_pairs).mean():.4f}")
    print(f"  suffix+word repeats: mean={mc_sw.mean():.3f} sd={mc_sw.std():.3f} "
          f"max={mc_sw.max()}  P(>= {obs_sw}) = {(mc_sw >= obs_sw).mean():.4f}")
    # joint probability of seeing both
    both = ((mc_pairs >= obs_pairs) & (mc_sw >= obs_sw)).mean()
    print(f"  P(both >= observed) = {both:.4f}")


if __name__ == "__main__":
    main()
