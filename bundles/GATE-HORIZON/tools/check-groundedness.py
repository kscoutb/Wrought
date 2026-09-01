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


_LIST = [l.strip() for l in (REPO / "review/horizon/file-list.txt").read_text().splitlines() if l.strip()]
_BY_ENCODED = {p.replace("/", "__") + ".md": p for p in _LIST}


def source_for(md: pathlib.Path) -> pathlib.Path | None:
    """repo-map/bin__foo.md -> bin/foo.

    DEFECT FOUND AND FIXED 2026-08-31, in this gate's own tool. The naive inverse --
    `md.name[:-3].replace("__", "/")` -- is LOSSY, because the encoding "/" -> "__" collides with
    every dunder filename: `src/wrought_verifier/__init__.py` encodes to
    `src__wrought_verifier____init__.py`, and decoding that gives `src/wrought_verifier//init/.py`,
    which is not a file. It silently marked 3 real modules NO-SOURCE -- an unreadable verdict that
    looked like a missing file rather than a broken decoder.

    The encoding is not invertible, so do not invert it: encode each path from the ORIGINAL file
    list and match forward. That is exact by construction and cannot collide.
    """
    p = _BY_ENCODED.get(md.name)
    if p:
        f = REPO / p
        return f if f.is_file() else None
    f = REPO / md.name[:-3].replace("__", "/")      # legacy fallback, still correct for non-dunders
    return f if f.is_file() else None


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
        # A SECOND DEFECT IN THIS TOOL, FOUND 2026-08-31 AND FIXED: the checker PENALIZED THE
        # CORRECT ANSWER. For a shell script with no functions the honest summary is
        #   "Key functions/classes: None; operates as a linear bash script without named functions"
        # and the extractor below read "operates", "linear", "without", "named" as CLAIMED
        # IDENTIFIERS, found them absent from the file, and marked the summary UNRELIABLE for
        # fabrication. It flagged 5 summaries this way, and every one of them was right.
        # A groundedness check that punishes "there are none here" measures fluency, not honesty.
        if re.match(r"\s*(?:\*\*)?\s*(none|no\b|n/?a\b)", line, re.IGNORECASE):
            continue
        # strip any backticked forms already captured, then take bare identifiers
        raw.extend(NAME.findall(line.replace("`", " ")))
    # Words that are PROSE, not symbols. An identifier check must never score a common English
    # word as a claimed symbol -- doing so scores FLUENCY, not groundedness.
    #
    # THIRD DEFECT IN THIS TOOL, and the same one twice: `bin/make-review-bundle-20` was scored
    # 0.56 UNRELIABLE for the sentence "Standalone bash script with no defined functions or
    # classes; operates via variables ZIP, STAGE, BASE and trap." Every identifier it actually
    # claimed is in the file (ZIP 7 hits, STAGE 18, BASE 6, trap 1); the four "invented" tokens --
    # Standalone, defined, operates, variables -- are English, 0 hits each. The summary was
    # perfectly grounded and the instrument was wrong. The None-prefix guard above did not catch
    # it because this sentence begins with "Standalone", not "None".
    STOP = {"and", "the", "none", "not", "applicable", "main", "logic", "script", "identifier",
            "functions", "classes", "class", "function", "helpers", "helper", "plus", "via", "for",
            # added after the make-review-bundle-20 false positive
            "standalone", "defined", "define", "operates", "operate", "variables", "variable",
            "executes", "execute", "top", "level", "inline", "control", "flow", "named", "without",
            "linear", "procedural", "driven", "uses", "using", "with", "structured", "sequential",
            "shell", "bash", "python", "code", "file", "files", "block", "blocks", "step", "steps",
            "only", "single", "simple", "direct", "purely", "entirely", "global", "globals"}
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
