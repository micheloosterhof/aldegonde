#!/usr/bin/env python3
# ABOUTME: Full forced-alignment OCR comparison of the LP page scans against
# ABOUTME: the transcription, with self-bootstrapped page-native templates.
"""Full OCR comparison of data/page0-58.txt against the page images.

Requires: pillow, scipy, and a clone of https://github.com/rtkd/iddqd at
/tmp/iddqd (page scans in liber-primus__images--unsolved/, font in ttf/).

Pipeline (modes, in order):
  harvest  - rough forced alignment using templates rendered from the
             shipped BabelStone TTF (horizontally compressed 0.73x to match
             the page typesetting); harvest confident glyph crops.
  harvest2 - re-harvest with neighbor-anchored extraction using the round-1
             native templates (separator dots removed via connected
             components; exemplar widths filtered by font priors).
  build    - median-stack exemplars into page-native templates.
  verify   - forced alignment of every transcription line onto its line
             band (FFT correlation responses + DP with the whole-line
             reconstruction objective: per-glyph score = 2*overlap - area);
             flag any glyph whose claimed rune scores low or loses to a
             slot-compatible alternative.
  inspect  - render crop/template panels for a flagged position.

RESULTS (full run over all 57 rune pages, ~13,136 runes):
- 44 pages fully machine-verified: mean reconstruction cover ~0.97, zero
  unexplained glyph disagreements.
- 13 section-start pages (0,3,6,8,15,23,27,33,39,40,53,55,56) have 117
  lines that fail STRUCTURAL alignment due to giant decorative initials /
  red text / layout; their remaining lines verified. ~83% of the corpus is
  machine-verified glyph-by-glyph.
- 6 single-glyph candidates were flagged and ALL resolved on visual
  inspection as non-rune page elements, not transcription errors:
  the giant red initial (page 0), an embedded literal digit '7' on page 10
  (present in the transcription as '-7-': faithful!), and four decorative
  sentence-mark ornaments (double-bars + dot-diamond) on pages 22, 42, 52
  that occupy glyph-sized space but correspond to the '.' separator.
- ZERO transcription errors found. The rune content of
  data/liber-primus__transcription--master.txt is additionally
  byte-identical to the iddqd master, and page0-58.txt is an exact
  rune-substring of it.
"""

import pickle
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label as cc_label
from scipy.signal import fftconvolve

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
IMG = "/tmp/iddqd/liber-primus__images--unsolved"
FONT = "/tmp/iddqd/ttf/BabelStoneRunicBeorhtnoth.ttf"
W = 1600

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
rune_parts = [i for i, p in enumerate(parts) if any(c in AB for c in p)]

def page_lines(pg):
    return ["".join(c for c in ln if c in AB)
            for ln in parts[rune_parts[pg]].split("/")
            if any(c in AB for c in ln)]

def load_binary(pg):
    im = Image.open(f"{IMG}/{rune_parts[pg]}.jpg").convert("L")
    return np.asarray(im) < 140

def find_bands(binary):
    rows = binary[:, 700:1700].sum(axis=1)
    on = rows >= 3
    bands = []
    i, h = 0, len(on)
    while i < h:
        if on[i]:
            j, gap = i, 0
            while j < h:
                if on[j]:
                    gap = 0
                else:
                    gap += 1
                    if gap > 12:
                        break
                j += 1
            bands.append((i, j - gap))
            i = j
        else:
            i += 1
    return [(a, b) for a, b in bands if 85 <= b - a <= 175]

def font_templates():
    font = ImageFont.truetype(FONT, 131)
    out = {}
    for r in AB:
        img = Image.new("L", (400, 400), 255)
        ImageDraw.Draw(img).text((100, 100), r, font=font, fill=0)
        a = np.asarray(img) < 128
        ys, xs = np.nonzero(a)
        t = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        timg = Image.fromarray((t * 255).astype("uint8"))
        w = max(6, int(round(t.shape[1] * 0.73)))
        out[r] = (np.asarray(timg.resize((w, t.shape[0]), Image.LANCZOS))
                  > 100).astype(np.float32)
    return out

def band_resp(band, tmpl):
    b = band.astype(np.float32)
    need = max(t.shape[0] for t in tmpl.values()) + 2
    if b.shape[0] < need:
        b = np.vstack([b, np.zeros((need - b.shape[0], b.shape[1]),
                                   np.float32)])
    out = {}
    for r, t in tmpl.items():
        ov = fftconvolve(b, t[::-1, ::-1], mode="valid")
        v = (2 * ov - t.sum()).max(axis=0)
        R = np.full(W, -1e18)
        R[:min(len(v), W)] = v[:W]
        out[r] = R
    return out

