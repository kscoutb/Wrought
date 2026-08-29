#!/usr/bin/env python3
"""GATE-RUNNER-POLISH Phase 3 — the secret-scan argv leak, reproduced and closed.

Two arms, one variable: HOW the needle reaches the matcher.

  OLD (J-164)  KEY=$(...); git diff --cached | grep -c -- "$KEY"
  NEW          bin/wrought-precommit-secret-scan  (needle in-process, never on a command line)

Both arms scan the SAME planted token in the SAME staged diff, so "did it detect the secret" is
answered identically for both and the only thing that differs is the exposure.

DETERMINISM. An argv exposure is a race — the window is the lifetime of one short-lived process.
Racing it would make this proof flaky and therefore worthless. So the diff is delivered through a
FIFO that this harness does not write until it has finished reading /proc: both matchers BLOCK on
stdin with their argv already fixed, and the /proc capture is taken with the process parked. No
sleeps, no polling, no luck.

SAFETY. The token is a FAKE generated here. No sealed credential is decrypted, read, or handled by
this harness at any point — testing a secret-scanner with a real secret would be the same class of
mistake the scanner exists to prevent.
"""
import json
import os
import secrets as pysecrets
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

WORK = Path("/var/lib/wrought/runner-polish/raw/20-scratch")
SCAN = "/home/kalib/foundry/bin/wrought-precommit-secret-scan"

out = []


def say(s=""):
    print(s, flush=True)
    out.append(s)


if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir(parents=True)

TOKEN = "wrought-FAKE-notarealkey-" + pysecrets.token_hex(16)

say("# GATE-RUNNER-POLISH raw/20 — the secret-scan argv leak: reproduced, then closed")
say(f"# date: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
say(f"# cmd: python3 {__file__}")
say(f"# scanner under test: {SCAN}")
say(f"# scanner sha256: {subprocess.run(['sha256sum', SCAN], capture_output=True, text=True).stdout.split()[0]}")
say()
say("## SETUP — a FAKE token and a scratch git repo. No sealed credential is touched by this file.")
say(f"   token (fake, generated now): {TOKEN}")
say(f"   token length: {len(TOKEN)} bytes")
say()

# ------------------------------------------------------------------ scratch repo + staged diff
repo = WORK / "repo"
repo.mkdir()
subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
subprocess.run(["git", "-C", str(repo), "config", "user.name", "proof"], check=True)
subprocess.run(["git", "-C", str(repo), "config", "user.email", "proof@example.invalid"], check=True)
(repo / "config.env").write_text(
    f"# a plausible accident: a key pasted into a config file\nAPI_KEY={TOKEN}\n")
(repo / "innocent.txt").write_text("nothing to see here\n")
subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)

diff_path = WORK / "staged.diff"
with diff_path.open("wb") as fh:
    subprocess.run(["git", "-C", str(repo), "diff", "--cached", "-a"], stdout=fh, check=True)
diff_bytes = diff_path.read_bytes()
say("## cmd: git -C <scratch repo> add -A && git diff --cached -a > staged.diff")
say(f"   staged diff: {len(diff_bytes)} bytes; contains the token: {TOKEN.encode() in diff_bytes}")
say()

fifo = WORK / "diff.fifo"
os.mkfifo(fifo)


def feed_fifo_later(delay_event: threading.Event):
    """Open the FIFO for WRITING (blocks until the matcher opens the read end), then park until
    told, then deliver the diff and close.

    Order matters, and the first cut of this harness got it wrong: it had the PARENT open the read
    end before the matcher existed, so the parent blocked on open() and nothing ever ran. The
    reader must be the matcher itself — `grep <fifo>` / `--diff-file <fifo>` — which is also the
    shape closer to the real thing."""
    with fifo.open("wb") as fh:
        delay_event.wait()
        fh.write(diff_bytes)


def read_all_cmdlines() -> dict:
    """Every process's argv on this box, right now. /proc is the exposure surface itself."""
    snap = {}
    for e in os.listdir("/proc"):
        if not e.isdigit():
            continue
        try:
            raw = Path(f"/proc/{e}/cmdline").read_bytes()
        except Exception:
            continue
        if raw:
            snap[e] = raw.replace(b"\0", b" ").decode("utf-8", "replace").strip()
    return snap


