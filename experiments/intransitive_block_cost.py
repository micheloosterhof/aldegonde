# ABOUTME: The only escape from the compact-state dichotomy is an intransitive
# ABOUTME: state group. This prices it against runeglish unigram frequencies.
"""compact_state_dichotomy.py shows that a TRANSITIVE state group containing
an order-5 element must be A_29 or S_29 -- astronomical, so not a device.

The escape is intransitivity: if <g, sigma> preserves a partition of the 29
runes into blocks, |G| can be small enough to index, and the machine becomes
hand-runnable (e.g. five independent 5-position wheels, |G| = 5^5 = 3125).

That escape has a price, and it is paid in the plaintext rather than the key.
If no base ever moves a rune out of its block, then for every block B

    (ciphertext mass of B) == (plaintext mass of B)

for the whole book. The ciphertext is flat (obs chi2 p = 0.55), so block B
carries mass |B|/29. Hence the PLAINTEXT unigram masses must already
partition into blocks of mass |B|/29 -- and runeglish frequencies are
strongly non-uniform, so this is a real constraint.

This script asks how well any partition can do, given g's cycle type forces
every block to be a union of g-orbits (five 5-cycles + four fixed points).

No claim is made that a good partition proves anything; the point is to find
out whether the escape is cheap or expensive.
"""

from __future__ import annotations

import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N = 29


def unigram_freqs() -> dict[str, float]:
    path = ROOT / "src" / "aldegonde" / "data" / "ngrams" / "runeglish" / "unigrams.txt"
    counts = {}
    for line in path.read_text().split("\n"):
        if not line.strip():
            continue
        r, c = line.split()
        counts[r] = int(c)
    tot = sum(counts.values())
    return {r: c / tot for r, c in counts.items()}


def main() -> None:
    f = unigram_freqs()
    assert len(f) == N, len(f)
    assert abs(sum(f.values()) - 1.0) < 1e-9
    target = 1.0 / N
    ranked = sorted(f.items(), key=lambda kv: -kv[1])
    print("runeglish unigram frequencies (target for a singleton block: 0.03448)")
    for r, v in ranked:
        mark = ""
        if v > 3 * target:
            mark = "  <- far too heavy for any small block"
        elif v < target / 5:
            mark = "  <- far too light"
        print(f"  {r}  {v:.5f}{mark}")

    # A block of size k must carry mass k/29. How many runes could be singletons?
    print(f"\nsingleton-viable runes (mass within 20% of {target:.5f}):")
    singles = [r for r, v in f.items() if abs(v - target) / target < 0.20]
    print(f"  {singles or 'NONE'}   ({len(singles)} of 29)")

    # g has cycle type 5^5 1^4, so blocks are unions of g-orbits: five 5-sets
    # and four singletons. Any block containing a 5-cycle has size >= 5.
    # Best case for a compact machine: exactly the five 5-cycles as blocks
    # (|G| <= 120^5) plus four fixed runes. Each 5-block then needs mass 5/29.
    print("\n--- best achievable partition into five 5-blocks + four singletons ---")
    print(f"  each 5-block needs mass {5 / N:.5f}; each singleton {target:.5f}")

    runes = [r for r, _ in ranked]
    # Choose the 4 singletons to be the closest to target, then greedily balance
    # the remaining 25 into five blocks of five.
    singles4 = sorted(runes, key=lambda r: abs(f[r] - target))[:4]
    rest = [r for r in runes if r not in singles4]
    rest.sort(key=lambda r: -f[r])
    blocks: list[list[str]] = [[] for _ in range(5)]
    for r in rest:  # greedy: heaviest rune into the lightest block with room
        b = min((b for b in blocks if len(b) < 5), key=lambda b: sum(f[x] for x in b))
        b.append(r)

    worst = 0.0
    for i, b in enumerate(blocks):
        m = sum(f[x] for x in b)
        err = abs(m - 5 / N) / (5 / N)
        worst = max(worst, err)
        print(
            f"  block {i}: mass {m:.5f}  ({err * 100:+.1f}% vs required)  {''.join(b)}"
        )
    for r in singles4:
        err = abs(f[r] - target) / target
        worst = max(worst, err)
        print(f"  singleton {r}: mass {f[r]:.5f}  ({err * 100:+.1f}% vs required)")

    print(f"\n  worst block error under the best greedy partition: {worst * 100:.1f}%")

    # Exhaustive check on the singletons: the four lightest/heaviest runes make
    # singletons impossible, so quantify how bad the forced choice is.
    best4 = min(
        itertools.combinations(runes, 4),
        key=lambda c: max(abs(f[r] - target) / target for r in c),
    )
    worst_single = max(abs(f[r] - target) / target for r in best4)
    print(
        f"  best possible four singletons: {''.join(best4)}  "
        f"worst error {worst_single * 100:.1f}%"
    )
    # A singleton's ciphertext count EQUALS its plaintext count, so quantify
    # the forced deviation against the observed flat ciphertext.
    n_runes = 12956
    sd = (n_runes * target * (1 - target)) ** 0.5
    print(
        f"\n  ciphertext consequence (corpus {n_runes} runes, expected {n_runes * target:.0f} +/- {sd:.1f}):"
    )
    for r in best4:
        cnt = f[r] * n_runes
        print(
            f"    singleton {r}: forced ciphertext count {cnt:.0f}  z = {(cnt - n_runes * target) / sd:+.2f}"
        )
    print("    observed ciphertext counts span 399..492 (flat-ioc.md)")

    # But blocks need only be unions of g-ORBITS, and g's four fixed points may
    # form ONE block of size 4 rather than four singletons. That is far cheaper.
    print("\n--- freer partition: blocks are arbitrary unions of g-orbits ---")
    for sizes in (
        [5, 5, 5, 5, 5, 4],
        [5, 5, 5, 5, 5, 1, 1, 1, 1],
        [10, 5, 5, 5, 4],
        [25, 4],
    ):
        err = best_partition_error(f, sizes)
        print(f"  block sizes {str(sizes):<30} worst mass error {err * 100:5.1f}%")

    print(
        "\n  Reading: four SINGLETON blocks are expensive -- some rune's ciphertext\n"
        "  count is forced >=23% off flat, around 5 sigma. But letting g's four\n"
        "  fixed points share ONE block of size 4 removes that cost almost\n"
        "  entirely. So the intransitive escape is NOT closed by unigram masses;\n"
        "  only its four-singleton special case is."
    )


def best_partition_error(
    f: dict[str, float], sizes: list[int], iters: int = 40000
) -> float:
    """Min over partitions of max |block mass - size/29| / (size/29), by local search."""
    import random

    rng = random.Random(3301)
    runes = list(f)
    assert sum(sizes) == len(runes)

    def cost(assign: list[int]) -> float:
        masses = [0.0] * len(sizes)
        for r, b in zip(runes, assign):
            masses[b] += f[r]
        return max(abs(m - s / N) / (s / N) for m, s in zip(masses, sizes))

    assign = []
    for b, s in enumerate(sizes):
        assign += [b] * s
    rng.shuffle(assign)
    best = cost(assign)
    for _ in range(iters):
        i, j = rng.randrange(len(runes)), rng.randrange(len(runes))
        if assign[i] == assign[j]:
            continue
        assign[i], assign[j] = assign[j], assign[i]
        c = cost(assign)
        if c <= best:
            best = c
        else:
            assign[i], assign[j] = assign[j], assign[i]
    return best


if __name__ == "__main__":
    main()