def align(line, resp, tmpl):
    k = len(line)
    layers = []
    fprev = None
    for idx, r in enumerate(line):
        f = resp[r].copy()
        if idx > 0:
            tw = tmpl[line[idx - 1]].shape[1]
            g = np.full(W, -1e18)
            for off in range(max(1, tw - 6), tw + 91):
                g[off:] = np.maximum(g[off:], fprev[:W - off])
            f = f + g
        layers.append(f.copy())
        fprev = f
    end = int(np.argmax(fprev))
    xs = [0] * k
    xs[-1] = end
    for idx in range(k - 1, 0, -1):
        tw = tmpl[line[idx - 1]].shape[1]
        lo = max(0, xs[idx] - (tw + 90))
        hi = max(lo, xs[idx] - max(1, tw - 6))
        seg = layers[idx - 1][lo:hi + 1]
        xs[idx - 1] = lo + int(np.argmax(seg))
    return xs

def match_lines_to_bands(lines, bands, binary, tmpl):
    """Monotone matching: for each line pick best band after previous."""
    out = []
    bi = 0
    cache = {}
    for line in lines:
        best = None
        for cand in range(bi, min(bi + 7, len(bands))):
            y0, y1 = bands[cand]
            band = binary[max(0, y0 - 3):y1 + 3, 430:1970]
            if cand not in cache:
                cache[cand] = band_resp(band, tmpl)
            resp = cache[cand]
            xs = align(line, resp, tmpl)
            cover = np.mean([
                (resp[r][x] + tmpl[r].sum()) / (2 * tmpl[r].sum())
                for r, x in zip(line, xs)])
            if best is None or cover > best[0]:
                best = (cover, cand, xs, resp, band)
            if cover > 0.9:
                break
        if best is None or best[0] < 0.55:
            out.append(None)
            continue
        bi = best[1] + 1
        out.append(best)
    return out

MODE = sys.argv[1]

if MODE == "harvest2":
    with open("/tmp/native.pkl", "rb") as f:
        native = {r: v.astype(np.float32) for r, v in pickle.load(f).items()}
    tmpl = font_templates()
    tmpl.update(native)  # mixed: native where available
    crops = {r: [] for r in AB}
    for pg in range(57):
        lines = page_lines(pg)
        binary = load_binary(pg)
        bands = find_bands(binary)
        res = match_lines_to_bands(lines, bands, binary, tmpl)
        kept = 0
        for line, r_ in zip(lines, res):
            if r_ is None:
                continue
            cover, cand, xs, resp, band = r_
            covs = [(resp[r][x] + tmpl[r].sum()) / (2 * tmpl[r].sum())
                    for r, x in zip(line, xs)]
            for gi, (r, x) in enumerate(zip(line, xs)):
                left_ok = gi == 0 or covs[gi - 1] > 0.72
                right_ok = gi == len(line) - 1 or covs[gi + 1] > 0.72
                if not (left_ok and right_ok):
                    continue
                w = tmpl[r].shape[1]
                # extract between this x and next glyph x (or x+w+6)
                x2 = xs[gi + 1] if gi + 1 < len(xs) else x + w + 6
                sub = band[:, x:min(x2 - 2, x + w + 10)]
                if sub.shape[1] < 6:
                    continue
                # remove small detached components (separator dots, specks)
                lab, nlab = cc_label(sub > 0)
                keep = np.zeros_like(sub)
                for li in range(1, nlab + 1):
                    m = lab == li
                    if m.sum() >= 420:
                        keep[m] = 1
                sub = keep
                cols = np.nonzero(sub.sum(axis=0))[0]
                if len(cols) == 0:
                    continue
                sub = sub[:, cols[0]:cols[-1] + 1]
                if sub.sum() < 150:
                    continue
                crops[r].append(sub.astype(np.float32))
                kept += 1
        print(f"page {pg}: {kept}", flush=True)
    with open("/tmp/harvest.pkl", "wb") as f:
        pickle.dump(crops, f)
    for r in AB:
        print(ENG[c3301.r2i(r)], len(crops[r]))


if MODE == "harvest":
    tmpl = font_templates()
    crops = {r: [] for r in AB}
    for pg in range(57):
        lines = page_lines(pg)
        binary = load_binary(pg)
        bands = find_bands(binary)
        res = match_lines_to_bands(lines, bands, binary, tmpl)
        kept = 0
        for line, r_ in zip(lines, res):
            if r_ is None:
                continue
            cover, cand, xs, resp, band = r_
            for _gi, (r, x) in enumerate(zip(line, xs)):
                t = tmpl[r]
                c = (resp[r][x] + t.sum()) / (2 * t.sum())
                if c < 0.68:
                    continue
                # neighbors must not overlap badly
                w = t.shape[1]
                sub = band[:, x:x + w]
                if sub.shape[1] != w:
                    continue
                ys2, xs2 = np.nonzero(sub)
                if len(ys2) < 100:
                    continue
                crops[r].append(sub.astype(np.float32))
                kept += 1
        print(f"page {pg}: harvested {kept}", flush=True)
    with open("/tmp/harvest.pkl", "wb") as f:
        pickle.dump(dict(crops), f)
    for r in AB:
        print(ENG[c3301.r2i(r)], len(crops[r]))

