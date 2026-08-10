# ABOUTME: Exports every image-vs-transcription discrepancy as a cropped line
# ABOUTME: image plus an HTML contact sheet, for manual adjudication.
"""Build a review sheet of every line where the scan and the transcription differ.

`boundary_verification.py` finds 113 mismatching lines but cannot adjudicate
them: 92 involve the connected-component reader merging touching runes, and
spot-checking the line-edge cases found one genuine omission and one piece of
marginal artwork misread as a dot. A human can settle each in seconds.

So this writes, for every discrepancy, a tight crop of the line at native
resolution plus what the reader saw and what the transcription says, into an
HTML sheet that opens straight from disk.

Classes, most decision-relevant first:

  separator   the rune counts agree but the separators do not — the cases that
              bear on boundary authenticity
  trailing    the reader sees a separator past the end of the transcribed line
  reader      the rune counts differ, so the reader is probably at fault; still
              worth a look, since the alternative is a transcription rune error

Output: review/boundary/index.html plus one PNG per line. Not committed —
regenerate with `python3 -m experiments.boundary_review_sheet`.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image

from aldegonde import c3301
from experiments.locate_marks import (
    CORPUS,
    IMAGE_DIR,
    bands,
    glyphs,
    text_lines,
    tokens,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review" / "boundary"
RUNE = re.compile(r"[ᚠ-᛿]")
PAGES = range(58)
MARGIN = 45
ORDER = {"separator": 0, "trailing": 1, "reader": 2}


def classify(img: list[str], txt: list[str]) -> str | None:
    if img == txt:
        return None
    if img[: len(txt)] == txt and all(t in c3301.MARK_CHARS for t in img[len(txt) :]):
        return "trailing"
    return "reader" if img.count("R") != txt.count("R") else "separator"


def crop(page: int, line: list, path: Path) -> None:
    ys = [g[1] for g in line]
    xs = [g[2] for g in line]
    box = (
        max(0, min(xs) - MARGIN),
        max(0, min(ys) - MARGIN),
        min(2400, max(xs) + 160),
        min(3600, min(ys) + 114 + MARGIN),
    )
    Image.open(IMAGE_DIR / f"{page}.jpg").convert("L").crop(box).save(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = CORPUS.read_text().split("%")
    rows = []

    for page in PAGES:
        lines = text_lines(blocks[page])
        img_lines = bands(glyphs(page), len(lines))
        if len(img_lines) != len(lines):
            continue
        for idx, (line, text) in enumerate(zip(img_lines, lines)):
            img = [t for t in tokens(line) if t not in "'\""]
            txt = [
                "R" if RUNE.match(c) else c
                for c in text
                if RUNE.match(c) or c in c3301.MARK_CHARS
            ]
            kind = classify(img, txt)
            if kind is None:
                continue
            name = f"p{page:02d}_l{idx:02d}_{kind}.png"
            crop(page, line, OUT / name)
            rows.append(
                (
                    ORDER[kind],
                    page,
                    idx,
                    kind,
                    name,
                    "".join(img),
                    "".join(txt),
                    text.rstrip("/"),
                )
            )

    rows.sort()
    counts = {k: sum(1 for r in rows if r[3] == k) for k in ORDER}
    parts = [
        "<meta charset='utf-8'><title>LP boundary discrepancies</title>",
        "<style>body{font:14px/1.5 system-ui;margin:2rem;max-width:1500px}"
        "h2{margin:2.5rem 0 .3rem;font-size:15px}img{max-width:100%;border:1px solid #ccc}"
        "code{font:13px ui-monospace;background:#f4f4f4;padding:1px 4px}"
        ".r{color:#b00}.sep{border-left:4px solid #b00;padding-left:12px}"
        ".trailing{border-left:4px solid #d80;padding-left:12px}"
        ".reader{border-left:4px solid #999;padding-left:12px}</style>",
        "<h1>Scan vs transcription: lines that disagree</h1>",
        f"<p>{len(rows)} lines. <b>separator</b> {counts['separator']} "
        f"(rune counts agree, separators differ — these bear on boundary "
        f"authenticity); <b>trailing</b> {counts['trailing']} (reader sees a "
        f"separator past the transcribed line end); <b>reader</b> "
        f"{counts['reader']} (rune counts differ, reader probably at fault).</p>",
        "<p><code>R</code> rune, <code>-</code> word separator, "
        "<code>.</code> sentence mark. <b>img</b> is what the reader saw, "
        "<b>txt</b> is the transcription.</p>",
    ]
    for _, page, idx, kind, name, img, txt, raw in rows:
        css = "sep" if kind == "separator" else kind
        parts.append(f"<h2 class='{css}'>page {page} line {idx} &mdash; {kind}</h2>")
        parts.append(
            f"<div><code>img</code> <code>{html.escape(img)}</code><br>"
            f"<code>txt</code> <code>{html.escape(txt)}</code><br>"
            f"<code>{html.escape(raw)}</code></div>"
        )
        parts.append(f"<img src='{name}'>")

    (OUT / "index.html").write_text("\n".join(parts), encoding="utf-8")
    print(f"{len(rows)} discrepancies written to {OUT}")
    for k, v in counts.items():
        print(f"   {k:>10}: {v}")
    print(f"\nopen {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
