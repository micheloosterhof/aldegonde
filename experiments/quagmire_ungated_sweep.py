# ABOUTME: Re-runs the keyword-Quagmire key enumeration with no DJU-BEI gate: every
# ABOUTME: complete key is scored directly by the base_0-free unigram verifier.
"""The keyword-Quagmire sweep, ungated.

`quagmire_runner.py` verified only the keys whose interval product over words
1477..2926 has >= 6 fixed points -- 186,465 of 313,972,400. That gate is a
necessary condition only if DJU-BEI is a genuine state return. Under this very
model it almost never is: the walk group is ~4e30, an LP-sized prose corpus holds
~480 repeated two-word phrases of >= 6 runes, and each returns on its six points
with probability 1/(29*28*27*26*25*24) = 2.9e-9 -- about 1e-6 expected returns,
against ~1e-2 for a chance ciphertext repeat. If the repeat is chance, the true
key passes the gate at the same 5.9e-4 rate as any other key, so the gated sweep
discarded it with probability 0.9994 and did not exclude the family.

Here every key is scored by `walk_score_kernel.score_sigmas`: no gate, no
hill-climb, base_0 free. Three windows of 200 words, each opening a long section,
are scored independently, so a section-level restart or a single wrong word length
costs one window rather than the corpus. The best keys are re-scored on whole
sections, where a wrong key scores 0.2-0.45 nats/rune and a true key sits near 1.2.

**Result (2026-09-19): negative inside the bands.** `--run`: 365,526,436 keys,
none at or above the candidate floor of 0.85; the best keys score at most 0.44 on a
whole section. `--extra`: 38,672 left-out keywords and 214 left-out disks,
334,988,084 keys, none at the floor, best section score 0.49. A true key scores
~1.2. The candidate bands rest on one stand-in register and keep a true key about
a quarter of the time (`register_band_sensitivity.py`), so this does not exclude
the family; the widened-band sweep would.

Run with no arguments for the positive control (a planted family key must be
found on prose enciphered with the real length sequence). `--run N` streams the
full candidate space over N workers. `--extra N` streams the keys the original
keyword list left out: it kept dictionary words of 4-12 letters, which drops
CIRCUMFERENCE (13 letters) and 3301's own vocabulary (PRIMES, KOAN). Every extra
keyword is tried on the letter wheel against all disks, and every extra disk
against the original letter wheels.
"""

from __future__ import annotations

import heapq
import json
import random
import sys
import tempfile
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from quagmire_runner import (  # noqa: E402
    build_setup,
    conj_shift,
    encrypt_walk,
    g_candidates,
    letter_steps,
    load_register,
)
from walk_score_kernel import Windows, score_sigmas  # noqa: E402

M = 29
WINDOW_WORDS = 200
WINDOW_STARTS = (419, 806, 2181)  # first words of sections 2, 4, 8
SECTIONS = ((160, 419), (419, 804), (806, 1245), (1472, 1824), (2181, 2861))
KEEP = 40  # best keys re-scored at the end
KEEP_PER_TASK = 5
# window scores under this are reported as upper bounds (the kernel's cheap path);
# wrong keys sit near 0.5 on a 200-word window and a true key near 1.2
CANDIDATE_FROM = 0.85
MAIN_TASKS = 360
EXTRA_TASKS = 72
OUT = ROOT / "experiments" / "quagmire_ungated_candidates.jsonl"
_W: dict = {}


def windows_of(words: list[list[int]]) -> Windows:
    return Windows([words[a : a + WINDOW_WORDS] for a in WINDOW_STARTS])


def _prepare(prose_path: Path, lens: list[int], *, want_extra: bool):
    """Fill the tables the workers read; return (words, vocab, extra keywords).

    Runs once in the parent. The pool forks, so the workers share these tables and
    the ~330 MB of n-gram data that importing aldegonde.c3301 loads, instead of each
    building its own copy.
    """
    words, vocab, T1, lo1, hi1, sigmas = build_setup(prose_path, lens)
    _W.update(
        T1=T1, lo1=lo1, hi1=hi1, windows=windows_of(words), logf=log_frequencies()
    )
    _W["sigmas"] = {"main": np.array(sigmas, dtype=np.int8)}
    extra = extra_vocabulary(vocab) if want_extra else []
    if extra:
        known = {tuple(x) for x in sigmas}
        every = build_setup(prose_path, lens, vocab + extra)[5]
        fresh = [x for x in every if tuple(x) not in known]
        _W["sigmas"]["all"] = np.array(every, dtype=np.int8)
        _W["sigmas"]["extra"] = np.array(fresh, dtype=np.int8).reshape(-1, M)
    return words, vocab, extra