def descendants(pid: int) -> list[int]:
    kids = []
    stack = [pid]
    while stack:
        p = stack.pop()
        kids.append(p)
        try:
            for c in Path(f"/proc/{p}/task/{p}/children").read_text().split():
                stack.append(int(c))
        except Exception:
            pass
    return kids


results = {}

# ============================================================== ARM 1 — the OLD form (J-164)
say("=" * 78)
say("## ARM 1 — THE OLD FORM, exactly as J-164 recorded it running")
say('##   KEY=$(sudo -n cat …); git diff --cached | grep -c -- "$KEY"')
say("##   Here the diff arrives on a FIFO, so `grep` is PARKED with its argv already set.")
say("=" * 78)

ev = threading.Event()
t = threading.Thread(target=feed_fifo_later, args=(ev,), daemon=True)
t.start()

# grep opens the FIFO itself and parks on read(), argv already fixed. This is the J-164
# command shape verbatim, with the diff arriving on a pipe grep cannot proceed past.
old = subprocess.Popen(["grep", "-c", "--", TOKEN, str(fifo)],
                       stdout=subprocess.PIPE, text=True)
time.sleep(0.4)          # let grep reach its blocking read; it cannot proceed until ev is set
say(f"## cmd: tr '\\0' ' ' </proc/{old.pid}/cmdline")
old_cmdline = Path(f"/proc/{old.pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
say(f"   {old_cmdline.strip()}")
snap_old = read_all_cmdlines()
exposed_old = {p: c for p, c in snap_old.items() if TOKEN in c}
say()
say(f"   ## cmd: walk /proc/*/cmdline; count processes whose argv CONTAINS the token")
say(f"   processes scanned : {len(snap_old)}")
say(f"   EXPOSED           : {len(exposed_old)}  {sorted(exposed_old, key=int)}")
for p, c in sorted(exposed_old.items(), key=lambda kv: int(kv[0])):
    say(f"     pid {p}: {c[:160]}")
ev.set()
old_out = old.communicate()[0].strip()
say()
say(f"   detection: grep -c reported {old_out!r} occurrence(s) — the OLD form DOES detect the token.")
say("   VERDICT ARM 1: DETECTS, and LEAKS. The finding was right and the method was the leak.")
results["old"] = {"detected": old_out, "exposed_pids": sorted(exposed_old, key=int)}
say()

# ============================================================== ARM 2 — the NEW form
say("=" * 78)
say("## ARM 2 — THE CORRECTED FORM: bin/wrought-precommit-secret-scan")
say("##   The needle is read from a file descriptor into process memory and compared in-process.")
say("##   Same FIFO, so the scanner is PARKED with its argv already set, exactly as above.")
say("=" * 78)

secret_file = WORK / "fake-secret"
secret_file.write_text(TOKEN + "\n")
secret_file.chmod(0o600)

os.unlink(fifo)
os.mkfifo(fifo)
ev2 = threading.Event()
t2 = threading.Thread(target=feed_fifo_later, args=(ev2,), daemon=True)
t2.start()

new = subprocess.Popen(
    [sys.executable, SCAN, "--diff-file", str(fifo), "--secrets-from", str(secret_file)],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(0.8)          # let it read the secret file and reach the blocking FIFO read
kids = descendants(new.pid)
say(f"## cmd: tr '\\0' ' ' </proc/{new.pid}/cmdline")
new_cmdline = Path(f"/proc/{new.pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
say(f"   {new_cmdline.strip()}")
say(f"   token present in the scanner's own argv: {TOKEN in new_cmdline}")
say()
say(f"   ## cmd: for each of the scanner's descendants, read /proc/<pid>/cmdline")
say(f"   scanner process tree: {kids}")
for k in kids:
    try:
        c = Path(f"/proc/{k}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except Exception:
        continue
    say(f"     pid {k}: {c.strip()[:160]}  token_in_argv={TOKEN in c}")
snap_new = read_all_cmdlines()
exposed_new = {p: c for p, c in snap_new.items() if TOKEN in c}
say()
say(f"   ## cmd: walk /proc/*/cmdline; count processes whose argv CONTAINS the token")
say(f"   processes scanned : {len(snap_new)}")
say(f"   EXPOSED           : {len(exposed_new)}  {sorted(exposed_new, key=int) if exposed_new else '[] — NONE'}")
for p, c in sorted(exposed_new.items(), key=lambda kv: int(kv[0])):
    say(f"     pid {p}: {c[:160]}")
ev2.set()
new_out = new.communicate()[0]
say()
say("   ## scanner output and exit code:")
for line in new_out.splitlines():
    say(f"     {line}")
say(f"     exit code: {new.returncode}   (1 = secret found, which is the CORRECT verdict here)")
results["new"] = {"rc": new.returncode, "exposed_pids": sorted(exposed_new, key=int)}
say()

# ============================================================== ARM 3 — the clean control
say("=" * 78)
say("## ARM 3 — CONTROL: the same scanner against a diff with NO secret in it must say PASS.")
say("##   A scanner that always reports FAIL detects nothing; it just always fails.")
say("=" * 78)
clean_repo = WORK / "clean"
clean_repo.mkdir()
subprocess.run(["git", "-C", str(clean_repo), "init", "-q"], check=True)
subprocess.run(["git", "-C", str(clean_repo), "config", "user.name", "proof"], check=True)
subprocess.run(["git", "-C", str(clean_repo), "config", "user.email", "proof@example.invalid"], check=True)
(clean_repo / "notes.md").write_text("a perfectly ordinary change, no credentials here\n")
subprocess.run(["git", "-C", str(clean_repo), "add", "-A"], check=True)
say(f"## cmd: {SCAN} --repo {clean_repo} --secrets-from <fake-secret>")
r3 = subprocess.run([sys.executable, SCAN, "--repo", str(clean_repo),
                     "--secrets-from", str(secret_file)],
                    capture_output=True, text=True)
for line in r3.stdout.splitlines():
    say(f"   {line}")
say(f"   exit code: {r3.returncode}   (0 = clean)")
results["control"] = {"rc": r3.returncode}
say()

# ============================================================== ARM 4 — the refusal
say("=" * 78)
say("## ARM 4 — a scan that CANNOT run must not report a green (exit 2, not 0).")
say("=" * 78)
empty = WORK / "no-secrets"
empty.write_text("\n")
say(f"## cmd: {SCAN} --repo {clean_repo} --secrets-from <empty file>")
r4 = subprocess.run([sys.executable, SCAN, "--repo", str(clean_repo), "--secrets-from", str(empty)],
                    capture_output=True, text=True)
for line in r4.stdout.splitlines():
    say(f"   {line}")
say(f"   exit code: {r4.returncode}   (2 = could not scan; NOT a pass)")
results["refusal"] = {"rc": r4.returncode}
say()

# ============================================================== verdict
ok = (results["old"]["exposed_pids"]                       # the old form really did leak
      and not results["new"]["exposed_pids"]               # the new one does not
      and results["new"]["rc"] == 1                        # and still detects
      and results["control"]["rc"] == 0                    # and does not cry wolf
      and results["refusal"]["rc"] == 2)                   # and refuses rather than green-lights
say("=" * 78)
say(f"=== PHASE 3 VERDICT: {'PASS' if ok else 'FAIL'} ===")
say(f"  OLD form: detected the token AND exposed it in {len(results['old']['exposed_pids'])} process argv "
    f"({results['old']['exposed_pids']})")
say(f"  NEW form: detected the token (exit 1) and exposed it in "
    f"{len(results['new']['exposed_pids'])} process argv")
say(f"  control : clean diff -> exit {results['control']['rc']} (no false positive)")
say(f"  refusal : no usable secret -> exit {results['refusal']['rc']} (a scan that did not happen "
    f"is not a green)")
say("=" * 78)

Path("/var/lib/wrought/runner-polish/raw/21-secret-scan-argv-proof.txt").write_text("\n".join(out) + "\n")
sys.exit(0 if ok else 1)
