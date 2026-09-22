# ABOUTME: Checks every row of the specification against its cited sources, flagging
# ABOUTME: broken citations and rows whose source carries a withdrawal it may not reflect.
r"""The specification is a summary of 60-odd files, and summaries drift.

`what-any-solution-must-satisfy.md` says of itself that it "adds no measurement and should
be regenerated rather than trusted if it drifts from those files". Nothing checked whether
it had. This does, mechanically, so the check can be rerun after any tick that withdraws
something.

**The first version of this check had two parsing bugs and reported four gaps that were
not there.** Both are fixed and recorded below under "what the checker got wrong", because
a consistency checker that invents inconsistencies is worse than none.

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

Both are fixed, so the check now reports **0 broken citations and 0 uncited rows**, with
eleven withdrawal markers that are all false positives -- verified one at a time:

- C3's marker is a withdrawn claim about seam-doublet fixed points;
- E1 and E3's are the rubricated-titles lead and "two effects, not one";
- D15's is the same titles lead; D5's, D14's, D7's, G4's and G5's each belong to a
  different claim in the cited file.

## What the checker got wrong

It first reported four rows -- B2, D2, D3, E5 -- as citing nothing at all. Both causes
were in the checker:

- **"same" inheritance.** The table writes `same` when a row shares the row above's
  source, which carries D2, D3 and E5. Reading that as an empty citation invents a gap.
- **Escaped pipes.** B2's claim contains `\|K̂(j)\|²`, and D11's and E2's contain escaped
  bars in their z-scores. Splitting the row on every `|` puts a fragment of the claim in
  the source column, so those rows look uncited too -- and fixing only the inheritance bug
  made D11 and E2 appear as new gaps, which is how the second bug surfaced.

Splitting on unescaped pipes and resolving `same` leaves nothing uncited.

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
        cells = cells_of(line)
        if len(cells) >= 3:
            out.append((cells[0], line))
    return out


def cells_of(line: str) -> list[str]:
    """Split a table row on UNESCAPED pipes.

    Several rows carry escaped pipes inside the claim -- B2's absolute value bars,
    D11's and E2's z-scores -- and a naive split on "|" puts a fragment of the claim
    in the source column, which reports them as uncited.
    """
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip("|"))]


def source_cell(line: str) -> str:
    """The third column, which holds the row's sources."""
    cells = cells_of(line)
    return cells[2] if len(cells) > 2 else ""


def cited(line: str, inherited: str) -> tuple[set[str], set[str]]:
    """Files named in the source column; "same" inherits the row physically above.

    That convention carries B2, D2, D3 and E5. Reading it as an empty citation reports
    four gaps that are not there, which is what the first version of this check did.
    """
    cell = source_cell(line)
    text = inherited if cell.lower().startswith("same") else cell
    names = set(re.findall(r"`([a-z0-9_-]+\.(?:md|py))`", text))
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
    inherited = ""
    for rid, line in table:
        cell = source_cell(line)
        docs, scripts = cited(line, inherited)
        if not cell.lower().startswith("same"):
            inherited = cell
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
