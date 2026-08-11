# ABOUTME: Tests the mixed-cycle-progression reading of the within-word rising
# ABOUTME: staircase: inverts the d2-d8 rates to a returned-alphabet-fraction
# ABOUTME: ladder, fits a cycle census for g, and confronts the d6 deficit.
"""Mixed-cycle progressive substitution: can the staircase be g's cycle census?

If the letter step g has mixed cycle lengths, positions d apart agree
wherever the plaintext repeats on a letter whose cycle length divides d:
the "returned fraction" phi_d of the alphabet grows with d, producing a
rising coincidence staircase structurally. Under a random assignment of
letters to cycles the expected within-word match rate at distance d is

    r_d = phi_d * K_d + (1 - phi_d) * (1 - K_d) / 28

with K_d the plaintext within-word coincidence at distance d (measured on
register prose cut to the LP word-length structure). Each observed rate
inverts to phi_d = (r_d - b_d) / (K_d - b_d), b_d = (1 - K_d)/28, and the
phi ladder must be realizable as (letters in cycles dividing d)/29 for a
single integer cycle census — including the d5 partial-echo fraction and
the d6 cell, where the mixed-cycle model and the order-5 model make
OPPOSITE predictions (3-cycle letters return at d6 vs the inherited
tuned-diagonal deficit).

Part 1 measures K_d, inverts phi_d with binomial errors, and reports the
best small-cycle census. Part 2 simulates the walk with the best census
(order lcm of the cycle lengths) vs the order-5 baseline and prints the
resulting staircases next to the LP's.
"""

from __future__ import annotations  # noqa: I001

import math
import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from sigma_power_kill import compose  # noqa: E402

M = 29
MAXD = 8


def lp_profile(stream, wid):
    words: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        words.setdefault(w, []).append(stream[i])
    m: Counter = Counter()
    s: Counter = Counter()
    for w in words.values():
        L = len(w)
        for j in range(L):
            for d in range(1, min(MAXD + 1, L - j)):
                s[d] += 1
                m[d] += w[j] == w[j + d]
    return m, s, [words[k] for k in sorted(words)]


def prose_k(lp_lens, prose_stream, rng, samples=40):
    """K_d: plaintext within-word coincidence by distance, LP length mix."""
    m: Counter = Counter()
    s: Counter = Counter()
    for _ in range(samples):
        off = rng.randrange(len(prose_stream) - sum(lp_lens))
        pos = off
        for L in lp_lens:
            w = prose_stream[pos : pos + L]
            pos += L
            for j in range(L):
                for d in range(1, min(MAXD + 1, L - j)):
                    s[d] += 1
                    m[d] += w[j] == w[j + d]
    return {d: m[d] / s[d] for d in s}


def census_phi(census: tuple[int, ...], d: int) -> float:
    return sum(L for L in census if d % L == 0) / M


