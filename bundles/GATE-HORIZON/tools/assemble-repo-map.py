#!/usr/bin/env python3
"""Assemble review/horizon/REPO-MAP.md from the RELIABLE local-model summaries only.

The gate prompt's rule is that a summary citing invented symbols is "marked UNRELIABLE and not
trusted". This tool is the "not trusted" half: it reads the verdicts written by
check-groundedness.py and carries ONLY the RELIABLE ones into the map. Everything else is listed
by name and verdict in an EXCLUDED section, so a reader sees what was dropped and why rather
than finding a silently shorter map.

The header of the generated file states, in its own words, what a RELIABLE verdict does and does
not mean. A map that reads as authoritative when it is machine-generated from a 27B's summaries
would be exactly the overclaim this project keeps catching in itself.
"""
from __future__ import annotations
import json, pathlib, sys, collections

REPO = pathlib.Path("/home/kalib/review-rc1")
MAPDIR = REPO / "review/horizon/repo-map"
GROUND = REPO / "review/horizon/groundedness.json"
OUT = REPO / "review/horizon/REPO-MAP.md"


def main() -> int:
    if not GROUND.is_file():
        print("run check-groundedness.py first", file=sys.stderr); return 1
    g = json.loads(GROUND.read_text(encoding="utf-8"))
    by_verdict = collections.defaultdict(list)
    for r in g["results"]:
        by_verdict[r["verdict"]].append(r)

    reliable = sorted(by_verdict["RELIABLE"], key=lambda r: r["source"] or "")
    # UNCHECKABLE is NOT the same as UNRELIABLE and must not be silently merged with it: it means
    # the summary cited too few checkable names for a ratio to mean anything, not that it lied.
    # Carried, clearly labelled, because dropping honest summaries over an instrument limitation
    # would bias the map toward whatever the checker happens to parse well.
    uncheckable = sorted(by_verdict["UNCHECKABLE"], key=lambda r: r["source"] or "")
    dropped = sorted(by_verdict["UNRELIABLE"] + by_verdict["EMPTY"]
                     + by_verdict["REASONING-ONLY"] + by_verdict["NO-SOURCE"],
                     key=lambda r: r["source"] or r["summary"])

    checked = len(reliable) + len(dropped)
    num = sum(r["grounded"] for r in g["results"] if "grounded" in r)
    den = sum(r["cited"] for r in g["results"] if "cited" in r and r.get("verdict") in
              ("RELIABLE", "UNRELIABLE"))

    L: list[str] = []
    L.append("# REPO-MAP — every script under `bin/` and module under `src/`, summarized locally\n")
    L.append("**Generated, not written.** Each entry below is a summary produced by the RESIDENT "
             "local model (Qwen3.6-27B, UD-Q4_K_XL, reasoning on) reading one file, air-gapped, "
             "at zero marginal cost. This file is assembled mechanically from those summaries by "
             "`assemble-repo-map.py`; no human and no cloud model reviewed the prose.\n")
    L.append("## What a RELIABLE verdict means, and what it does not\n")
    L.append("Every entry carried here passed `check-groundedness.py`: the identifiers the summary "
             "cites were grepped against the file it summarizes, and at least 60 % of them "
             "literally appear in it. **That is a test for FABRICATION and nothing else.** A "
             "summary can cite only real names and still describe them wrongly, cite the "
             "unimportant ones, or omit what matters. **Read an entry as *not obviously "
             "fabricated*, never as *correct*.**\n")
    L.append(f"- Summaries produced: **{len(g['results'])}**\n")
    L.append(f"- Carried here as RELIABLE: **{len(reliable)}**"
             f"{f' of {checked} checkable ({100*len(reliable)/checked:.1f} %)' if checked else ''}\n")
    L.append(f"- Carried with the caveat UNCHECKABLE: **{len(uncheckable)}** "
             "(too few citable names for a ratio to mean anything — an instrument limit, "
             "**not** evidence of fabrication)\n")
    L.append(f"- Excluded: **{len(dropped)}**\n")
    if den:
        L.append(f"- Identifier groundedness across all checked summaries: "
                 f"**{num}/{den} ({100*num/den:.1f} %)**\n")
    L.append("\n---\n")

    def emit(rows, title, note=""):
        if not rows:
            return
        L.append(f"\n## {title}\n")
        if note:
            L.append(f"{note}\n")
        cur = None
        for r in rows:
            src = r["source"] or r["summary"]
            top = src.split("/")[0]
            if top != cur:
                cur = top
                L.append(f"\n### `{top}/`\n")
            body = (MAPDIR / r["summary"]).read_text(encoding="utf-8", errors="replace")
            lines = [x for x in body.splitlines() if x.strip()]
            lines = lines[1:] if lines and lines[0].startswith("# ") else lines
            ratio = f" · grounded {r['grounded']}/{r['cited']}" if "grounded" in r else ""
            L.append(f"\n**`{src}`**{ratio}\n")
            for x in lines:
                L.append(f"> {x}\n")

    emit(reliable, "RELIABLE summaries")
    emit(uncheckable, "UNCHECKABLE summaries — carried, with the caveat",
         "*These cite fewer than two checkable identifiers, so the groundedness ratio would be "
         "noise. They are carried because excluding honest summaries over an instrument "
         "limitation would bias this map toward whatever the checker parses well.*")

    if dropped:
        L.append("\n---\n\n## EXCLUDED — not carried into this map\n")
        L.append("*Listed so the map is visibly shorter for a stated reason, rather than "
                 "silently incomplete.*\n\n")
        L.append("| File | Verdict | Detail |\n|---|---|---|\n")
        for r in dropped:
            det = (f"grounded {r.get('grounded','?')}/{r.get('cited','?')}; "
                   f"invented: {', '.join(r.get('invented', [])[:4])}"
                   if r["verdict"] == "UNRELIABLE" else r.get("reason", ""))
            L.append(f"| `{r['source'] or r['summary']}` | **{r['verdict']}** | {det} |\n")

    OUT.write_text("".join(L), encoding="utf-8")
    print(f"REPO-MAP.md: {OUT.stat().st_size} B — {len(reliable)} reliable, "
          f"{len(uncheckable)} uncheckable, {len(dropped)} excluded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
