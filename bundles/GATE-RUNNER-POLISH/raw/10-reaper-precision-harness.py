#!/usr/bin/env python3
"""GATE-RUNNER-POLISH Phase 2 — PROVE the reaper's survivor test is precise.

Imports the REAL functions out of bin/wrought-runner (no reimplementation, no stub) and runs
them against three deliberately-constructed processes:

  DECOY-A  /usr/bin/bash      — command line CONTAINS "qemu-system-x86_64", exe is bash
  DECOY-B  /usr/bin/python3   — command line CONTAINS "qemu-system-x86_64", exe is python3
  REAL     qemu-system-x86_64 — an actual guest-shaped process, launched as a descendant of a
                                `systemd-run --user --scope` exactly as a gate's guest would be
                                (EXECUTOR-RAILS §13.1), halted at startup (-S), no disk, no net,
                                no display, 128 MiB.

GROUND TRUTH is what the functions return, and then what is alive afterwards.
Both arms of the prompt's Phase-2 block must hold:
  - the decoys must NOT be swept;
  - the real scope-descendant guest MUST be.

Safety: the harness REFUSES to call reap() if the residue diff contains anything other than the
one REAL pid it started (no domains, no listeners, no unexpected qemu), and it tears its own
decoys down by RECORDED PID, never by pattern (EXECUTOR-RAILS §3).
"""
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RUNNER = "/home/kalib/foundry/bin/wrought-runner"
WORK = Path("/var/lib/wrought/runner-polish/raw/10-scratch")

# spec_from_file_location returns None for an extensionless path, so name the loader.
_loader = importlib.machinery.SourceFileLoader("wrought_runner", RUNNER)
spec = importlib.util.spec_from_loader("wrought_runner", _loader)
wr = importlib.util.module_from_spec(spec)
_loader.exec_module(wr)

CFG = {"reaper": {"enabled": True, "qemu_pattern": "qemu-system", "terminate_grace_sec": 5}}

if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir(parents=True)
rlog = wr.RunLog(WORK, wr.utcnow())

out = []


def say(s=""):
    print(s, flush=True)
    out.append(s)


say("# GATE-RUNNER-POLISH raw/10 — the reaper's survivor test, PROVEN precise")
say(f"# date: {wr.utcnow()}")
say(f"# cmd: python3 {__file__}")
say(f"# runner under test: {RUNNER}")
say(f"# runner sha256: {subprocess.run(['sha256sum', RUNNER], capture_output=True, text=True).stdout.split()[0]}")
say()

# --------------------------------------------------------------------- snapshot BEFORE
before = wr.residue_snapshot(CFG)
say("## STEP 1 — residue_snapshot() BEFORE anything is started")
say(f"   qemu processes : {len(before['qemu'])}  {sorted(before['qemu'])}")
say(f"   libvirt domains: {before['domains']}")
say(f"   listeners      : {len(before['listeners'])}")
say(f"   notes          : {before['notes']}")
say()

# --------------------------------------------------------------------- start the three
DECOY_STRING = "qemu-system-x86_64 -m 8192 -nographic -drive file=overlay.qcow2"