def make_g(census: tuple[int, ...], rng) -> list[int]:
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    i = 0
    for L in census:
        cyc = pts[i : i + L]
        i += L
        for k in range(L):
            g[cyc[k]] = cyc[(k + 1) % L]
    return g


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    obs_m, obs_s, lp_words = lp_profile(stream, wid)
    lp_lens = [len(w) for w in lp_words]

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    prose_stream = [
        IDX_ENG[t] for w in prose_words(prose_path) for t in to_runeglish(w)
    ]
    K = prose_k(lp_lens, prose_stream, rng)

    print("Part 1 — phi ladder inverted from the LP staircase:")
    print(
        f"{'d':>2} {'LP rate':>8} {'K_d':>7} {'phi_d':>7} {'± (1σ)':>7} "
        f"{'letters (29·phi)':>16}"
    )
    phi_est = {}
    for d in range(1, MAXD + 1):
        r = obs_m[d] / obs_s[d]
        b = (1 - K[d]) / 28
        phi = (r - b) / (K[d] - b)
        sd_r = math.sqrt(r * (1 - r) / obs_s[d])
        sd_phi = sd_r / (K[d] - b)
        phi_est[d] = (phi, sd_phi)
        note = " (diagonal-tuned channel)" if d == 1 else ""
        print(
            f"{d:>2} {r:>8.4f} {K[d]:>7.4f} {phi:>7.2f} {sd_phi:>7.2f} "
            f"{29 * phi:>+16.1f}{note}"
        )

    # census search: partitions of 29 into parts 1..6, scored on d2..d5
    # (d6 reported as the discriminating cell, not fitted)
    best = []
    for n6 in range(3):
        for n5 in range(6):
            for n4 in range(4):
                for n3 in range(4):
                    for n2 in range(3):
                        rest = M - (6 * n6 + 5 * n5 + 4 * n4 + 3 * n3 + 2 * n2)
                        if rest < 0:
                            continue
                        census = (
                            (1,) * rest
                            + (2,) * n2
                            + (3,) * n3
                            + (4,) * n4
                            + (5,) * n5
                            + (6,) * n6
                        )
                        chi = sum(
                            ((census_phi(census, d) - phi_est[d][0]) / phi_est[d][1])
                            ** 2
                            for d in (2, 3, 4, 5)
                        )
                        best.append((chi, census))
    best.sort()
    print("\nbest cycle censuses (fitted on d2-d5; d6 prediction shown):")
    print(
        f"{'census':>28} {'chi2(d2-5)':>10} {'phi6 pred':>9} "
        f"{'phi6 obs':>8} {'d6 pull':>8}"
    )
    for chi, census in best[:5]:
        p6 = census_phi(census, 6)
        pull = (p6 - phi_est[6][0]) / phi_est[6][1]
        cs = "+".join(str(L) for L in census if L > 1) or "id"
        n1 = sum(1 for L in census if L == 1)
        print(
            f"{cs + (f' +{n1}fix' if n1 else ''):>28} {chi:>10.2f} "
            f"{p6:>9.2f} {phi_est[6][0]:>8.2f} {pull:>+8.1f}"
        )

    # order-5 baseline for comparison
    o5 = (5, 5, 5, 5, 5, 1, 1, 1, 1)
    chi5 = sum(
        ((census_phi(o5, d) - phi_est[d][0]) / phi_est[d][1]) ** 2 for d in (2, 3, 4, 5)
    )
    p6 = census_phi(o5, 6)
    print(
        f"{'order-5 (5x5 +4fix)':>28} {chi5:>10.2f} {p6:>9.2f} "
        f"{phi_est[6][0]:>8.2f} "
        f"{(p6 - phi_est[6][0]) / phi_est[6][1]:>+8.1f}"
    )

    # Part 2 — simulate best census vs order-5
    print(
        "\nPart 2 — simulated within-word staircases (30 runs each, "
        "random letter assignment, random base per word):"
    )
    print(f"{'model':>28} " + "".join(f"{f'd{d}':>8}" for d in range(1, MAXD + 1)))
    lp_rates = [obs_m[d] / obs_s[d] for d in range(1, MAXD + 1)]
    print(f"{'LP observed':>28} " + "".join(f"{r:>8.4f}" for r in lp_rates))
    print(
        f"{'prose K_d (no cipher)':>28} "
        + "".join(f"{K[d]:>8.4f}" for d in range(1, MAXD + 1))
    )

    for name, census in (("best fit", best[0][1]), ("order-5", o5)):
        acc_m = Counter()
        acc_s = Counter()
        for _ in range(30):
            g = make_g(census, rng)
            gp = [list(range(M))]
            order = 1
            for L in set(census):
                order = order * L // math.gcd(order, L)
            for _ in range(order - 1):
                gp.append(compose(g, gp[-1]))
            off = rng.randrange(len(prose_stream) - sum(lp_lens))
            pos = off
            for L in lp_lens:
                w = prose_stream[pos : pos + L]
                pos += L
                base = list(range(M))
                rng.shuffle(base)
                ct = [base[gp[j % order][p]] for j, p in enumerate(w)]
                for j in range(L):
                    for d in range(1, min(MAXD + 1, L - j)):
                        acc_s[d] += 1
                        acc_m[d] += ct[j] == ct[j + d]
        cs = "+".join(str(L) for L in census if L > 1)
        print(
            f"{name + ' (' + cs + ')':>28} "
            + "".join(f"{acc_m[d] / acc_s[d]:>8.4f}" for d in range(1, MAXD + 1))
        )


if __name__ == "__main__":
    main()
