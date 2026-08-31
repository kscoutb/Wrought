#!/usr/bin/env python3
"""Groundedness check for the local repo-map summaries (GATE-HORIZON PHASE 2).

THE RULE THIS ENFORCES, from the gate prompt: "for a sample of the names each summary cites,
grep the tree; a summary citing invented symbols is marked UNRELIABLE and not trusted."

METHOD, and its limits stated up front because a check that overclaims is worse than no check.
Each summary is asked for "key functions or classes BY EXACT NAME as they appear". This tool
extracts the backticked identifiers a summary cites and asks one question of each: does this
literal string appear in the file the summary is about? That is a test for FABRICATION, and it
is the only thing it tests.

WHAT IT DOES NOT TEST, so nobody reads a green as more than it is:
  * whether the summary's PROSE is true -- a summary can cite only real names and still describe
    them wrongly;
  * whether the cited names are the IMPORTANT ones;
  * whether anything material was omitted.
A file passing this check is "not obviously fabricated", never "correct".

Deliberately conservative in the direction that avoids false accusations of fabrication:
identifiers are matched as plain substrings against the raw file text, and dotted or qualified
names are matched on their last component, so `wrought_orchestrator.store` counts as grounded if
`store` appears. A tool that cried fabrication over a spelling convention would be ignored within
a day, which is worse than a tool that is slightly generous.
"""
from __future__ import annotations
import pathlib, re, sys, json

REPO = pathlib.Path("/home/kalib/review-rc1")
MAPDIR = REPO / "review/horizon/repo-map"

# Identifiers the model cites in backticks. Require >=3 chars so `os` / `re` noise is skipped.
IDENT = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]{2,})`")
# The model frequently writes names WITHOUT backticks on its labelled line -- e.g.
#   "Key functions/classes: fail"
# Measured on the first 14 summaries: backticks alone left 8 of 14 UNCHECKABLE, which would have
# reported a groundedness rate over a biased half of the sample. The FUNCTION-NAME line is also
# the sharpest fabrication test there is, since an invented function name is the failure this
# check exists to catch. Deliberately NOT parsing the imports/dependencies line: it carries
# generic tool names and sysfs paths whose absence from the file proves nothing.
KEYLINE = re.compile(r"^\s*(?:\*\*)?Key [Ff]unctions?[^:]*:\s*(.+)$", re.MULTILINE)
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_.]{2,}")
# A summary must cite at least this many checkable names before a ratio means anything.
MIN_CITED = 2
# Below this fraction grounded, the summary is UNRELIABLE and is not carried into REPO-MAP.md.
THRESHOLD = 0.60


def source_for(md: pathlib.Path) -> pathlib.Path | None:
    """repo-map/bin__foo.md -> bin/foo. The name is the encoding, so this is exact."""
    rel = md.name[:-3].replace("__", "/")
    p = REPO / rel
    return p if p.is_file() else None


def check(md: pathlib.Path) -> dict:
    src_path = source_for(md)
    body = md.read_text(encoding="utf-8", errors="replace")
    rec = {"summary": md.name, "source": str(src_path.relative_to(REPO)) if src_path else None}

    if src_path is None:
        return rec | {"verdict": "NO-SOURCE", "reason": "cannot resolve the file this summarizes"}
    if len(body.strip().splitlines()) <= 1:
        return rec | {"verdict": "EMPTY", "reason": "no content -- the rails-18 failure mode"}
    if "reasoning_content" in body and "NOT a summary" in body:
        return rec | {"verdict": "REASONING-ONLY",
                      "reason": "model returned no content; reasoning preserved but it is not a summary"}

    text = src_path.read_text(encoding="utf-8", errors="replace")
    raw: list[str] = list(IDENT.findall(body))
    for line in KEYLINE.findall(body):
        # strip any backticked forms already captured, then take bare identifiers
        raw.extend(NAME.findall(line.replace("`", " ")))
    # words that are prose, not symbols, on a "Key functions:" line
    STOP = {"and", "the", "none", "not", "applicable", "main", "logic", "script", "identifier",
            "functions", "classes", "class", "function", "helpers", "helper", "plus", "via", "for"}
    cited = []
    for m in raw:
        last = m.split(".")[-1]
        if len(last) < 3 or last.lower() in STOP:
            continue
        cited.append((m, last))
    # de-duplicate, preserve order
    seen, uniq = set(), []
    for full, last in cited:
        if full not in seen:
            seen.add(full); uniq.append((full, last))

    if len(uniq) < MIN_CITED:
        return rec | {"verdict": "UNCHECKABLE", "cited": len(uniq),
                      "reason": f"cites fewer than {MIN_CITED} checkable names; ratio would be noise"}

    grounded = [f for f, l in uniq if l in text]
    invented = [f for f, l in uniq if l not in text]
    ratio = len(grounded) / len(uniq)
    return rec | {"verdict": "RELIABLE" if ratio >= THRESHOLD else "UNRELIABLE",
                  "cited": len(uniq), "grounded": len(grounded),
                  "ratio": round(ratio, 3), "invented": invented[:8]}


def main() -> int:
    mds = sorted(MAPDIR.glob("*.md"))
    if not mds:
        print("no summaries found", file=sys.stderr); return 1
    results = [check(m) for m in mds]

    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    print(f"summaries checked: {len(results)}")
    for v in sorted(counts):
        print(f"  {v:<15} {counts[v]}")
    rel = [r for r in results if r["verdict"] == "RELIABLE"]
    checked = [r for r in results if r["verdict"] in ("RELIABLE", "UNRELIABLE")]
    if checked:
        num = sum(r["grounded"] for r in checked)
        den = sum(r["cited"] for r in checked)
        print(f"\nRELIABLE {len(rel)}/{len(checked)} of checkable "
              f"({100*len(rel)/len(checked):.1f}%)")
        print(f"identifier groundedness across all checked summaries: {num}/{den} "
              f"({100*num/den:.1f}%)")
    worst = sorted((r for r in checked if r["verdict"] == "UNRELIABLE"),
                   key=lambda r: r["ratio"])[:10]
    if worst:
        print("\nUNRELIABLE, worst first -- these are NOT carried into REPO-MAP.md:")
        for r in worst:
            print(f"  {r['source']:<44} {r['ratio']:.2f}  invented: {', '.join(r['invented'][:4])}")

    (REPO / "review/horizon/groundedness.json").write_text(
        json.dumps({"threshold": THRESHOLD, "min_cited": MIN_CITED,
                    "counts": counts, "results": results}, indent=2), encoding="utf-8")
    print("\n-> review/horizon/groundedness.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
