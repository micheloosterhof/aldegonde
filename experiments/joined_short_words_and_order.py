# ABOUTME: Joins named short words (THE, A, ...) to the following word in English and asks
# ABOUTME: whether that reproduces the body's block lengths AND its missing length order.
"""Does writing short words joined explain the order of the blocks as well as their lengths?

Two things about the body's blocks are not English: the length marginal has a hole at two
runes, and the lengths carry no order (neighbours inside a span are independent, and a
span does not end on a long block). `short-units-are-written-joined.md` joins units by
LENGTH at a fitted rate. This script joins by IDENTITY, with no rate: the named words
are prefixed to the word that follows them, always. That is the reading "THE and A are
written onto their nouns".

Rules, from narrow to absurd: THE; THE and A; the articles; the articles with OF, then
TO, then IN; every word of one or two runes; every word of one to three runes. Each rule is run
forward on the author's own plaintext (the solved pages, with their sentence marks) and
on five prose registers, and three numbers are read:

  marginal   two-sample chi-square of the block lengths against the body's
  adjacency  `length_adjacency_self_null.score`: the transition table of neighbouring
             length classes inside a span against the text's OWN within-span shuffle
  final gap  mean length of a span's last block minus the mean of its interior blocks

The first is the combination question, the other two the ordering question. Both
references are read at matched size: prose is cut to windows of the body's block count,
and the body is cut to windows of the author's block count, so neither comparison
extrapolates a z across sample sizes.

The author's pages hold refrains (WHO ARE YOU WHO WISHES TO STUDY HERE stands five
times). A repeated sentence repeats its length transitions, which the adjacency
statistic counts as order, so the author's rows are given twice: all spans, and with
every span dropped that repeats a three-word run of an earlier span.

What the null keeps and destroys: the within-span shuffle keeps every span's multiset
of block lengths, so it keeps whatever the joining did to the marginal, and destroys
only the order inside the span. The adjacency z is in units of that shuffle's own
spread, so the body's windows are compared to the author's z in those units.

    python experiments/joined_short_words_and_order.py [workers]
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
import lp_plaintext_register  # noqa: E402
from length_adjacency_self_null import score, windows  # noqa: E402
from lp_plaintext_register import IDX, MASTER, PLAIN_PAGES, RUNE, TRIPLES  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import sentence_gap  # noqa: E402
from the_gap_depends_on_span_length import body_spans  # noqa: E402

from aldegonde import c3301  # noqa: E402

SEED = 20261112
TOP = 12  # length classes 1..11 and 12+
WINDOWS = 4  # windows of the body's size per prose register
BODY_WINDOWS = 12  # windows of the body at the author's size, per rule
NAMES = ("1-2", "3", "4", "5-6", "7+")  # the length classes of `score`
PROSE = REGISTERS[:5]
DRAWS = 200  # shuffles per window
AUTHOR_DRAWS = 1000  # shuffles for the body and the author's text: one corpus each
RULES: tuple[tuple[str, tuple[str, ...] | int], ...] = (
    ("as written", ()),
    ("THE", ("THE",)),
    ("THE, A", ("THE", "A")),
    ("THE, A, AN", ("THE", "A", "AN")),
    ("articles, OF", ("THE", "A", "AN", "OF")),
    ("articles, OF, TO", ("THE", "A", "AN", "OF", "TO")),
    ("articles, OF, TO, IN", ("THE", "A", "AN", "OF", "TO", "IN")),
    ("every word of 1 or 2 runes", 2),
    ("every word of 1 to 3 runes", 3),
)

Word = tuple[int, ...]


def author_word_spans() -> list[list[Word]]:
    """The author's plaintext words, grouped into the runs a period closes."""
    pages = MASTER.read_text().split("%")
    plain = {t["page"]: t["plaintext_runes"] for t in json.loads(TRIPLES.read_text())}
    spans: list[list[Word]] = []
    for n in sorted(set(PLAIN_PAGES) | set(plain)):
        runes = plain.get(n)
        k = 0
        current: list[Word] = []
        word: list[int] = []
        for ch in pages[n]:
            if RUNE.match(ch):
                word.append(runes[k] if runes is not None else IDX[ch])
                k += 1
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY:
                if word:
                    current.append(tuple(word))
                    word = []
                if ch == "." and current:
                    spans.append(current)
                    current = []
        if word:
            current.append(tuple(word))
        if current:
            spans.append(current)
    return spans