def _work(task: tuple[str, str, list[str]]):
    """Score every (K, schedule) x sigma key for one slice of keywords.

    The task carries its name and which disks the slice's letter wheels are tried
    against. Returns (name, keys tested, best keys as [score, K, schedule, sigma]).
    """
    name, disks, chunk = task
    sigmas = _W["sigmas"][disks]
    best: list[tuple[float, list[int], list[int], list[int]]] = []
    tested = 0
    if not len(sigmas):
        return name, tested, best
    for K, sched in g_candidates(chunk, _W["T1"], _W["lo1"], _W["hi1"], None):
        scores = score_sigmas(
            letter_steps(K, sched),
            sigmas,
            _W["windows"],
            _W["logf"],
            skip_below=CANDIDATE_FROM,
        )
        tested += len(scores)
        top = int(scores.argmax())
        item = (float(scores[top]), K, sched, [int(x) for x in sigmas[top]])
        if len(best) < KEEP_PER_TASK:
            heapq.heappush(best, item)
        elif item[0] > best[0][0]:
            heapq.heapreplace(best, item)
    return name, tested, best


def positive_control(lens: list[int], prose_path: Path) -> None:
    """A planted family key, enciphered on the real length sequence, must score high."""
    from d5_partial_leak import to_runeglish  # noqa: PLC0415
    from doublet_position_profile import IDX_ENG  # noqa: PLC0415

    rng = random.Random(3301)
    pools, _table, _floor = load_register(prose_path)
    plain = [rng.choice(pools[L])[:L] for L in lens]

    def keyed(word: str) -> list[int]:
        seen: list[int] = []
        for r in [IDX_ENG[t] for t in to_runeglish(word)] + list(range(M)):
            if r not in seen:
                seen.append(r)
        return seen

    K, sched = keyed("DIUINITY"), [3, 7, 5, 11, (0 - 3 - 7 - 5 - 11) % M]
    sigma = conj_shift(keyed("PILGRIM"), 8)
    base0 = rng.sample(range(M), M)
    cipher = encrypt_walk(plain, base0, letter_steps(K, sched), sigma)
    assert len({tuple(w) for w in cipher}) > 2000, "planted key is degenerate"

    sigmas = np.array(
        [sigma] + [rng.sample(range(M), M) for _ in range(2000)], dtype=np.int8
    )
    scores = score_sigmas(
        letter_steps(K, sched), sigmas, windows_of(cipher), log_frequencies()
    )
    print(
        f"planted key {scores[0]:.3f}; best of 2000 wrong sigmas {scores[1:].max():.3f}"
    )
    assert scores[0] > scores[1:].max() + 0.2, "planted key not found"
    print("positive control passed")


def rescore_on_sections(words, K, sched, sigma, logf) -> list[float]:
    """Whole-section scores of one key: 0.2-0.45 for a wrong key, ~1.2 for a true one."""
    perms = letter_steps(K, sched)
    sig = np.array([sigma], dtype=np.int8)
    return [
        float(score_sigmas(perms, sig, Windows([words[a:b]]), logf)[0])
        for a, b in SECTIONS
    ]


