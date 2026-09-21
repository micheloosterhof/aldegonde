# ABOUTME: Prices the sharpest available test of whether the letter clock resets per block
# ABOUTME: or runs continuously, and finds it needs eighteen times the corpus.
"""The clock convention is worth a factor of five and cannot be settled here.

`key-local-channel-is-empty.md` derives order(sigma) >= 1,536 if the letter phase resets
at each block and only >= 307 if it runs continuously, and leaves the convention open. Two
channels have now been tried.

The first, in `sigma-moves-almost-every-rune.md`, reads adjacent blocks under both phase
conventions. It fails: a planted continuous clock scores +2.54 under the RESET reading
against a planted reset clock's +2.86, so that reading fires either way.

The second is sharper and is priced here. Under a continuous clock, comparing runes at
matching POSITION mod 5 in adjacent blocks is the right comparison exactly when the first
block's length is divisible by 5, since only then do the two blocks' start phases agree.
Under a reset clock it is always right. So the signal should CONCENTRATE in the
len % 5 == 0 class under a continuous clock and be flat under a reset one, and the
contrast between that class and the others discriminates them.

It does discriminate -- and by far too little.

    python clock_convention_power.py
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from sigma_fixed_points import M, body_blocks, planted  # noqa: E402

from lp_plaintext_register import corpus  # noqa: E402


def contrast(blocks: list[list[int]]) -> float:
    """nIoC of the len%5==0 class minus the mean of the other four."""
    cells = {r: [0, 0] for r in range(5)}
    for w in range(len(blocks) - 1):
        a_block, b_block = blocks[w], blocks[w + 1]
        r = len(a_block) % 5
        for i, a in enumerate(a_block):
            for j, b in enumerate(b_block):
                if i % 5 == j % 5:
                    cells[r][1] += 1
                    cells[r][0] += a == b
    v = {r: (cells[r][0] / cells[r][1] * M if cells[r][1] else 0.0) for r in range(5)}
    return v[0] - sum(v[r] for r in (1, 2, 3, 4)) / 4


def continuous_walk(f_sigma: int, words, rng: random.Random) -> list[list[int]]:
    """Like sigma_fixed_points.planted but with the letter phase running across blocks."""
    points = list(range(M))
    rng.shuffle(points)
    g = list(range(M))
    for c in range(5):
        blk = points[c * 5 : (c + 1) * 5]
        for a, b in zip(blk, blk[1:] + blk[:1]):
            g[a] = b
    order = list(range(M))
    rng.shuffle(order)
    fixed = set(order[:f_sigma])
    rest = [x for x in range(M) if x not in fixed]
    sh = rest[:]
    while len(rest) > 1 and any(a == b for a, b in zip(rest, sh)):
        rng.shuffle(sh)
    sigma = list(range(M))
    for a, b in zip(rest, sh):
        sigma[a] = b
    base = list(range(M))
    rng.shuffle(base)
    blocks, total = [], 0
    for _ in range(2928):
        word = rng.choice(words)
        step = list(range(M))
        for _ in range(total % 5):
            step = [g[x] for x in step]
        blk = []
        for p in word:
            blk.append(base[step[p]])
            step = [g[x] for x in step]
        blocks.append(blk)
        total += len(word)
        base = [base[sigma[x]] for x in range(M)]
    return blocks


def main() -> None:
    rng = random.Random(31)
    words = corpus()
    reset = statistics.median(contrast(planted(5, words, rng)) for _ in range(8))
    cont = statistics.median(contrast(continuous_walk(5, words, rng)) for _ in range(8))
    print(f"planted reset clock,      sigma fixes 5: contrast {reset:+.4f}")
    print(f"planted continuous clock, sigma fixes 5: contrast {cont:+.4f}")
    separation = abs(cont - reset)
    print(f"separation {separation:.4f}\n")

    blocks = body_blocks()
    obs = contrast(blocks)
    flat = [x for b in blocks for x in b]
    null = []
    for _ in range(60):
        t = flat[:]
        rng.shuffle(t)
        it = iter(t)
        null.append(contrast([[next(it) for _ in b] for b in blocks]))
    mu = statistics.mean(null)
    sd = statistics.pstdev(null)
    print(f"body contrast {obs:+.4f}; shuffled null {mu:+.4f} +- {sd:.4f}, z = {(obs - mu) / sd:+.2f}")
    print(f"\nseparation / noise = {separation / sd:.2f} sigma")
    print(f"corpus factor needed to reach 2 sigma: {(2 * sd / separation) ** 2:.0f}x"
          f"  ({12956 * (2 * sd / separation) ** 2:,.0f} runes)")
    print(
        "\nSo the sharpest discriminator available is about a quarter the size it would"
        "\nneed to be, and the shortfall is in the corpus rather than the method. The"
        "\nconvention cannot be settled here, and the sigma order bound has to keep both"
        "\nreadings -- 307 and 1,536 -- rather than choosing."
    )


if __name__ == "__main__":
    main()
