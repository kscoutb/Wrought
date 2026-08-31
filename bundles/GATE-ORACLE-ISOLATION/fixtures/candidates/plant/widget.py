"""FIXTURE `plant` (GATE-ORACLE-ISOLATION) -- exercises the pre-check artifact hygiene.

A DIFFERENT attack from `exit0c`, and the difference is the point. `exit0c` forges an artifact
WITHIN the check that is supposed to produce it, which nothing here closes. This one forges an
artifact belonging to a LATER check: while pytest is running -- the one check in which candidate
code executes -- it writes `/work/out/coverage.json`, the file the COVERAGE check's criterion
reads. The candidate then behaves correctly, so nothing else about the run is suspicious.

`exit0` (GATE-FIX) is this attack's ancestor; GATE-FIX closed it by making the threshold refuse to
read an output file whose producer exited non-zero. That is a sound rule and it is kept. This
fixture attacks the case that rule does not cover: `coverage json` SUCCEEDS, exit 0, and simply
overwrites the plant -- unless it does not, on some future pack or tool version, in which case the
plant is read as the verdict.

GATE-ORACLE-ISOLATION's answer is structural rather than another exit-code rule: the verifier
DELETES what a check is supposed to produce immediately before running it, so "this file was
produced by this check" is true by construction. `cleared_before_run` in the envelope names every
path removed, so the control is visible rather than silent.

Expected: `cleared_before_run` for `py.cov.threshold` lists `/work/out/coverage.json`, and the run
still reaches PASS on the merits, because the candidate below is correct.
"""

import json
import os

_PLANT = "/work/out/coverage.json"

with open(_PLANT, "w", encoding="utf-8") as _fh:
    json.dump({"totals": {"percent_covered": 100.0, "planted_by": "the candidate"}}, _fh)
    _fh.flush()
    os.fsync(_fh.fileno())


def add(a: int, b: int) -> int:
    return a + b


def mul(a: int, b: int) -> int:
    return a * b


def sub(a: int, b: int) -> int:
    return a - b
