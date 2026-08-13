# ABOUTME: Simulates a lag-1 ciphertext + lag-5 plaintext autokey and measures it
# ABOUTME: against the LP's signatures, including the floor on its doublet rate.
"""A dual autokey: lag-1 ciphertext feedback plus lag-5 plaintext feedback.

    c_j = alpha * p_j + beta * c_{j-1} + gamma * p_{j-5}   (mod 29)

Michel's proposal. It matters because it escapes the test that killed pure
ciphertext autokey. Grouping runes by the previous ciphertext rune fixes c_{j-1},
leaving `c_j = alpha p_j + gamma p_{j-5} + const` -- a CONVOLUTION of two plaintext
letters, which is far flatter than plaintext. So grouped IoC stays near 1.0 instead
of rising to ~1.78, and the ciphertext-feedback signature never appears.

**beta = 1 is forced.** The doublet condition is

    c_j == c_{j+1}   <=>   c_j (1 - beta) = alpha p_{j+1} + gamma p_{j-4}

If beta != 1 the left side is a flat ciphertext value and the condition holds at
chance. With beta = 1 it reduces to a pure plaintext relation at distance 5:

    p_{j+1} = lambda * p_{j-4},   lambda = -gamma/alpha

so the doublet rate is the lambda-diagonal of the distance-5 plaintext table.

Measured against the LP (real runeglish prose, LP-matched word lengths):

    signature        LP        this cipher
    IoC              1.000     1.000     ok
    grouped IoC      1.026     1.046     ok   (pure ct autokey: 1.756)
    delta IoC        1.024     1.046     ok
    within-word d1   0.63%     2.28%     suppressed, but not enough
    seam d1          0.79%     1.91%     boundary-blind FOR FREE
    within-word d5   4.92%     2.99%     FAILS -- no echo

**The doublet floor.** With a BIJECTIVE value map v, the relation
`pi = v^-1 (x lambda) v` is conjugate to multiplication by lambda, so its cycle type
is fixed by ord(lambda), and ord(lambda) divides 28 -- five never appears. Because
multiplication fixes 0, pi always has a fixed point, which contributes that rune's
plaintext distance-5 self-coincidence. Hillclimbing the assignment for each order:

    ord(lambda)   1      2      4      7     14     28
    min diagonal  6.03%  0.911% 0.896% 0.950% 0.880% 0.857%

So the family floors near **0.86%** against an observed 0.63% -- about 1.4x short.
Two caveats: the floor is hillclimbed rather than proven, and it rests on a
Pride & Prejudice distance-5 table, so register uncertainty could move it by more
than 1.4x. This is "short on the reference available", not a refutation.

(An earlier pass used the Gematria values mod 29 as the value map. Those are NOT
injective -- 24 distinct residues, with F/I/D all congruent to 2 -- so that run was
invalid. The stream simulation uses rune indices 0..28, which are bijective.)

**The trade-off, which is the real finding.** The lag-5 PLAINTEXT term alone
produces the d5 echo (5.93% against a 4.92% target). The lag-1 CIPHERTEXT term alone
produces the doublet suppression. Combined, the ciphertext recursion makes c_j depend
on the whole prefix, which destroys the clean distance-5 relation and washes the echo
out to 2.99%. Something else has to carry the period-5 that the feedback does not
reach through.
"""

from __future__ import annotations

import bisect
import random
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
PROSE = Path(tempfile.gettempdir()) / "pg1342.txt"


def matched_plaintext(rng: random.Random) -> tuple[list[int], list[int]]:
    """Runeglish prose resampled to the LP's word-length histogram, plus boundaries."""
    body = PROSE.read_text(errors="ignore")
    body = body[body.find("It is a truth universally") :]
    by_len: dict[int, list[list[int]]] = {}
    for word in re.findall(r"[A-Za-z]+", body):
        runes = [IDX[c] for c in english_to_runeglish(word.upper()) if c in IDX]
        if runes:
            by_len.setdefault(len(runes), []).append(runes)
    words = []
    for length, count in Counter(len(w) for w in load_words()).items():
        if length in by_len:
            words += [rng.choice(by_len[length]) for _ in range(count)]
    rng.shuffle(words)
    stream: list[int] = []
    bounds: list[int] = []
    for w in words:
        stream += w
        bounds.append(len(stream))
    return stream, bounds