def prose_word_spans(path: Path) -> list[list[Word]]:
    """Sentences of a prose text as rune-index words, the outer tenths trimmed."""
    text = path.read_text(encoding="utf-8", errors="replace")
    trim = len(text) // 10
    cache: dict[str, Word] = {}
    out = []
    for sentence in re.split(r"[.!?]+", text[trim : len(text) - trim]):
        words = []
        for w in re.findall(r"[A-Za-z']+", sentence):
            w = w.upper()
            if w not in cache:
                cache[w] = tuple(c3301.encode_english(w))
            if cache[w]:
                words.append(cache[w])
        if len(words) >= 3:
            out.append(words)
    return out


def joined(span: list[Word], rule: tuple[str, ...] | int) -> list[int]:
    """Block lengths of one span with the rule's words prefixed to the word after them."""
    if isinstance(rule, int):

        def joins(w: Word) -> bool:
            return len(w) <= rule
    else:
        named = {tuple(c3301.encode_english(x)) for x in rule}

        def joins(w: Word) -> bool:
            return w in named

    out: list[int] = []
    carry = 0
    for i, w in enumerate(span):
        if joins(w) and i + 1 < len(span):
            carry += len(w)
        else:
            out.append(carry + len(w))
            carry = 0
    return out


def marginal(lengths: list[int], body: Counter, body_count: int) -> tuple[float, float]:
    """Two-sample chi-square of a model's block lengths against the body's, and its P."""
    counts = Counter(min(x, TOP) for x in lengths)
    size = len(lengths)
    stat = 0.0
    for k in range(1, TOP + 1):
        a, b = body[k], counts[k]
        if a + b == 0:
            continue
        ea = (a + b) * body_count / (body_count + size)
        eb = (a + b) * size / (body_count + size)
        stat += (a - ea) ** 2 / ea + (b - eb) ** 2 / eb
    return stat, float(chi2.sf(stat, TOP - 1))


def without_refrains(spans: list[list[Word]]) -> list[list[Word]]:
    """Spans that do not repeat a three-word run of an earlier span."""
    seen: set[tuple[Word, ...]] = set()
    kept = []
    for s in spans:
        runs = {tuple(s[i : i + 3]) for i in range(len(s) - 2)}
        if runs & seen:
            continue
        seen |= runs
        kept.append(s)
    return kept


def _adjacency(args):
    label, spans, seed, draws = args
    r = score(spans, random.Random(seed), draws=draws)
    with np.errstate(invalid="ignore", divide="ignore"):
        resid = np.nan_to_num((r["table"] - r["mean"]) / r["sd"])
    return label, r["z"], r["lag1"], resid


