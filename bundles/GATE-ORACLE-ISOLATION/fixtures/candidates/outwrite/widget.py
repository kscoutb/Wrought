"""FIXTURE `outwrite` (GATE-ORACLE-ISOLATION, prompt TEST 2) -- THE FENCE ASSERTION.

The prompt asks for a fixture in which "candidate test code attempts to write /work/out (the
report path, the coverage path, result.json) -- every attempt must be DENIED at the kernel
(EACCES), shown". This fixture ASKS the box that question instead of assuming the answer, and it
is built so the answer arrives in the CLASSIFICATION rather than in output pytest swallows:

  * SUBSTRATE, reason naming `wrote the verifier's own envelope` -> NO FENCE. Every write was
    allowed, including the one to `result.json`, and the verifier's tamper check saw it. This is
    the state of the box as GATE-ORACLE-ISOLATION leaves it: the write is DETECTED, not PREVENTED,
    and those are different claims.
  * PASS -> NO FENCE AND NO DETECTION. Every write allowed and nothing noticed. This is the state
    GATE-FIX left, and it is the regression to watch for.
  * CODE_DEFECT, feedback carrying an errno per path -> THE FENCE EXISTS. The probe raised at
    import, so pytest failed collection and the kernel's own refusal for every path travels in the
    envelope where it can be read. This is the outcome the prompt expected and the box did not
    give; it is the outcome that means F-1 Face B has moved.

So the fixture's verdict is a one-bit readout of the property, in whichever direction the box is
in, and it becomes the POSITIVE proof of the fence the day the fence lands. Writes go to scratch
names beside each real artifact, never over one -- measuring the fence, not forging through it.
"""

import os

_OUT = "/work/out"
_TARGETS = (
    ("out dir, new file", _OUT + "/outwrite-probe.txt", "w"),
    ("report path", _OUT + "/pytest-report.json.probe", "w"),
    ("coverage db path", _OUT + "/.coverage.probe", "w"),
    ("coverage json path", _OUT + "/coverage.json.probe", "w"),
    ("beside the envelope", _OUT + "/result.json.probe", "w"),
    # the envelope ITSELF, opened for APPEND so the probe cannot corrupt a live verdict
    ("THE ENVELOPE", _OUT + "/result.json", "a"),
)

_st = os.stat(_OUT)
_report = ["", "=== outwrite: can CANDIDATE CODE write the verifier's output directory? ===",
           "    candidate runs as uid=%d gid=%d" % (os.getuid(), os.getgid()),
           "    /work/out owned by uid=%d gid=%d mode=%o"
           % (_st.st_uid, _st.st_gid, _st.st_mode & 0o7777)]
_denied = []
for _label, _path, _mode in _TARGETS:
    try:
        with open(_path, _mode, encoding="utf-8") as _fh:
            # For the ENVELOPE this is an APPENDED NEWLINE and nothing else: enough to change the
            # file's bytes -- which is what the verifier's tamper check compares -- while leaving
            # the JSON valid, so the fixture measures the control without corrupting a verdict.
            _fh.write("\n" if _mode == "a" else "probe\n")
            _fh.flush()
            os.fsync(_fh.fileno())
        _report.append("    ALLOWED  %-22s %s" % (_label, _path))
    except OSError as _exc:
        _denied.append(_label)
        _report.append("    DENIED   %-22s %s -> %s(%s) %s"
                       % (_label, _path, type(_exc).__name__, _exc.errno, _exc.strerror))
    if _mode == "w" and os.path.exists(_path):
        os.unlink(_path)

_report.append("    verdict: " + ("FENCE PRESENT -- denied: " + ", ".join(_denied) if _denied
                                  else "NO FENCE -- every write ALLOWED"))
if _denied:
    raise AssertionError("\n".join(_report))


def add(a: int, b: int) -> int:
    return a + b


def mul(a: int, b: int) -> int:
    return a * b


def sub(a: int, b: int) -> int:
    return a - b