def extra_vocabulary(main: list[str]) -> list[str]:
    """Keywords the 4-12 letter dictionary list leaves out."""
    from keyword_exhaustion import DICT  # noqa: PLC0415

    seen = {w.upper() for w in main}
    found = [w for w in DICT.read_text().split() if len(w) == 3 or 13 <= len(w) <= 20]
    for line in (ROOT / "data" / "register_vocab.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            found.append(line.split("\t")[1])
    found += [
        "PRIMES",
        "KOAN",
        "KOANS",
        "CICADA",
        "LIBER",
        "PRIMUS",
        "TOTIENT",
        "DIUINITY",
    ]
    out = []
    for word in found:
        if word.isalpha() and word.isascii() and word.upper() not in seen:
            seen.add(word.upper())
            out.append(word)
    return out


def run(nproc: int, prose_path: Path, lens: list[int], *, extra_only: bool) -> None:
    """Stream the tasks over nproc workers, logging each finished task.

    The progress log makes the sweep resumable: a task already in it is skipped,
    so a killed run loses only the tasks in flight.
    """
    words, vocab, extra = _prepare(prose_path, lens, want_extra=extra_only)
    logf = _W["logf"]
    if extra:
        tasks = [
            (f"extra-g-{i}", "all", extra[i::EXTRA_TASKS]) for i in range(EXTRA_TASKS)
        ]
        tasks += [
            (f"extra-s-{i}", "extra", vocab[i::MAIN_TASKS]) for i in range(MAIN_TASKS)
        ]
        print(
            f"{len(extra):,} extra keywords, {len(_W['sigmas']['extra'])} extra disks, "
            f"{nproc} workers",
            flush=True,
        )
    else:
        tasks = [(f"main-{i}", "main", vocab[i::MAIN_TASKS]) for i in range(MAIN_TASKS)]
        print(
            f"{len(vocab):,} keywords, {len(_W['sigmas']['main'])} sigma disks, "
            f"{nproc} workers",
            flush=True,
        )
    out_path = OUT.with_name("quagmire_ungated_extra.jsonl") if extra else OUT
    progress = Path(tempfile.gettempdir()) / f"{out_path.stem}_progress.jsonl"
    tested = 0
    best: list[list] = []
    finished = set()
    if progress.exists():
        for line in progress.read_text().splitlines():
            record = json.loads(line)
            finished.add(record["task"])
            tested += record["tested"]
            best += record["best"]
        print(f"resuming: {len(finished)} tasks already in {progress}", flush=True)
    todo = [t for t in tasks if t[0] not in finished]
    start = time.time()
    with progress.open("a") as log, get_context("fork").Pool(nproc) as pool:
        for done, (name, count, top) in enumerate(pool.imap_unordered(_work, todo), 1):
            tested += count
            best = heapq.nlargest(
                KEEP, best + [list(t) for t in top], key=lambda t: t[0]
            )
            log.write(json.dumps({"task": name, "tested": count, "best": top}) + "\n")
            log.flush()
            if done % 20 == 0 or done == len(todo):
                print(
                    f"  {done}/{len(todo)} tasks, {tested:,} keys, "
                    f"best window score {best[0][0]:.3f}, {time.time() - start:.0f}s",
                    flush=True,
                )
    print(f"\nDONE: {tested:,} keys; this run {(time.time() - start) / 60:.1f} min")
    print("best keys re-scored on whole sections (wrong 0.2-0.45, true ~1.2):")
    with out_path.open("w") as fout:
        for score, K, sched, sigma in best:
            full = rescore_on_sections(words, K, sched, sigma, logf)
            print(
                f"  window {score:.3f}  sections {' '.join(f'{x:.2f}' for x in full)}  sched {sched}"
            )
            record = {
                "window": score,
                "sections": full,
                "K": K,
                "sched": sched,
                "sigma": sigma,
            }
            fout.write(json.dumps(record) + "\n")
    print(f"written to {out_path}")


def main() -> None:
    from lp_corpus import load_clean  # noqa: PLC0415

    stream, wid = load_clean()
    lens = [0] * (wid[-1] + 1)
    for w in wid:
        lens[w] += 1
    assert len(stream) == sum(lens)
    if "--run" in sys.argv:
        run(
            int(sys.argv[sys.argv.index("--run") + 1]),
            PROSE_CACHE,
            lens,
            extra_only=False,
        )
    elif "--extra" in sys.argv:
        run(
            int(sys.argv[sys.argv.index("--extra") + 1]),
            PROSE_CACHE,
            lens,
            extra_only=True,
        )
    else:
        positive_control(lens, PROSE_CACHE)


if __name__ == "__main__":
    main()
