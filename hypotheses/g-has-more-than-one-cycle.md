---
type: observation
---
# Observation: The Letter Step Has More Than One 5-Cycle, and Sits Nearest Four

## A channel that follows from the model

The letter step has order 5, so its cycle type is 5ᵏ 1²⁹⁻⁵ᵏ for some k in 1..5. The
project assumes k = 5 — five 5-cycles and four fixed points — and nothing had measured it.

There is a channel, and it is a consequence rather than an assumption. Position j of a
block carries `base ∘ gʲ`, so a plaintext rune p enciphers to `base(gʲ(p))`. If **p is a
fixed point of g** then `gʲ(p) = p` for every j, and

> a fixed-point rune enciphers to the same ciphertext value everywhere in its block

at *any* distance, not only at multiples of five. So the within-block coincidence at
d = 2, 3, 4 carries a floor proportional to the number of fixed points, on top of whatever
g's graph contributes at those distances.

## Result

Body: within-block coincidence at lags 2, 3 and 4 is **1.0662** over 15,231 pairs.
Planted walks, 40 draws each:

| 5-cycles k | fixed points | median | 10th | 90th | draws below the body |
|---|---|---|---|---|---|
| 1 | 24 | 1.4837 | 1.2977 | 1.6768 | **2%** |
| 2 | 19 | 1.3741 | 0.8821 | 1.5803 | 25% |
| 3 | 14 | 1.2605 | 0.8184 | 1.5849 | 32% |
| 4 | 9 | **1.0283** | 0.7790 | 1.5359 | **52%** |
| 5 | 4 | 0.9240 | 0.6722 | 1.4134 | 70% |

The medians fall monotonically with the fixed-point count, which is what the mechanism
predicts. Against that scale:

- **k = 1 is excluded at p = 0.02.** A letter step with a single 5-cycle would leave 24
  runes enciphering identically throughout each block, and the body does not show it.
- **k = 2 through 5 are all admissible.** The body sits at the median for k = 4 and in
  the upper half for k = 5.

## The resolution is intrinsic, not a budget problem

The spread within each k is wide — the 10th-to-90th range spans 0.4 to 0.8 — and it does
not come from corpus size. It comes from where g's 5-cycles happen to fall relative to the
plaintext bigram table, so a longer corpus would not narrow it and neither would more
runtime. This is the resolution the channel has.

It also needs enough draws to see at all: at 12 and 15 draws the medians do not come out
monotone, and an earlier pass at 15 draws read the ordering backwards for k = 4 against
k = 5. Forty is the working figure.

## Status

**Status**: confirmed (measurement with planted controls at every cycle count). Excludes
k = 1 at p = 0.02; k = 2..5 admissible, nearest k = 4.
`experiments/g_fixed_points.py`.

## Related

- `mixed-cycle-progression.md` — the standing question about g's cycle structure, which
  this addresses for the first time with a direct measurement.
- `period5-is-confirmed` (memory) — the order-5 result this takes as given.
- `length-clocked-walk.md` — where the 5⁵1⁴ assumption is made.
