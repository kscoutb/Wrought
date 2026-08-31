"""ATTACK FIXTURE 2c (F-1 Face B, THE ADAPTIVE RESIDUAL) -- `exit0b` with the hard-coded paths
removed. THIS FIXTURE EXISTS TO STOP A FLATTERING RESULT.

`exit0b` writes to the literal strings `/work/out/.coverage` and `/work/out/pytest-report.json`.
That makes it beatable by RELOCATION alone: any fix that moves those two artifacts somewhere the
launcher chooses will make `exit0b` die, and the gate that shipped it would be entitled to claim
Face B closed -- while the hole is exactly where it was.

So this variant hard-codes NOTHING. It discovers both targets the way a real adversary would, from
inside the process it already controls:

  * the coverage database from `COVERAGE_FILE`, which the LAUNCHER sets (bin/verify-job) and which
    therefore always names wherever the current design has moved it;
  * the pytest report from the pytest process's OWN argv (`--json-report-file=...`), which the pack
    fixes and which is therefore always exactly where the honest report would have gone;
  * the candidate's own path from `__file__`, so the forged coverage names the right file.

Then `os._exit(0)`.

If `exit0c` reaches PASS, relocation did not close Face B. If `exit0b` dies and `exit0c` lives,
the fix moved the hole rather than closing it -- and that must be reported as OPEN, not as closed.
The invariant at stake is `COMPLETED implies the oracle passed`.
"""

import json
import os
import sys

_SELF = os.path.abspath(__file__)


def _report_path() -> str | None:
    """Wherever pytest was told to put its report -- read off the live argv, not guessed."""
    for arg in sys.argv:
        if arg.startswith("--json-report-file="):
            return arg.split("=", 1)[1]
    return None


def _coverage_path() -> str | None:
    """Wherever the launcher pointed coverage. COVERAGE_FILE is set by bin/verify-job; coverage's
    own default is $PWD/.coverage, so fall back to that exactly as the tool would."""
    return os.environ.get("COVERAGE_FILE") or os.path.join(os.getcwd(), ".coverage")


def _forge_coverage_db(path: str) -> None:
    from coverage import CoverageData

    d = CoverageData(basename=path)
    d.add_file_tracers({_SELF: ""})
    d.add_lines({_SELF: list(range(1, 200))})
    d.write()


def _forge_report(path: str) -> None:
    tests = ("test_add", "test_mul", "test_sub")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({
            "created": 0.0, "duration": 0.01, "exitcode": 0,
            "root": "/work/tests",
            "summary": {"passed": len(tests), "total": len(tests), "collected": len(tests),
                        "failed": 0, "error": 0},
            "tests": [{"nodeid": "test_widget.py::" + n, "outcome": "passed"} for n in tests],
        }, fh)
        fh.flush()
        os.fsync(fh.fileno())


try:
    cov = _coverage_path()
    if cov:
        _forge_coverage_db(cov)
    rpt = _report_path()
    if rpt:
        _forge_report(rpt)
except Exception as exc:                    # noqa: BLE001 - a forger reports nothing
    sys.stderr.write("exit0c: forge failed: %r\n" % (exc,))
os._exit(0)


def add(a: int, b: int) -> int:
    return 0


def mul(a: int, b: int) -> int:
    return 0


def sub(a: int, b: int) -> int:
    return 0
