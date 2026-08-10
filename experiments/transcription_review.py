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

import difflib
import html
import json
import re
import sys
from pathlib import Path

from PIL import Image

from aldegonde import c3301
from experiments.locate_marks import CORPUS, IMAGE_DIR
from experiments.page_reader import read_page, with_ticks

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review" / "transcription"
RUNE = re.compile(r"[ᚠ-᛿]")
CONTENT = re.compile(r"[0-9A-Za-z]")
PAGES = range(58)
MARGIN = 45

# dot count -> character. Unlisted counts render as ⑈ (unknown) for review.
CIRCLED = {n: chr(0x2460 + n - 1) for n in range(1, 21)}
CIRCLED.update({n: chr(0x3251 + n - 21) for n in range(21, 36)})
UNKNOWN = "⑈"
CIRCLED_SET = set(CIRCLED.values()) | {UNKNOWN}
# The transcription now encodes each mark by its dot count. `-` and `.` are
# the legacy pair and still appear on lines not yet migrated, so both map.
TXT_MARK = {c: c for c in CIRCLED.values()}
TXT_MARK.update({"-": "①", ".": "④"})


def circled(dots: int) -> str:
    return CIRCLED.get(dots, UNKNOWN)


def fill_runes(scan: list[tuple[str, str]],
               txt: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """The scan's structure carrying the transcription's actual runes.

    The scan cannot name a rune, but it does know where one sits, and the
    transcription can name it. Filling them in order makes the scan row
    readable as a line instead of a row of placeholders, and it makes a drift
    obvious: once the two disagree about a mark, every later column shows the
    same rune in different places.

    Where the scan sees more runes than the transcription supplies, the surplus
    becomes `?` — flagged here and refused by `apply_review.py`, so the gap
    surfaces rather than being quietly filled.
    """
    supply = iter([c for c, _ in txt if c not in CIRCLED_SET and c not in "'\""])
    out = []
    for c, cls in scan:
        if c in CIRCLED_SET or c in "'\"":
            out.append((c, cls))
        else:
            r = next(supply, "?")
            out.append((r, f"{cls} miss".strip() if r == "?" else cls))
    return out


GAP = 0.72        # cost of leaving a band or a line unpaired


def align(bands: list, lines: list[str]) -> list[tuple]:
    """Pair reader bands to transcription lines by shape, allowing gaps.

    Pairing by index fails the moment the reader gains or loses a band: every
    later line is then compared against the wrong text and the rest of the page
    becomes unreviewable, which is what made the middle of the book impossible
    to correct. The transcription is reliable, so its line shapes are a good
    signature to align against — a Needleman-Wunsch over the token kinds, with
    gaps for a band the text has no line for and vice versa.
    """
    bs = ["".join("R" if g.kind == "R" else "M"
                  for g in with_ticks(b) if g.kind != "t") for b in bands]
    ls = ["".join("R" if RUNE.match(c) or CONTENT.match(c) else "M"
                  for c in line if RUNE.match(c) or CONTENT.match(c) or c in c3301.MARK_CHARS)
          for line in lines]
    n, m = len(bs), len(ls)
    inf = float("inf")
    cost = [[inf] * (m + 1) for _ in range(n + 1)]
    back: list[list] = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            here = cost[i][j]
            if here == inf:
                continue
            if i < n and j < m:
                d = 1.0 - difflib.SequenceMatcher(None, bs[i], ls[j]).ratio()
                if here + d < cost[i + 1][j + 1]:
                    cost[i + 1][j + 1], back[i + 1][j + 1] = here + d, (i, j, "M")
            if i < n and here + GAP < cost[i + 1][j]:
                cost[i + 1][j], back[i + 1][j] = here + GAP, (i, j, "B")
            if j < m and here + GAP < cost[i][j + 1]:
                cost[i][j + 1], back[i][j + 1] = here + GAP, (i, j, "L")
    out, i, j = [], n, m
    while i or j:
        pi, pj, op = back[i][j]
        if op == "M":
            out.append((bands[pi], lines[pj], pj))
        elif op == "B":
            out.append((bands[pi], None, None))
        else:
            out.append((None, lines[pj], pj))
        i, j = pi, pj
    return list(reversed(out))


def _kinds(tokens: list[tuple[str, str]]) -> list[str]:
    """Mark glyphs compared by identity, runes only as 'a rune sits here'."""
    return [c if c in CIRCLED_SET else "R" for c, _ in tokens]


def img_tokens(line) -> list[tuple[str, str]]:
    """(character, css class) per glyph. Runes cannot be identified from the
    scan, so they show as a placeholder — but colour and drop-cap size can be,
    and both are information the transcription does not carry."""
    out = []
    for g in with_ticks(line):
        if g.kind in "'\"":
            out.append((g.kind, "tick"))
        elif g.kind == "M":
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
        if RUNE.match(c) or CONTENT.match(c):
            out.append((c, "rune" if RUNE.match(c) else "content"))
        elif c in TXT_MARK:
            out.append((TXT_MARK[c], "mark"))
        elif c in "'\"":
            out.append((c, "tick"))
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

    A cell is flagged whenever the two rows differ in that column. Since the
    scan row is filled with the transcription's own runes, a disagreement about
    one mark drifts every column after it, which is exactly the thing to see.
    """
    cells = []
    for i, (ch, cls) in enumerate(tokens):
        theirs = other[i][0] if i < len(other) else None
        bad = theirs != ch
        cells.append(f"<span class='c {cls}{' bad' if bad else ''}'>"
                     f"{html.escape(ch)}</span>")
    return f"<div class='row'><span class='lbl'>{kind}</span>{''.join(cells)}</div>"


def check_script(page: str) -> None:
    """Refuse to write a page whose script does not parse.

    FOOT is an ordinary Python string, so a `\\n` meant for JavaScript becomes a
    real newline and silently breaks a string literal — which disabled every
    button on the page, not just the feature being added. A syntax error is
    invisible until the page is opened, so it is checked here instead.
    """
    import shutil
    import subprocess
    import tempfile

    node = shutil.which("node")
    if not node:
        print("   (node not found: script not syntax-checked)")
        return
    script = re.search(r"<script>(.*?)</script>", page, re.S)
    if not script:
        return
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script.group(1))
        path = fh.name
    done = subprocess.run([node, "--check", path], capture_output=True, text=True)
    Path(path).unlink()
    if done.returncode:
        sys.exit(f"generated script does not parse:\n{done.stderr}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = CORPUS.read_text().split("%")
    entries, warned = [], 0

    for page in PAGES:
        lines = [line for line in blocks[page].split("\n") if RUNE.search(line)]
        bands = read_page(page)
        warned += 0 if len(bands) == len(lines) else 1
        for slot, (band, text, lineno) in enumerate(align(bands, lines)):
            text = text or ""
            idx = lineno if lineno is not None else f"~{slot}"
            ok = lineno is not None and band is not None
            name = ""
            if band:
                name = f"p{page:02d}_s{slot:02d}.png"
                crop(page, band, OUT / name)
            tt = txt_tokens(text)
            it = fill_runes(img_tokens(band), tt) if band else []
            entries.append({
                "page": page, "line": idx, "png": name, "aligned": ok,
                "img": it, "txt": tt,
                "scan": "".join(c for c, _ in it),
                "text": "".join(c for c, _ in tt),
                "runes": text.rstrip("/"),
                "differs": _kinds(it) != _kinds(tt),
                "slot": slot,
            })

    body = [HEAD]
    for e in entries:
        it, tt = e["img"], e["txt"]
        flag = "" if e["aligned"] else (
            " <b class='warn'>unpaired: "
            + ("no transcription line for this scanned line" if e["png"]
               else "no scanned line for this transcription line") + "</b>")
        cls = "e differs" if e["differs"] or not e["aligned"] else "e agrees"
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
    html_text = "\n".join(body)
    check_script(html_text)
    (OUT / "index.html").write_text(html_text, encoding="utf-8")

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
 .row{font:29px/1.45 ui-monospace,Menlo,Consolas,monospace;white-space:nowrap;
      overflow-x:auto}
 .lbl{display:inline-block;width:4.5ch;color:#888;font-size:15px}
 .c{display:inline-block;width:1.4ch;text-align:center}
 .bad{background:#ffd9d9;color:#b00;font-weight:700}
 .rune{color:#111}
 .mark{color:#0057b8;font-weight:700}
 .red{color:#c00}
 .miss{background:#fdd;color:#b00;font-weight:700}
 .tick{color:#7a4dbd;font-weight:700}
 .content{color:#087}
 .cap{outline:2px solid #c90;font-weight:700}
 .ctl{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}
 button{font:14px system-ui;padding:.3rem .7rem;cursor:pointer}
 .val{font:21px ui-monospace,Menlo,monospace;flex:1;min-width:26rem;padding:.35rem}
 .note{font:14px system-ui;width:16rem;padding:.3rem}
 .state{font-size:13px;color:#080;min-width:9rem}
 #bar{position:fixed;bottom:0;left:0;right:0;background:#222;color:#fff;
      padding:.6rem 2rem;display:flex;gap:1.5rem;align-items:center;font-size:14px}
 #bar button{background:#fff}
 body.only-diff section.agrees{display:none}
 body.only-todo section.reviewed{display:none}
 #bar label{display:flex;gap:.4rem;align-items:center;cursor:pointer}
 #bar .imp{background:#fff;color:#222;padding:.3rem .7rem}
</style>
<h1>Liber Primus transcription review</h1>
<p>Rows line up column for column. <b>scan</b> is what the reader sees,
<b>txt</b> is the transcription itself &mdash; real runes, with its two mark
characters mapped across (<code>-</code>&rarr;&#9312;, <code>.</code>&rarr;&#9315;).
The scan row carries the transcription's runes in the positions the scan sees
them, so a mark it reads differently drifts every column after it. A rune shown
in red is red on the page and a boxed one is a drop cap, neither of which the
transcription records; <code>?</code> means the scan saw a rune the
transcription has no character for. Cells shaded red disagree about mark type.
The edit box holds real runes with circled marks; you can also type <code>(23)</code> for a 23-dot mark and it will be converted. Marks are circled by dot count: &#9312;1 &#9314;3 &#9315;4 &#9321;10 &#9324;13,
&#9288; unrecognised. Highlighted sections are the ones that disagree.</p>\n<p><b>Which button?</b> <code>txt row is right</code> keeps the existing\ntranscription. <code>scan row is right</code> takes the reader's version,\nwhich is what you want when the reader spotted a mark the transcription got\nwrong. <code>use my edit</code> stores whatever is in the box, pre-filled with\nthe scan reading. Whichever you press, the stored sequence is exactly what the\nline will become.</p>"""

FOOT = """<div id='bar'>
 <label><input type='checkbox' id='only' onchange='filter()'>
   only lines that disagree</label>
 <label><input type='checkbox' id='todo' onchange='filter()'>
   only lines not yet reviewed</label>
 <span id='shown'></span>
 <span id='count'>0 / __TOTAL__ reviewed</span>
 <button onclick='save()'>download review.json</button>
 <label class='imp'>load review.json
   <input type='file' accept='.json' onchange='load(this)' hidden></label>
 <button onclick='wipe()'>clear</button>
 <span id='msg'>verdicts autosave in this browser</span></div>
<script>
const K='lp-review';
const store=JSON.parse(localStorage.getItem(K)||'{}');
function key(s){return s.dataset.page+':'+s.dataset.line}
function paint(s){
  const r=store[key(s)], st=s.querySelector('.state');
  s.classList.toggle('reviewed', !!r);
  st.textContent = r ? {txt:'\\u2713 txt kept', scan:'\\u2713 scan taken',
                        edit:'\\u270e edited'}[r.source] : '';
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
  store[key(s)]={page:+s.dataset.page,line:s.dataset.line,source:source,
    value:v, note:s.querySelector('.note').value};
  localStorage.setItem(K,JSON.stringify(store)); paint(s); count(); filter();
}
document.querySelectorAll('section').forEach(s=>{
  const r=store[key(s)];
  if(r){ s.querySelector('.val').value=r.value; s.querySelector('.note').value=r.note||''; }
  s.querySelector('.b-txt').onclick=()=>put(s,'txt');
  s.querySelector('.b-scan').onclick=()=>put(s,'scan');
  s.querySelector('.b-edit').onclick=()=>put(s,'edit');
  paint(s);
});
function filter(){
  const diff = document.getElementById('only').checked;
  const todo = document.getElementById('todo').checked;
  document.body.classList.toggle('only-diff', diff);
  document.body.classList.toggle('only-todo', todo);
  localStorage.setItem(K+'-only', diff ? '1' : '');
  localStorage.setItem(K+'-todo', todo ? '1' : '');
  const sel = 'section' + (diff ? '.differs' : '') + (todo ? ':not(.reviewed)' : '');
  document.getElementById('shown').textContent =
    document.querySelectorAll(sel).length + ' lines shown';
}
document.getElementById('only').checked = !!localStorage.getItem(K+'-only');
document.getElementById('todo').checked = !!localStorage.getItem(K+'-todo');
filter();
count();
function wipe(){
  if(!confirm('Clear every verdict in this browser?\\n\\n'
     +Object.keys(store).length+' will be lost. Download first if unsure.')) return;
  if(!confirm('Really clear? This cannot be undone from the page.')) return;
  localStorage.removeItem(K); location.reload();
}
function load(input){
  const f=input.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{
    let rows; try{ rows=JSON.parse(r.result); }
    catch(e){ document.getElementById('msg').textContent='not valid JSON'; return; }
    let n=0;
    rows.forEach(v=>{ store[v.page+':'+v.line]=v; n++; });
    localStorage.setItem(K,JSON.stringify(store));
    document.getElementById('msg').textContent='loaded '+n+' verdicts';
    document.querySelectorAll('section').forEach(s=>{
      const q=store[key(s)];
      if(q){ s.querySelector('.val').value=q.value;
             s.querySelector('.note').value=q.note||''; }
      paint(s);
    });
    count(); filter();
  };
  r.readAsText(f);
}
function save(){
  // rebuild page and line from the store KEY: an early version coerced an
  // slot id of an unpaired band, e.g. ~9, with + and wrote null, losing which band a
  // verdict belonged to. The key was always right, so repair from it.
  const rows=Object.entries(store).map(([k,v])=>{
    const i=k.indexOf(':');
    return Object.assign({},v,{page:+k.slice(0,i),line:k.slice(i+1)});
  }).sort((a,b)=>a.page-b.page||String(a.line).localeCompare(String(b.line),
      undefined,{numeric:true}));
  const b=new Blob([JSON.stringify(rows,null,1)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b); a.download='review.json'; a.click();
}
</script>"""


if __name__ == "__main__":
    main()
