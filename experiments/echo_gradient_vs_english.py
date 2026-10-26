# ABOUTME: Compares the within-word distance-5 coincidence of the body with English prose
# ABOUTME: class by word-length class, to see whether the echo's rise with length is inherited.
"""Does the shared-alphabet window read English at every word length?

Positions five apart inside a block share a substitution, so `c_i = c_(i+5)` exactly when
`p_i = p_(i+5)`: the within-block d5 rate is a plaintext statistic. Pooled, it is ordinary
English once length and the preventer's drift are carried
(`is_the_d5_rate_normal_for_english.py`). But the body's rate rises with block length --
1.15x chance at 6-7 runes, 1.81x at 10+ -- and that was recorded as suggestive because
the author's own plaintext shows no trend on 261 pairs. English prose does rise with
length. So the question is whether the two gradients match class by class.

For each length class: the body's rate with its binomial error, prose's rate (nine
Gutenberg registers, book spelling, pooled) with its error, prose attenuated by the drift
`(1-q)^5` at the recorded q = 0.034, and the body's departure in sigma. A chi-square over
the classes asks whether one attenuation fits every class; a weighted regression asks
whether the body's slope against length is English's.

    python experiments/echo_gradient_vs_english.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from frame_count_baseline import prose_books  # noqa: E402
from within_word_d5 import M, parse_clean_sections  # noqa: E402

LAG = 5
Q = 0.034
CLASSES = ((6, 6), (7, 7), (8, 8), (9, 9), (10, 11), (12, 99))
CHANCE = 1 / M


def rates_by_class(words: list[list[int]]) -> dict[tuple[int, int], tuple[int, int]]:
    """(matches, pairs) at distance 5 inside words, per length class."""
    out = {c: [0, 0] for c in CLASSES}
    for w in words:
        for c in CLASSES:
            if c[0] <= len(w) <= c[1]:
                break
        else:
            continue
        pairs = len(w) - LAG
        out[c][1] += pairs
        out[c][0] += sum(w[i] == w[i + LAG] for i in range(pairs))
    return {c: (m, n) for c, (m, n) in out.items()}


def drifted(rate: float, q: float = Q) -> float:
    keep = (1 - q) ** LAG
    return keep * rate + (1 - keep) * CHANCE


def label(c: tuple[int, int]) -> str:
    return (
        f"{c[0]}" if c[0] == c[1] else (f"{c[0]}-{c[1]}" if c[1] < 99 else f"{c[0]}+")
    )


def main() -> None:
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    body = rates_by_class([w for s in sections for w in s])
    prose = rates_by_class([w for b in prose_books() for w in b])

    print(
        f"within-word d5 by block length; prose drifted at q = {Q}; chance {CHANCE:.4f}\n"
    )
    print(
        f"{'length':<8}{'body pairs':>11}{'body rate':>11}{'±':>8}{'prose rate':>12}{'±':>8}"
        f"{'drifted':>9}{'body/drifted':>13}{'z':>7}"
    )
    chi2 = 0.0
    xs, ys, ws, es = [], [], [], []
    for c in CLASSES:
        mb, nb = body[c]
        mp, np_ = prose[c]
        rb, rp = mb / nb, mp / np_
        sb = np.sqrt(rb * (1 - rb) / nb)
        sp = np.sqrt(rp * (1 - rp) / np_)
        ref = drifted(rp)
        s_ref = (1 - Q) ** LAG * sp
        z = (rb - ref) / np.sqrt(sb**2 + s_ref**2)
        chi2 += z**2
        xs.append((c[0] + min(c[1], 14)) / 2)
        ys.append(rb)
        es.append(ref)
        ws.append(1 / (sb**2 + s_ref**2))
        print(
            f"{label(c):<8}{nb:>11}{rb:>11.4f}{sb:>8.4f}{rp:>12.4f}{sp:>8.4f}"
            f"{ref:>9.4f}{rb / ref:>13.2f}{z:>+7.2f}"
        )
    print(
        f"\nchi2 over {len(CLASSES)} classes against drifted English: {chi2:.1f} on {len(CLASSES)} df"
    )

    xs, ys, es, ws = map(np.array, (xs, ys, es, ws))
    for name, y in (("body", ys), ("drifted English", es)):
        xm = np.average(xs, weights=ws)
        slope = np.sum(ws * (xs - xm) * (y - np.average(y, weights=ws))) / np.sum(
            ws * (xs - xm) ** 2
        )
        se = np.sqrt(1 / np.sum(ws * (xs - xm) ** 2)) if name == "body" else 0.0
        print(
            f"slope of {name:<16} {slope:+.5f} per rune"
            + (f"  ± {se:.5f}" if se else "")
        )
    diff = np.sum(ws * (xs - np.average(xs, weights=ws)) * (ys - es)) / np.sum(
        ws * (xs - np.average(xs, weights=ws)) ** 2
    )
    se = np.sqrt(1 / np.sum(ws * (xs - np.average(xs, weights=ws)) ** 2))
    print(
        f"slope of body minus English  {diff:+.5f} ± {se:.5f} per rune, z = {diff / se:+.2f}"
    )

    pooled_b = sum(m for m, _ in body.values()) / sum(n for _, n in body.values())
    pooled_ref = sum(
        drifted(prose[c][0] / prose[c][1]) * body[c][1] for c in CLASSES
    ) / sum(n for _, n in body.values())
    print(
        f"\npooled, body-length-weighted: body {pooled_b:.4f}, drifted English {pooled_ref:.4f}"
    )


if __name__ == "__main__":
    main()
