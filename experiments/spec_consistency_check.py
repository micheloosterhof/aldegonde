# ABOUTME: Checks every row of the specification against its cited sources, flagging
# ABOUTME: broken citations and rows whose source carries a withdrawal it may not reflect.
"""The specification is a summary of 60-odd files, and summaries drift.

`what-any-solution-must-satisfy.md` says of itself that it "adds no measurement and should
be regenerated rather than trusted if it drifts from those files". Nothing checked whether
it had. This does, mechanically, so the check can be rerun after any tick that withdraws
something.

Three checks, in order of how often they fire:

- **Broken citations.** A row naming a file that does not exist. One found: E6 cited
  `interleaving_depth.md`, which is `experiments/interleaving_depth.py`.
- **Withdrawal markers.** A row citing a file containing "withdrawn", "retracted" or
  "superseded". Twelve fired and **ten are false positives** -- the marker belongs to a
  different claim in the same file. That is the expected rate and the reason this check
  reports rather than judges.
- **Dangling experiment references.** The same for `.py` names.

## What the audit found

| row | source | verdict |
|---|---|---|
| E6 | `interleaving_depth.md` | **was broken** — the file is `experiments/interleaving_depth.py`; fixed |
| D5 | `seam-to-d1w-ratio-is-a-constraint.md` | **was stale** — its exclusion is retracted and D5's seam clause rested on it; row rewritten |
| C5, D7, G4, G5, C3, D14, D15, E1, E3, C-1 | various | false positives; the marker is about another claim |

Both are fixed, so this now reports zero broken citations. It also reports four rows
(B2, D2, D3, E5) that cite nothing at all, which is a different kind of gap: their claims
cannot be traced from the specification alone.

**D5 is the substantive one.** Its row asserts the suppression's failures "must be as
likely at a seam as inside a word", citing a file whose own status line reads "the
exclusion claimed in the first version is **retracted** — it held g fixed". The ratio is
not a constraint: `one-parameter-fits-both-suppressions.md` shows a single phi lands the
seam and the within-block rate together, with the ratio falling out at 1.07-1.35 around
the corpus's 1.25. The row's other half -- rune-blindness, 28 of 29 runes at chi2 27.8 on
28 df -- is untouched and keeps its own source.

    python spec_consistency_check.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "hypotheses" / "what-any-solution-must-satisfy.md"
MARKERS = (
    "WITHDRAWN",
    "withdrawn",
    "RETRACTED",
    "retracted",
    "SUPERSEDED",
    "superseded",
)


def rows(text: str) -> list[tuple[str, str]]:
    """(row id, whole line) for each constraint row of the table."""
    out = []
    for line in text.split("\n"):
        if not line.startswith("| ") or line.startswith(("|---", "| #", "| id")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3:
            out.append((cells[0], line))
    return out


def cited(line: str) -> tuple[set[str], set[str]]:
    names = set(re.findall(r"`([a-z0-9_-]+\.(?:md|py))`", line))
    return (
        {n for n in names if n.endswith(".md")},
        {n for n in names if n.endswith(".py")},
    )


def main() -> None:
    text = SPEC.read_text()
    table = rows(text)
    print(f"{len(table)} constraint rows in the specification.\n")

    broken = []
    flagged = []
    uncited = []
    for rid, line in table:
        docs, scripts = cited(line)
        if not docs and not scripts:
            uncited.append(rid)
        for name in docs:
            path = ROOT / "hypotheses" / name
            if not path.exists():
                broken.append((rid, name, "no such hypothesis"))
                continue
            body = path.read_text()
            hit = next((m for m in MARKERS if m in body), None)
            if hit:
                flagged.append((rid, name, hit))
        for name in scripts:
            if not (ROOT / "experiments" / name).exists():
                broken.append((rid, name, "no such experiment"))

    print(f"broken citations: {len(broken)}")
    for rid, name, why in broken:
        print(f"   {rid:<8}{name:<46}{why}")

    print(f"\nrows with no citation at all: {len(uncited)}")
    if uncited:
        print("   " + ", ".join(uncited))

    print(f"\nrows citing a file that carries a withdrawal marker: {len(flagged)}")
    print("   (the marker often belongs to a different claim in that file --")
    print("    this reports, it does not judge)")
    for rid, name, marker in sorted(flagged):
        print(f"   {rid:<8}{name:<46}({marker})")

    print(
        "\nRerun this after any tick that withdraws something. A broken citation is"
        "\nalways a defect; a withdrawal marker needs reading, and about ten in twelve"
        "\nturn out to be about another claim in the same file."
    )


if __name__ == "__main__":
    main()
