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
CIRCLED_SET = set(CIRCLED.values()) | {UNKNOWN}
TXT_MARK = {"-": "①", ".": "④"}      # what the transcription's two characters mean


def circled(dots: int) -> str:
    return CIRCLED.get(dots, UNKNOWN)


def with_runes(scan: list[tuple[str, str]], txt: list[tuple[str, str]]) -> str:
    """The scan's mark structure carrying the transcription's actual runes.

    The scan cannot name a rune, but the transcription can, so an editable
    value shows real runes and circled marks rather than placeholders. Where the
    scan sees more runes than the transcription supplies, the surplus becomes
    `?`, which `apply_review.py` refuses — so the gap surfaces instead of being
    quietly filled.
    """
    supply = iter([c for c, _ in txt if c not in CIRCLED_SET])
    return "".join(c if c in CIRCLED_SET else next(supply, "?") for c, _ in scan)


def _kinds(tokens: list[tuple[str, str]]) -> list[str]:
    """Mark glyphs compared by identity, runes only as 'a rune sits here'."""
    return [c if c in CIRCLED_SET else "R" for c, _ in tokens]


def img_tokens(line) -> list[tuple[str, str]]:
    """(character, css class) per glyph. Runes cannot be identified from the
    scan, so they show as a placeholder — but colour and drop-cap size can be,
    and both are information the transcription does not carry."""
    out = []
    for g in line:
        if g.kind == "t":
            continue
        if g.kind != "R":
            out.append((circled(g.dots), "mark"))
        elif g.tall:
            out.append(("R", "red cap" if g.red else "cap"))
        else:
            out.append(("R", "red" if g.red else ""))
    return out


def txt_tokens(text: str) -> list[tuple[str, str]]:
    """The transcription's own characters: real runes, marks mapped across."""
    out = []
    for c in text:
        if RUNE.match(c):
            out.append((c, "rune"))
        elif c in TXT_MARK:
            out.append((TXT_MARK[c], "mark"))
    return out


def crop(page: int, line, path: Path) -> None:
    """Colour is kept: red runes are the point of several corrections, and a
    drop cap is taller than the body hand so the box has to grow for it."""
    ys = [g.y for g in line]
    xs = [g.x for g in line]
    height = 520 if any(g.kind == "R" and g.tall for g in line) else 114
    box = (max(0, min(xs) - MARGIN), max(0, min(ys) - MARGIN),
           min(2400, max(xs) + 170), min(3600, min(ys) + height + MARGIN))
    Image.open(IMAGE_DIR / f"{page}.jpg").crop(box).save(path, optimize=True)


def row(tokens: list[tuple[str, str]], other: list[tuple[str, str]], kind: str) -> str:
    """One token per fixed-width cell so the two rows line up exactly.

    A cell is flagged when the two rows disagree about what KIND of thing sits
    in that column — rune against mark, or one mark glyph against another.
    Rune identity is not compared, since the scan cannot supply it.
    """
    cells = []
    for i, (ch, cls) in enumerate(tokens):
        theirs = other[i][0] if i < len(other) else None
        mine_mark, their_mark = ch in CIRCLED_SET, theirs in CIRCLED_SET
        bad = theirs is None or mine_mark != their_mark or (mine_mark and ch != theirs)
        cells.append(f"<span class='c {cls}{' bad' if bad else ''}'>"
                     f"{html.escape(ch)}</span>")
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
                "page": page, "line": idx, "png": name, "aligned": ok,
                "img": it, "txt": tt,
                "scan": with_runes(it, tt),
                "text": "".join(c for c, _ in tt),
                "runes": text.rstrip("/"),
                "differs": _kinds(it) != _kinds(tt),
            })

    body = [HEAD]
    for e in entries:
        it, tt = e["img"], e["txt"]
        flag = "" if e["aligned"] else " <b class='warn'>page alignment uncertain</b>"
        cls = "e differs" if e["differs"] else "e"
        body.append(
            f"<section class='{cls}' id='p{e['page']}l{e['line']}' "
            f"data-page='{e['page']}' data-line='{e['line']}' "
            f"data-scan='{html.escape(e['scan'])}' data-txt='{html.escape(e['text'])}'>"
            f"<h2>page {e['page']} &middot; line {e['line']}{flag}</h2>"
            + (f"<img loading='lazy' src='{e['png']}'>" if e["png"] else
               "<p class='warn'>no crop: reader found no band for this line</p>")
            + row(it, tt, "scan")
            + row(tt, it, "txt")
            + "<div class='ctl'>"
              "<button class='b-txt'>txt row is right</button>"
              "<button class='b-scan'>scan row is right</button>"
              "<button class='b-edit'>use my edit &rarr;</button>"
              f"<input class='val' placeholder='runes and marks, e.g. ᚦᛖ①ᛗᚪᚾ④' "
              f"value='{html.escape(e['scan'])}'>"
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
 .rune{color:#111}
 .mark{color:#0057b8;font-weight:700}
 .red{color:#c00}
 .cap{outline:2px solid #c90;font-weight:700}
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
<b>txt</b> is the transcription itself &mdash; real runes, with its two mark
characters mapped across (<code>-</code>&rarr;&#9312;, <code>.</code>&rarr;&#9315;).
The scan cannot name a rune, so it shows <code>R</code>; red <code>R</code> is a
red rune and a boxed one is a drop cap, neither of which the transcription
records. Cells shaded red disagree about mark type.
The edit box holds real runes with circled marks. Marks are circled by dot count: &#9312;1 &#9314;3 &#9315;4 &#9321;10 &#9324;13,
&#9288; unrecognised. Highlighted sections are the ones that disagree.</p>\n<p><b>Which button?</b> <code>txt row is right</code> keeps the existing\ntranscription. <code>scan row is right</code> takes the reader's version,\nwhich is what you want when the reader spotted a mark the transcription got\nwrong. <code>use my edit</code> stores whatever is in the box, pre-filled with\nthe scan reading. Whichever you press, the stored sequence is exactly what the\nline will become.</p>"""

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
function put(s,source){
  const v = source==='txt'  ? s.dataset.txt
          : source==='scan' ? s.dataset.scan
          :                   s.querySelector('.val').value;
  store[key(s)]={page:+s.dataset.page,line:+s.dataset.line,source:source,
    value:v, note:s.querySelector('.note').value};
  localStorage.setItem(K,JSON.stringify(store)); paint(s); count();
}
document.querySelectorAll('section').forEach(s=>{
  const r=store[key(s)];
  if(r){ s.querySelector('.val').value=r.value; s.querySelector('.note').value=r.note||''; }
  s.querySelector('.b-txt').onclick=()=>put(s,'txt');
  s.querySelector('.b-scan').onclick=()=>put(s,'scan');
  s.querySelector('.b-edit').onclick=()=>put(s,'edit');
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