def main() -> None:
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rng = random.Random(SEED)

    def seed() -> int:
        return rng.randrange(1 << 30)

    body_words = lp_corpus.load_words(join_pages=True)
    body_marginal = Counter(min(len(w), TOP) for w in body_words)
    body = [s for s in body_spans() if len(s) >= 2]
    size = sum(len(s) for s in body)
    body_gap, body_gap_se, _ = sentence_gap(body)

    author = author_word_spans()
    # the same words as the register every other length test uses, here kept in order
    register = sorted(tuple(w) for w in lp_plaintext_register.corpus())
    if sorted(w for s in author for w in s) != register:
        msg = "author_word_spans disagrees with lp_plaintext_register.corpus"
        raise RuntimeError(msg)
    fresh = without_refrains(author)
    prose = {}
    for number in PROSE:
        path = fetch(number)
        if path is not None:
            prose[number] = prose_word_spans(path)

    tasks = [("body", body, seed(), AUTHOR_DRAWS)]
    lengths, gaps, sizes = {}, {}, {}
    prose_gap: dict[str, list[float]] = {}
    prose_short: dict[str, list[float]] = {}
    for name, rule in RULES:
        flat = [x for s in author for x in joined(s, rule)]
        stat, p = marginal(flat, body_marginal, len(body_words))
        lengths[name] = (
            len(flat),
            float(np.mean(flat)),
            flat.count(2) / len(flat),
            stat,
            p,
        )
        for label, source in (("author", author), ("fresh", fresh)):
            spans = [b for b in (joined(s, rule) for s in source) if len(b) >= 2]
            gaps[label, name] = sentence_gap(spans)[:2]
            sizes[label, name] = sum(len(b) for b in spans)
            tasks.append((f"{label}|{name}", spans, seed(), AUTHOR_DRAWS))
        for i, w in enumerate(windows(body, sizes["fresh", name], BODY_WINDOWS, rng)):
            tasks.append((f"body at|{name}|{i}", w, seed(), DRAWS))
        for number, sentences in prose.items():
            blocks = [b for b in (joined(s, rule) for s in sentences) if len(b) >= 2]
            prose_gap.setdefault(name, []).append(sentence_gap(blocks)[0])
            every = [x for b in blocks for x in b]
            prose_short.setdefault(name, []).append(every.count(2) / len(every))
            for i, w in enumerate(windows(blocks, size, WINDOWS, rng)):
                tasks.append((f"prose|{name}|{number}.{i}", w, seed(), DRAWS))

    with Pool(nproc) as pool:
        results = pool.map(_adjacency, tasks, chunksize=1)
    z = {label: (zz, r) for label, zz, r, _ in results}
    cells = {label: resid for label, _, _, resid in results}
    body_z, body_lag1 = z["body"]

    def group(prefix: str) -> tuple[np.ndarray, np.ndarray]:
        hit = [v for k, v in z.items() if k.startswith(prefix)]
        return np.array([v[0] for v in hit]), np.array([v[1] for v in hit])

    flat_body = [len(w) for w in body_words]
    print(
        f"the body: {len(body_words)} blocks, mean {np.mean(flat_body):.3f}, 2-rune share "
        f"{flat_body.count(2) / len(flat_body):.3f}; adjacency z {body_z:+.2f} (lag-1 r "
        f"{body_lag1:+.3f}); final gap {body_gap:+.2f} +- {body_gap_se:.2f}"
    )
    print(
        f"the author: {len(author)} spans, {sum(len(s) for s in author)} words; without "
        f"refrains {len(fresh)} spans, {sum(len(s) for s in fresh)} words\n"
    )

    print("1. Lengths: the author's words with each rule run forward, against the body")
    print(
        f"  {'words joined to the next word':<30}{'blocks':>7}{'mean':>7}{'2-rune':>8}"
        f"{'chi2':>7}{'P':>8}"
    )
    for name, _ in RULES:
        n, mean, short, stat, p = lengths[name]
        print(f"  {name:<30}{n:>7}{mean:>7.3f}{short:>8.3f}{stat:>7.1f}{p:>8.3f}")

    print(
        "\n2. Order between neighbours: the author's text, and the body at the same size"
    )
    print(
        f"  {'words joined to the next word':<30}{'all spans':>10}{'no refrains':>13}"
        f"{'blocks':>8}{'body, same size':>18}{'highest':>9}"
    )
    body_at = {}
    for name, _ in RULES:
        ws, _ = group(f"body at|{name}|")
        body_at[name] = ws
        print(
            f"  {name:<30}{z[f'author|{name}'][0]:>+10.2f}{z[f'fresh|{name}'][0]:>+13.2f}"
            f"{sizes['fresh', name]:>8}{f'{ws.mean():+.2f} +- {ws.std(ddof=1):.2f}':>18}"
            f"{ws.max():>+9.2f}"
        )

    print(f"\n3. Order between neighbours: prose at the body's {size} blocks")
    print(
        f"  {'words joined to the next word':<30}{'2-rune':>8}{'adjacency z':>22}"
        f"{'lowest':>8}{'at or below body':>18}{'lag-1 r':>9}"
    )
    prose_z = {}
    for name, _ in RULES:
        zs, rs = group(f"prose|{name}|")
        prose_z[name] = zs
        print(
            f"  {name:<30}{np.mean(prose_short[name]):>8.3f}"
            f"{f'{zs.mean():+.1f} +- {zs.std(ddof=1):.1f} ({len(zs)})':>22}{zs.min():>+8.1f}"
            f"{f'{int((zs <= body_z).sum())} of {len(zs)}':>18}{rs.mean():>+9.3f}"
        )

    print("\n4. Span ends: last block minus interior blocks, in runes")
    print(
        f"  {'words joined to the next word':<30}{'author':>16}{'no refrains':>16}"
        f"{'prose registers':>18}"
    )
    for name, _ in RULES:
        pg = np.array(prose_gap[name])
        print(
            f"  {name:<30}"
            f"{'{:+.2f} +- {:.2f}'.format(*gaps['author', name]):>16}"
            f"{'{:+.2f} +- {:.2f}'.format(*gaps['fresh', name]):>16}"
            f"{f'{pg.mean():+.2f} +- {pg.std(ddof=1):.2f}':>18}"
        )

    fits = [name for name, _ in RULES if lengths[name][4] > 0.05]
    print()
    if not fits:
        print("VERDICT: no rule here reproduces the body's block lengths.")
        return
    best = max(fits, key=lambda name: lengths[name][4])

    def apart(name: str) -> tuple[float, float, float]:
        """Sigma between intact order under a rule and the body, on three readings."""
        author_sigma = z[f"fresh|{name}"][0] - body_at[name].mean()
        zs = prose_z[name]
        prose_sigma = (zs.mean() - body_z) / zs.std(ddof=1)
        gap, se = gaps["fresh", name]
        return (
            float(author_sigma),
            float(prose_sigma),
            (gap - body_gap) / float(np.hypot(se, body_gap_se)),
        )

    resid = cells[f"fresh|{best}"]
    top = sorted(
        (
            (abs(resid[i, k]), i, k)
            for i in range(len(NAMES))
            for k in range(len(NAMES))
        ),
        reverse=True,
    )[:3]
    print(
        f"what is left in the author's order under {best}, refrains out: "
        + "; ".join(f"{NAMES[i]} then {NAMES[k]} {resid[i, k]:+.1f}" for _, i, k in top)
        + " (standardised cells of the transition table)\n"
    )

    print(
        "5. Sigma between intact English order and the body, rules that fit the lengths"
    )
    print(
        f"  {'rule':<30}{'neighbours, author':>20}{'neighbours, prose':>19}{'span ends':>11}"
    )
    rows = {name: apart(name) for name in fits}
    for name in fits:
        a_s, p_s, g_s = rows[name]
        print(f"  {name:<30}{a_s:>+20.1f}{p_s:>+19.1f}{g_s:>+11.1f}")

    a_s, p_s, g_s = rows[best]
    narrow = fits[0]
    weakest = min(rows.values(), key=max)
    raw = prose_z[RULES[0][0]].mean()
    floor = min(prose_z[name].mean() for name, _ in RULES)
    if max(weakest) < 2.0:
        print(
            f"\nVERDICT: under at least one rule that fits the lengths, intact English "
            f"order is within {max(weakest):.1f} sigma of the body on every reading. "
            f"Joining may be the whole story."
        )
        return
    print(
        f"\nVERDICT: a combination, and an ordering that joining shrinks but does not "
        f"remove. {len(fits)} rules reproduce the body's block lengths. Under the "
        f"narrowest, {narrow}, neighbours keep all of English's order: prose reads "
        f"{prose_z[narrow].mean():+.1f} +- {prose_z[narrow].std(ddof=1):.1f} where the "
        f"body reads {body_z:+.2f} (as written: {raw:+.1f}). Under the best-fitting, "
        f"{best} (P {lengths[best][4]:.2f}), prose falls to {prose_z[best].mean():+.1f} "
        f"+- {prose_z[best].std(ddof=1):.1f} ({p_s:+.1f} sigma from the body, "
        f"{int((prose_z[best] <= body_z).sum())} of {len(prose_z[best])} windows at or "
        f"below it) and the author reads {z[f'fresh|{best}'][0]:+.2f} against "
        f"{body_at[best].mean():+.2f} for the body at the same size. No rule here takes "
        f"prose below {floor:+.1f}. What no rule removes is the long block at the end "
        f"of a span: {gaps['fresh', best][0]:+.2f} runes under {best} against the "
        f"body's {body_gap:+.2f} ({g_s:+.1f} sigma; at least "
        f"{min(r[2] for r in rows.values()):.1f} under every fitting rule)."
    )


if __name__ == "__main__":
    main()