def encipher(plain: list[int], *, ct_lag: int, pt_lag: int) -> list[int]:
    """c_j = p_j + c_{j-ct_lag} + p_{j-pt_lag}, omitting unavailable terms."""
    out: list[int] = []
    for j, p in enumerate(plain):
        v = p
        if ct_lag and j >= ct_lag:
            v += out[j - ct_lag]
        if pt_lag and j >= pt_lag:
            v += plain[j - pt_lag]
        out.append(v % M)
    return out


def within_word_rates(c: list[int], bounds: list[int]) -> dict[int, float]:
    wid = lambda i: bisect.bisect_right(bounds, i)  # noqa: E731
    out = {}
    for k in range(1, 7):
        total = hits = 0
        for j in range(len(c) - k):
            if wid(j) == wid(j + k):
                total += 1
                hits += c[j] == c[j + k]
        out[k] = 100 * hits / total if total else 0.0
    return out


def seam_rate(c: list[int], bounds: list[int]) -> float:
    total = hits = 0
    for b in bounds[:-1]:
        if b < len(c):
            total += 1
            hits += c[b - 1] == c[b]
    return 100 * hits / total if total else 0.0


def ioc(seq: list[int]) -> float:
    counts = Counter(seq)
    n = len(seq)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1) / M) if n > 1 else 0


def grouped_ioc(c: list[int]) -> float:
    groups: dict[int, list[int]] = {}
    for j in range(1, len(c)):
        groups.setdefault(c[j - 1], []).append(c[j])
    big = [v for v in groups.values() if len(v) > 30]
    return sum(ioc(v) * len(v) for v in big) / sum(len(v) for v in big)


def main() -> None:
    rng = random.Random(3301)
    plain, bounds = matched_plaintext(rng)
    lp = load_words()
    lp_stream = [r for w in lp for r in w]
    lp_bounds = []
    total = 0
    for w in lp:
        total += len(w)
        lp_bounds.append(total)

    print(
        f"{'cipher':<30}{'IoC':>7}{'grpIoC':>8}"
        + "".join(f"{'d' + str(k):>7}" for k in range(1, 7))
        + f"{'seam':>7}"
    )
    r = within_word_rates(lp_stream, lp_bounds)
    print(
        f"{'LIBER PRIMUS (target)':<30}{ioc(lp_stream):>7.3f}{grouped_ioc(lp_stream):>8.3f}"
        + "".join(f"{r[k]:>7.2f}" for k in range(1, 7))
        + f"{seam_rate(lp_stream, lp_bounds):>7.2f}"
    )
    for label, ct, pt in (
        ("p + c[-1] + p[-5]  (dual)", 1, 5),
        ("p + c[-1]   (ct autokey)", 1, 0),
        ("p + p[-5]   (pt autokey)", 0, 5),
    ):
        c = encipher(plain, ct_lag=ct, pt_lag=pt)
        r = within_word_rates(c, bounds)
        print(
            f"{label:<30}{ioc(c):>7.3f}{grouped_ioc(c):>8.3f}"
            + "".join(f"{r[k]:>7.2f}" for k in range(1, 7))
            + f"{seam_rate(c, bounds):>7.2f}"
        )
    print("\nThe dual form keeps grouped IoC near 1.0 where pure ciphertext autokey")
    print("gives ~1.76 -- that is the test it escapes. It suppresses doublets from")
    print("structure alone, and is boundary-blind for free. It does NOT produce the")
    print("d5 echo: the lag-5 plaintext term does, and the ciphertext recursion")
    print("destroys it. See the module docstring for the 0.86% floor.")


if __name__ == "__main__":
    main()