decoy_a = subprocess.Popen(
    ["/usr/bin/bash", "-c", f"sleep 900; :  # monitoring the guest: {DECOY_STRING}"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
decoy_b = subprocess.Popen(
    ["/usr/bin/python3", "-c", f"import time; time.sleep(900)  # watchdog for {DECOY_STRING}"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

decoy_note = WORK / "qemu-system-x86_64-launch-notes.txt"
decoy_note.write_text("a gate's own notes file, being tailed by a monitoring command\n")
decoy_c = subprocess.Popen(
    ["/usr/bin/tail", "-f", str(decoy_note)],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

unit = f"wrought-polish-decoyproof-{int(time.time())}.scope"
real = subprocess.Popen(
    ["systemd-run", "--user", "--scope", "--quiet", f"--unit={unit}",
     "/usr/bin/qemu-system-x86_64", "-S", "-display", "none", "-machine", "none",
     "-m", "128", "-nodefaults", "-no-user-config"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
time.sleep(3)

# The REAL qemu pid is a descendant of the systemd-run wrapper, not the wrapper itself.
real_pids = [p for p, m in wr.qemu_processes("qemu-system").items()
             if p not in before["qemu"]]

say("## STEP 2 — three processes started")
say(f"   DECOY-A  pid {decoy_a.pid}  exe=/usr/bin/bash     (cmdline CONTAINS 'qemu-system-x86_64')")
say(f"   DECOY-B  pid {decoy_b.pid}  exe=/usr/bin/python3  (cmdline CONTAINS 'qemu-system-x86_64')")
say(f"   DECOY-C  pid {decoy_c.pid}  exe=/usr/bin/tail     (ARGUMENT is a path containing 'qemu-system-x86_64')")
say(f"   REAL     scope unit {unit}; qemu pid(s) {real_pids}")
say()
say("   ## cmd: for p in <the three>; do readlink /proc/$p/exe; done   — ground truth on identity")
for label, pid in (("DECOY-A", decoy_a.pid), ("DECOY-B", decoy_b.pid), ("DECOY-C", decoy_c.pid),
                   *[("REAL", int(p)) for p in real_pids]):
    try:
        exe = os.readlink(f"/proc/{pid}/exe")
    except Exception as e:
        exe = f"<unreadable: {e}>"
    cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    say(f"   {label:8} pid {pid:<8} exe={exe}")
    say(f"   {'':8}          cmdline={cmd.strip()[:150]}")
say()

# --------------------------------------------------------------------- the OLD test
say("## STEP 3 — THE DEFECT, reproduced. The OLD test was `pgrep -a -f \"qemu-system\"`.")
say("   ## cmd: pgrep -a -f qemu-system")
old = subprocess.run(["pgrep", "-a", "-f", "qemu-system"], capture_output=True, text=True)
old_pids = [ln.split()[0] for ln in old.stdout.splitlines()]
for ln in old.stdout.splitlines():
    say(f"   {ln[:170]}")
say(f"   => OLD test matched {len(old_pids)} pids: {sorted(old_pids)}")
say(f"      DECOY-A ({decoy_a.pid}) matched by the OLD test: {str(decoy_a.pid) in old_pids}")
say(f"      DECOY-B ({decoy_b.pid}) matched by the OLD test: {str(decoy_b.pid) in old_pids}")
say(f"      DECOY-C ({decoy_c.pid}) matched by the OLD test: {str(decoy_c.pid) in old_pids}")
say("   Every one of those would have been enumerated, SIGTERMed/SIGKILLed, and would have")
say("   LATCHED a `gate-residue` breaker.")
say()

# --------------------------------------------------------------------- the NEW test
after = wr.residue_snapshot(CFG)
new = wr.residue_diff(before, after)
say("## STEP 4 — THE FIX. residue_snapshot() + residue_diff() with the executable-identity test.")
say("   ## cmd: wr.residue_diff(wr.residue_snapshot(cfg)_before, wr.residue_snapshot(cfg)_after)")
say(json.dumps(new, indent=2, sort_keys=True))
say()
matched = sorted(new["qemu"])
say(f"   => NEW test matched {len(matched)} pids: {matched}")
say(f"      DECOY-A ({decoy_a.pid}) matched by the NEW test: {str(decoy_a.pid) in new['qemu']}")
say(f"      DECOY-B ({decoy_b.pid}) matched by the NEW test: {str(decoy_b.pid) in new['qemu']}")
say(f"      DECOY-C ({decoy_c.pid}) matched by the NEW test: {str(decoy_c.pid) in new['qemu']}")
say(f"      REAL    {real_pids} matched by the NEW test: {all(p in new['qemu'] for p in real_pids)}")
say()

# --------------------------------------------------------------------- safety gate, then reap
problems = []
if {str(decoy_a.pid), str(decoy_b.pid), str(decoy_c.pid)} & set(new["qemu"]):
    problems.append("a decoy is in the residue diff — the fix does NOT hold")
if not real_pids or not all(p in new["qemu"] for p in real_pids):
    problems.append("the real guest is NOT in the residue diff — the fix over-corrected")
if sorted(new["qemu"]) != sorted(real_pids):
    problems.append(f"diff qemu set {sorted(new['qemu'])} != the one process this harness started {sorted(real_pids)}")
if new["domains"]:
    problems.append(f"unexpected new domains {new['domains']} — refusing to reap")
if new["listeners"]:
    problems.append(f"unexpected new listeners {sorted(new['listeners'])} — refusing to reap")

if problems:
    say("## STEP 5 — REFUSING TO REAP. The harness will not signal anything it did not start:")
    for p in problems:
        say(f"   - {p}")
else:
    say("## STEP 5 — safety gate PASSED (diff is exactly the one guest this harness started).")
    say("   ## cmd: wr.reap(cfg, new, rlog, 'GATE-RUNNER-POLISH-PROOF')")
    killed = wr.reap(CFG, new, rlog, "GATE-RUNNER-POLISH-PROOF")
    for k in killed:
        say(f"   REAPED: {k}")
say()

time.sleep(2)


def alive(pid):
    """Alive means RUNNING, not merely addressable. `os.kill(pid, 0)` succeeds on a ZOMBIE, so
    the first run of this harness reported a SIGKILLed guest as alive=True. Read the state."""
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("State:"):
                return line.split()[1] != "Z"
    except FileNotFoundError:
        return False
    except Exception:
        pass
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


say("## STEP 6 — GROUND TRUTH after the sweep: who is still alive?")
say(f"   DECOY-A pid {decoy_a.pid}  alive={alive(decoy_a.pid)}   <- MUST be True (not a guest)")
say(f"   DECOY-B pid {decoy_b.pid}  alive={alive(decoy_b.pid)}   <- MUST be True (not a guest)")
say(f"   DECOY-C pid {decoy_c.pid}  alive={alive(decoy_c.pid)}   <- MUST be True (not a guest)")
for p in real_pids:
    say(f"   REAL    pid {p}  alive={alive(p)}   <- MUST be False (a real scope-descendant guest)")
say()

verdict_ok = (not problems and alive(decoy_a.pid) and alive(decoy_b.pid)
              and alive(decoy_c.pid) and not any(alive(p) for p in real_pids))
say(f"=== VERDICT: {'PASS' if verdict_ok else 'FAIL'} ===")
say("The survivor test now matches the process's EXECUTABLE (/proc/<pid>/exe, comm as fallback),")
say("not an arbitrary command-line substring. A command line that merely MENTIONS a guest is no")
say("longer swept; a real guest still is.")
say()

# --------------------------------------------------------------------- enumerated teardown
say("## STEP 7 — teardown, ENUMERATED by recorded pid (EXECUTOR-RAILS §3), never by pattern.")
for label, pid in (("DECOY-A", decoy_a.pid), ("DECOY-B", decoy_b.pid), ("DECOY-C", decoy_c.pid)):
    try:
        os.kill(pid, 15)
        say(f"   {label} pid {pid}: SIGTERM sent")
    except ProcessLookupError:
        say(f"   {label} pid {pid}: already gone")
time.sleep(1)
subprocess.run(["systemctl", "--user", "stop", unit], capture_output=True, check=False)
say(f"   scope {unit}: stopped")
real.wait(timeout=10)
for d in (decoy_a, decoy_b, decoy_c):
    try:
        d.wait(timeout=10)
    except Exception:
        pass
say(f"   DECOY-A alive={alive(decoy_a.pid)}  DECOY-B alive={alive(decoy_b.pid)}  "
    f"DECOY-C alive={alive(decoy_c.pid)}  (all MUST be False now)")
say()
final = wr.residue_snapshot(CFG)
fdiff = wr.residue_diff(before, final)
say("## STEP 8 — closing bracket: residue_diff(before, now) must be EMPTY.")
say(json.dumps(fdiff, indent=2, sort_keys=True))
say(f"=== HARNESS LEFT NOTHING BEHIND: {not fdiff['any']} ===")

Path("/var/lib/wrought/runner-polish/raw/11-reaper-precision-proof.txt").write_text(
    "\n".join(out) + "\n")
sys.exit(0 if verdict_ok and not fdiff["any"] else 1)