elif MODE == "build":
    with open("/tmp/harvest.pkl", "rb") as f:
        crops = pickle.load(f)
    ftw = {r: max(6, int(round(t.shape[1] * 0.73)))
           for r, t in font_templates().items()}
    native = {}
    for r, lst in crops.items():
        lst = [c for c in lst
               if 0.55 * ftw[r] <= c.shape[1] <= 1.45 * ftw[r]]
        if len(lst) < 3:
            print(f"WARNING {ENG[c3301.r2i(r)]}: only {len(lst)} exemplars")
            continue
        h = max(c.shape[0] for c in lst)
        w = int(np.median([c.shape[1] for c in lst]))
        acc = np.zeros((h, w), np.float32)
        cnt = 0
        for c in lst:
            if abs(c.shape[1] - w) > 6:
                continue
            cc = np.zeros((h, w), np.float32)
            ch = min(c.shape[0], h)
            cw = min(c.shape[1], w)
            cc[:ch, :cw] = c[:ch, :cw]
            acc += cc
            cnt += 1
        t = (acc / cnt) > 0.5
        ys, xs = np.nonzero(t)
        native[r] = t[ys.min():ys.max() + 1,
                      xs.min():xs.max() + 1].astype(np.float32)
        print(f"{ENG[c3301.r2i(r)]}: {cnt} exemplars, "
              f"template {native[r].shape}")
    with open("/tmp/native.pkl", "wb") as f:
        pickle.dump(native, f)

elif MODE == "verify":
    with open("/tmp/native.pkl", "rb") as f:
        native = {r: v.astype(np.float32) for r, v in pickle.load(f).items()}
    start, stop = int(sys.argv[2]), int(sys.argv[3])
    for pg in range(start, stop):
        lines = page_lines(pg)
        binary = load_binary(pg)
        bands = find_bands(binary)
        res = match_lines_to_bands(lines, bands, binary, native)
        covers = []
        flags = []
        for ln, (line, r_) in enumerate(zip(lines, res)):
            if r_ is None:
                flags.append((ln, None, "UNALIGNED", 0, 0))
                continue
            cover, cand, xs, resp, band = r_
            covers.append(cover)
            for gi, (r, x) in enumerate(zip(line, xs)):
                t = native[r]
                sc = resp[r][x]
                c = (sc + t.sum()) / (2 * t.sum())
                slot = (xs[gi + 1] - x) if gi + 1 < len(xs) else t.shape[1] + 12
                altb, altr = -1e18, "?"
                for r2 in AB:
                    if r2 == r or native[r2].shape[1] > slot + 6:
                        continue
                    a2 = native[r2].sum()
                    v = resp[r2][max(0, x - 6):x + 7].max()
                    vc = (v + a2) / (2 * a2)
                    if vc > altb:
                        altb, altr = vc, r2
                if c < 0.93 and (c < 0.60 or altb > c + 0.10):
                    altn = ENG[c3301.r2i(altr)] if altr != "?" else "?"
                    flags.append((ln, gi, ENG[c3301.r2i(r)], c, altn))
        print(f"page {pg:2d}: mean cover "
              f"{np.mean(covers) if covers else 0:.3f}, "
              f"{len(flags)} flags", flush=True)
        for fl in flags:
            print(f"    line {fl[0]+1} pos "
                  f"{fl[1]+1 if fl[1] is not None else '-'}: "
                  f"{fl[2]} cover={fl[3] if isinstance(fl[3], float) else 0:.2f} "
                  f"alt={fl[4]}", flush=True)

if MODE == "inspect":
    # inspect page,line,pos: save crop of slot + claimed/alt templates
    with open("/tmp/native.pkl", "rb") as f:
        native = {r: v.astype(np.float32) for r, v in pickle.load(f).items()}
    pg, lnq, posq = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    lines = page_lines(pg)
    binary = load_binary(pg)
    bands = find_bands(binary)
    res = match_lines_to_bands(lines, bands, binary, native)
    line = lines[lnq - 1]
    r_ = res[lnq - 1]
    cover, cand, xs, resp, band = r_
    gi = posq - 1
    r, x = line[gi], xs[gi]
    x0 = max(0, x - 30)
    x1 = min(band.shape[1], x + native[r].shape[1] + 30)
    crop = band[:, x0:x1]
    t = native[r]
    eng = ENG[c3301.r2i(r)]
    H = max(crop.shape[0], t.shape[0])
    Wt = crop.shape[1] + t.shape[1] + 20
    c = np.zeros((H, Wt))
    c[:crop.shape[0], :crop.shape[1]] = crop
    c[:t.shape[0], crop.shape[1] + 20:crop.shape[1] + 20 + t.shape[1]] = t
    out = f"/tmp/inspect_p{pg}_l{lnq}_g{posq}_{eng}.png"
    Image.fromarray((255 * (1 - c)).astype("uint8")).resize(
        (Wt * 2, H * 2), Image.NEAREST).save(out)
    print(out, "claimed", eng, "x", x)
