# ABOUTME: Builds a reviewable page covering every line of the LP, pairing the
# ABOUTME: scan against the transcription and collecting corrections as JSON.
"""A review tool for correcting the transcription line by line.

The mark inventory is wrong (`mark-glyph-inventory.md`): the scans carry
several distinct dot glyphs and the transcription records two characters, so
counts, types and some whole marks are lost. Fixing it needs every line looked
at, not only the ones a reader flags — a reader that misses a glyph class will
also miss the lines containing it.

So this emits all lines of all pages: a crop of the line, the reader's token
sequence and the transcription's, aligned column-for-column, plus the runes.
Corrections are typed straight into the page, kept in localStorage so a session
survives a reload, and exported as JSON for `apply_review.py` to consume.

Mark encoding, circled numerals throughout so the dot count is the identity:

    ① 1 dot (word separator)   ③ 3 dots   ④ 4 dots   ⑩ 10 dots   ⑬ 13 dots

The structural characters the project added itself are NOT dot marks and stay
as they are: `/` end of line, `%` end of page, `&` end of paragraph,
`$` end of section.

Usage:  python3 -m experiments.transcription_review
Output: review/transcription/index.html plus one crop per line.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from PIL import Image

from experiments.locate_marks import CORPUS, IMAGE_DIR
from experiments.page_reader import read_page

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review" / "transcription"
RUNE = re.compile(r"[ᚠ-᛿]")
PAGES = range(58)
MARGIN = 45

# dot count -> character. Unlisted counts render as ⑈ (unknown) for review.
CIRCLED = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦", 8: "⑧",
           9: "⑨", 10: "⑩", 11: "⑪", 12: "⑫", 13: "⑬", 14: "⑭", 15: "⑮"}
UNKNOWN = "⑈"
TXT_MARK = {"-": "①", ".": "④"}      # what the transcription's two characters mean


def circled(dots: int) -> str:
    return CIRCLED.get(dots, UNKNOWN)


def img_tokens(line) -> list[str]:
    return ["R" if g.kind == "R" else circled(g.dots)
            for g in line if g.kind != "t"]


def txt_tokens(text: str) -> list[str]:
    return ["R" if RUNE.match(c) else c for c in text if RUNE.match(c) or c in "-."]


def crop(page: int, line, path: Path) -> None:
    ys = [g.y for g in line]
    xs = [g.x for g in line]
    box = (max(0, min(xs) - MARGIN), max(0, min(ys) - MARGIN),
           min(2400, max(xs) + 170), min(3600, min(ys) + 114 + MARGIN))
    Image.open(IMAGE_DIR / f"{page}.jpg").convert("L").crop(box).save(path, optimize=True)


def row(tokens: list[str], other: list[str], kind: str) -> str:
    """One token per fixed-width cell so the two rows line up exactly."""
    cells = []
    for i, t in enumerate(tokens):
        mism = i >= len(other) or other[i] != t
        cls = "c bad" if mism else "c"
        cells.append(f"<span class='{cls}'>{html.escape(t)}</span>")
    return f"<div class='row'><span class='lbl'>{kind}</span>{''.join(cells)}</div>"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = CORPUS.read_text().split("%")
    entries, warned = [], 0

    for page in PAGES:
        lines = [line for line in blocks[page].split("\n") if RUNE.search(line)]
        bands = read_page(page)
        ok = len(bands) == len(lines)
        warned += 0 if ok else 1
        for idx in range(max(len(bands), len(lines))):
            band = bands[idx] if idx < len(bands) else None
            text = lines[idx] if idx < len(lines) else ""
            name = ""
            if band:
                name = f"p{page:02d}_l{idx:02d}.png"
                crop(page, band, OUT / name)
            it = img_tokens(band) if band else []
            tt = txt_tokens(text)
            entries.append({
                "page": page, "line": idx, "img": "".join(it), "txt": "".join(tt),
                "runes": text.rstrip("/"), "png": name, "aligned": ok,
                "differs": [TXT_MARK.get(c, c) for c in tt] != it,
            })

    body = [HEAD]
    for e in entries:
        it, tt = list(e["img"]), [TXT_MARK.get(c, c) for c in e["txt"]]
        flag = "" if e["aligned"] else " <b class='warn'>page alignment uncertain</b>"
        cls = "e differs" if e["differs"] else "e"
        body.append(
            f"<section class='{cls}' id='p{e['page']}l{e['line']}' "
            f"data-page='{e['page']}' data-line='{e['line']}'>"
            f"<h2>page {e['page']} &middot; line {e['line']}{flag}</h2>"
            + (f"<img loading='lazy' src='{e['png']}'>" if e["png"] else
               "<p class='warn'>no crop: reader found no band for this line</p>")
            + row(it, tt, "scan")
            + row(tt, it, "txt")
            + f"<div class='runes'>{html.escape(e['runes'])}</div>"
            + "<div class='ctl'>"
              "<button class='ok'>correct as transcribed</button>"
              "<button class='fix'>needs change</button>"
              f"<input class='val' placeholder='true sequence, e.g. RRR④RR①' "
              f"value='{html.escape(e['img'])}'>"
              "<input class='note' placeholder='note'>"
              "<span class='state'></span></div></section>")
    body.append(FOOT.replace("__TOTAL__", str(len(entries))))
    (OUT / "index.html").write_text("\n".join(body), encoding="utf-8")

    (OUT / "entries.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    print(f"{len(entries)} lines written to {OUT}")
    print(f"   {sum(1 for e in entries if e['differs'])} differ from the transcription")
    print(f"   {warned} pages where the reader's band count disagrees with the text")
    print(f"\nopen {OUT / 'index.html'}")


HEAD = """<meta charset='utf-8'><title>LP transcription review</title>
<style>
 body{font:15px/1.5 system-ui;margin:0;padding:1rem 2rem 6rem;max-width:1600px}
 h1{font-size:20px}
 section{border-top:1px solid #ddd;padding:1.2rem 0}
 section.differs{background:#fffdf5}
 h2{font-size:19px;margin:0 0 .5rem;font-weight:600}
 .warn{color:#b00}
 img{max-width:100%;border:1px solid #ccc;display:block;margin:.4rem 0}
 .row{font:20px/1.35 ui-monospace,Menlo,Consolas,monospace;white-space:nowrap;
      overflow-x:auto}
 .lbl{display:inline-block;width:4.5ch;color:#888;font-size:14px}
 .c{display:inline-block;width:1.35ch;text-align:center}
 .bad{background:#ffd9d9;color:#b00;font-weight:700}
 .runes{font:19px/1.4 serif;color:#333;margin:.35rem 0 .6rem;word-break:break-all}
 .ctl{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}
 button{font:14px system-ui;padding:.3rem .7rem;cursor:pointer}
 .val{font:16px ui-monospace,Menlo,monospace;flex:1;min-width:22rem;padding:.3rem}
 .note{font:14px system-ui;width:16rem;padding:.3rem}
 .state{font-size:13px;color:#080;min-width:9rem}
 #bar{position:fixed;bottom:0;left:0;right:0;background:#222;color:#fff;
      padding:.6rem 2rem;display:flex;gap:1.5rem;align-items:center;font-size:14px}
 #bar button{background:#fff}
</style>
<h1>Liber Primus transcription review</h1>
<p>Rows line up column for column. <b>scan</b> is what the reader sees,
<b>txt</b> is the transcription mapped onto the same alphabet
(<code>-</code>&rarr;&#9312;, <code>.</code>&rarr;&#9315;). Red cells differ.
Marks are circled by dot count: &#9312;1 &#9314;3 &#9315;4 &#9321;10 &#9324;13,
&#9288; unrecognised. Highlighted sections are the ones that disagree.</p>"""

FOOT = """<div id='bar'>
 <span id='count'>0 / __TOTAL__ reviewed</span>
 <button onclick='save()'>download review.json</button>
 <button onclick='if(confirm("clear all verdicts?")){localStorage.clear();location.reload()}'>clear</button>
 <span>verdicts autosave in this browser</span></div>
<script>
const K='lp-review';
const store=JSON.parse(localStorage.getItem(K)||'{}');
function key(s){return s.dataset.page+':'+s.dataset.line}
function paint(s){
  const r=store[key(s)], st=s.querySelector('.state');
  st.textContent = r ? (r.verdict==='ok'?'\\u2713 confirmed':'\\u270e corrected') : '';
  s.style.opacity = r ? .72 : 1;
}
function count(){
  document.getElementById('count').textContent =
    Object.keys(store).length+' / __TOTAL__ reviewed';
}
function put(s,verdict){
  store[key(s)]={page:+s.dataset.page,line:+s.dataset.line,verdict:verdict,
    value:s.querySelector('.val').value, note:s.querySelector('.note').value};
  localStorage.setItem(K,JSON.stringify(store)); paint(s); count();
}
document.querySelectorAll('section').forEach(s=>{
  const r=store[key(s)];
  if(r){ s.querySelector('.val').value=r.value; s.querySelector('.note').value=r.note||''; }
  s.querySelector('.ok').onclick=()=>put(s,'ok');
  s.querySelector('.fix').onclick=()=>put(s,'fix');
  paint(s);
});
count();
function save(){
  const rows=Object.values(store).sort((a,b)=>a.page-b.page||a.line-b.line);
  const b=new Blob([JSON.stringify(rows,null,1)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b); a.download='review.json'; a.click();
}
</script>"""


if __name__ == "__main__":
    main()
