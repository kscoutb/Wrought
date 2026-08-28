#!/usr/bin/env python3
"""wrought-runner — the day-long, operator-started batch runner for approved gate prompts.

Started MANUALLY by the operator once per day (GATE-RUNNER, operator ruling 2026-08-21). It is
NOT a daemon and installs no timer: the operator's manual start each day IS the human gate, and
forward progress is gated by the APPROVED state the advisor and operator set at the daily ferry.

It walks the courier QUEUE, runs each APPROVED gate in a FRESH sessionless `claude -p` context
inside a kernel-contained systemd scope under a default-deny permission mode, verifies the gate's
work MECHANICALLY, and halts on any circuit breaker.

Interpreter note: this is `#!/usr/bin/env python3`, not the repo's usual
`#!/opt/wrought/venv-orch/bin/python`. Deliberate: the runner supervises gates, and a gate may
legitimately rebuild that venv. A supervisor must not depend on the thing it supervises. The
script is stdlib-only by rule; the observed interpreter is pinned in PROPOSED-PINS-DELTA.md.

EVERY threshold in the shipped config is PROPOSED-UNRATIFIED. CLAUDE.md forbids inventing
thresholds; they are listed in build-evidence/runner/PROPOSED-PINS-DELTA.md for operator ratification.

Phase-1 evidence this design rests on (build-evidence/runner/raw/, GATE-RUNNER 2026-08-21):
  raw/06  `acceptEdits` and `auto` SILENTLY RAN an un-allowlisted Bash call; only `dontAsk` and
          `manual` are default-deny-with-allowlist. Every case exited rc=0, INCLUDING every
          denial -> the exit integer never classifies a run.
  raw/07  PreToolUse hooks DO fire under `claude -p`, but a MALFORMED settings file is SILENTLY
          ignored under -p (rc=0, empty stderr, hook layer gone) -> the runner json-validates the
          hook settings before every launch, and never load-bears on hooks.
  raw/08  BASH_DEFAULT_TIMEOUT_MS BACKGROUNDS an overrunning command rather than killing it, and
          --max-budget-usd overshot its cap 4.6x -> the kernel scope is the only real kill, and
          the budget cap is a soft ceiling that must be reconciled after the fact.
  raw/05  Per-project auto-memory is a live cross-invocation channel -> fenced per gate.

GATE-RUNNER-HARDEN evidence (build-evidence/runner-harden/raw/, 2026-08-28) — the two blockers
that stood between this runner and unattended use:
  raw/06  The steering surfaces are TWO, with DIFFERENT keys: the peer LISTING is keyed on
          $HOME, the addressable SOCKET on $XDG_RUNTIME_DIR/cc-socks/<pid>.sock. A private HOME
          alone leaves the socket in the shared directory. Both are now fenced per gate, and
          the measured minimum HOME is three files. Auth and the gate's own courier push both
          survive the isolated shape (probe D2 pushed to origin/main from inside it).
  raw/09  A post-gate orphan sweep, because a gate that dies does not reap its own guest:
          GATE-J0B-SURFACE left one running for seven days with the API key in a proxy's memory.
  raw/02  The CLI SELF-UPDATED 2.1.238 -> 2.1.250 underneath the pin on 2026-08-28. Every
          containment behaviour above was measured on 2.1.238. See the report's drift section.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_CONFIG = "/etc/wrought/runner.conf"

# The QUEUE vocabulary. APPROVED is NEW with this gate and is flagged for advisor ratification.
QUEUE_STATUSES = {"QUEUED", "APPROVED", "RUNNING", "BUNDLED", "ADJUDICATED", "NOT RUN", "HALTED"}
RUNNABLE_STATUS = "APPROVED"

ROW_RE = re.compile(r"^\|(?P<gate>[^|]*)\|(?P<status>[^|]*)\|(?P<notes>.*)\|\s*$")
GATE_RE = re.compile(r"^GATE-[A-Z0-9][A-Z0-9-]*$")
ALLOWED_TOOLS_RE = re.compile(r"^ALLOWED-TOOLS:[ \t]*(?P<tools>.+?)[ \t]*$", re.M)
MAX_BUDGET_RE = re.compile(r"^MAX-BUDGET-USD:[ \t]*(?P<usd>[0-9]+(?:\.[0-9]+)?)[ \t]*$", re.M)
ADD_DIRS_RE = re.compile(r"^ADD-DIRS:[ \t]*(?P<dirs>.+?)[ \t]*$", re.M)

# api_error_status values that are worth a bounded retry rather than a failure.
RETRYABLE_HTTP = {429, 529}

# Breakers that STOP THIS RUN but do NOT latch. The GATE-RUNNER prompt distinguishes them:
# the gate-count cap and the wall-clock budget mean "stop, wait for the daily ferry", whereas
# the consecutive-failure ledger means "disable further runs, require operator reset". If every
# halt latched, a batch that simply reached its own cap would poison the NEXT morning's manual
# start — the operator's day-2 run would refuse on a run that ended normally.
NON_LATCHING = {"gate-cap", "wall-clock"}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Halt(Exception):
    """A circuit breaker tripped. The batch stops and waits for the operator."""

    def __init__(self, reason: str, breaker: str):
        super().__init__(reason)
        self.reason = reason
        self.breaker = breaker


# --------------------------------------------------------------------------- config


def load_config(path: str) -> dict:
    """Strictly parse the config. A config that does not parse is a refusal to start.

    Never `source`d, never eval'd: raw/07 c4 showed what silent config tolerance costs.
    """
    p = Path(path)
    if not p.is_file():
        sys.exit(f"wrought-runner: config not found: {p}  (refusing to start)")
    try:
        cfg = json.loads(p.read_text())
    except Exception as e:
        sys.exit(f"wrought-runner: config {p} does not parse as JSON: {e}  (refusing to start)")
    if not isinstance(cfg, dict):
        sys.exit(f"wrought-runner: config {p} is not a JSON object  (refusing to start)")
    if cfg.get("schema_version") != SCHEMA_VERSION:
        sys.exit(f"wrought-runner: config schema_version != {SCHEMA_VERSION}  (refusing to start)")
    # `ephemeral_home` and `reaper` are REQUIRED, not optional-with-a-default. Both are safety
    # controls added by GATE-RUNNER-HARDEN, and a config predating them would otherwise start
    # silently unhardened — a gate child back on the shared socket, and no post-gate sweep.
    # Refusing to start is the loud failure; a quiet default is the one that costs seven days.
    required = ("courier_dir", "gate_cwd", "state_dir", "freeze_paths", "claude_bin",
                "hook_settings", "permission_mode", "limits", "pacing", "breakers",
                "course_check", "git", "ephemeral_home", "reaper")
    missing = [k for k in required if k not in cfg]
    if missing:
        sys.exit(f"wrought-runner: config missing required keys: {missing}  (refusing to start)")
    cfg["_config_path"] = str(p.resolve())
    if cfg["permission_mode"] not in ("dontAsk", "manual"):
        # raw/06: these are the only two modes measured to be default-deny-with-allowlist.
        sys.exit(f"wrought-runner: permission_mode {cfg['permission_mode']!r} is not a measured "
                 f"default-deny mode (dontAsk|manual)  (refusing to start)")
    return cfg


# --------------------------------------------------------------------------- run log


class RunLog:
    """Append-only evidence for one run. Never overwritten (EXECUTOR-RAILS S4)."""

    def __init__(self, state_dir: Path, started: str):
        self.dir = state_dir / "runs" / started.replace(":", "").replace("-", "")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "run.jsonl"
        self.log(kind="run-start", at=started)

    def log(self, **rec) -> None:
        rec.setdefault("at", utcnow())
        with self.path.open("a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def say(self, msg: str) -> None:
        print(f"[{utcnow()}] {msg}", flush=True)
        self.log(kind="note", msg=msg)


# --------------------------------------------------------------------------- git


def git(repo: Path, *args: str, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=check, timeout=timeout)


def git_pull(repo: Path, cfg: dict, rlog: RunLog) -> None:
    tries = int(cfg["git"]["push_retry_max"])
    for i in range(1, tries + 1):
        r = git(repo, "pull", "--rebase", check=False, timeout=180)
        if r.returncode == 0:
            return
        rlog.log(kind="git-pull-retry", attempt=i, rc=r.returncode, stderr=r.stderr[-800:])
        time.sleep(int(cfg["git"]["push_retry_sleep_sec"]))
    raise Halt("git pull --rebase failed after retries", "git")


def git_push(repo: Path, cfg: dict, rlog: RunLog, message: str) -> None:
    """Commit whatever is staged-able and push, rebasing on races (gates push here too)."""
    git(repo, "add", "-A", check=False)
    st = git(repo, "status", "--porcelain", check=False)
    if st.stdout.strip():
        git(repo, "-c", "user.name=Kalib Bailey",
            "-c", "user.email=anthropic.spotlight807@passmail.net",
            "commit", "-q", "-m", message, check=False)
    tries = int(cfg["git"]["push_retry_max"])
    for i in range(1, tries + 1):
        r = git(repo, "push", "origin", "HEAD", check=False, timeout=180)
        if r.returncode == 0:
            return
        rlog.log(kind="git-push-retry", attempt=i, rc=r.returncode, stderr=r.stderr[-800:])
        git(repo, "pull", "--rebase", check=False, timeout=180)
        time.sleep(int(cfg["git"]["push_retry_sleep_sec"]))
    raise Halt("git push failed after retries", "git")


# --------------------------------------------------------------------------- QUEUE


def parse_queue(queue_path: Path) -> list[dict]:
    """Strict row parse. Anything ambiguous is a refusal, never a best-effort guess."""
    rows = []
    for n, line in enumerate(queue_path.read_text().splitlines(), 1):
        m = ROW_RE.match(line)
        if not m:
            continue
        gate = m.group("gate").strip().strip("`").strip()
        status = m.group("status").strip().strip("`").strip()
        if not GATE_RE.match(gate):
            continue          # legend rows, header rows, separators
        if status not in QUEUE_STATUSES:
            raise Halt(f"QUEUE row {n} for {gate} has unknown status {status!r}; "
                       f"known: {sorted(QUEUE_STATUSES)}", "queue-parse")
        rows.append({"line": n, "gate": gate, "status": status,
                     "notes": m.group("notes").strip(), "raw": line})
    names = [r["gate"] for r in rows]
    dupes = sorted({g for g in names if names.count(g) > 1})
    if dupes:
        raise Halt(f"QUEUE has duplicate rows for {dupes}; refusing to run an ambiguous queue",
                   "queue-parse")
    return rows


def set_queue_status(queue_path: Path, gate: str, new_status: str, note_append: str = "") -> None:
    lines = queue_path.read_text().splitlines(keepends=True)
    out, hits = [], 0
    for line in lines:
        m = ROW_RE.match(line.rstrip("\n"))
        if m and m.group("gate").strip().strip("`").strip() == gate:
            notes = m.group("notes").strip()
            if note_append:
                notes = f"{notes} {note_append}".strip()
            out.append(f"| `{gate}` | `{new_status}` | {notes} |\n")
            hits += 1
        else:
            out.append(line)
    if hits != 1:
        raise Halt(f"set_queue_status matched {hits} rows for {gate} (expected exactly 1)",
                   "queue-parse")
    queue_path.write_text("".join(out))


# --------------------------------------------------------------------------- freeze


def hash_paths(paths: list[str]) -> dict:
    out = {}
    for p in paths:
        f = Path(p)
        if not f.exists():
            out[p] = "ABSENT"
            continue
        h = hashlib.sha256()
        with f.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        out[p] = h.hexdigest()
    return out


def freeze_diff(before: dict, after: dict) -> list[str]:
    return [f"{k}: {before.get(k)} -> {after.get(k)}"
            for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)]


# --------------------------------------------------------------------------- memory fence


def memory_snapshot(mem_dir: Path, dest: Path) -> dict:
    """Copy the per-project auto-memory dir aside and hash it (raw/05)."""
    if dest.exists():
        shutil.rmtree(dest)
    if mem_dir.is_dir():
        shutil.copytree(mem_dir, dest)
    else:
        dest.mkdir(parents=True, exist_ok=True)
    return {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(dest.rglob("*")) if p.is_file()}


def memory_restore(mem_dir: Path, snap_dir: Path) -> None:
    if mem_dir.exists():
        shutil.rmtree(mem_dir)
    if snap_dir.exists():
        shutil.copytree(snap_dir, mem_dir)


# ------------------------------------------------- ephemeral HOME (steering breaker, BLOCKER 1)


# The MEASURED minimum a headless `claude -p` gate child needs in a private HOME
# (GATE-RUNNER-HARDEN raw/06, incremental seeding):
#   .claude/.credentials.json   authentication.   Without it: is_error=true,
#                               terminal_reason=api_error, "Not logged in · Please run /login".
#   .gitconfig                  identity + credential.helper=store, for the gate's OWN push.
#   .git-credentials            the https push token.
# `.claude.json` is deliberately NOT seeded: the CLI writes a fresh one per gate, and that is
# the point of the fence rather than a gap in it.
EPHEMERAL_HOME_SEED = (".claude/.credentials.json", ".gitconfig", ".git-credentials")


def make_ephemeral_home(cfg: dict, gate: str, rlog: RunLog) -> tuple[Path | None, Path | None]:
    """Build this gate's private HOME and private runtime dir. Returns (home, runtime_dir).

    BLOCKER 1, closed by measurement rather than by assumption. raw/06 isolates TWO independent
    surfaces with DIFFERENT keys, and closing one does not close the other:
      * the PEER LISTING is keyed on $HOME      — probe E3 vs F2;
      * the ADDRESSABLE SOCKET is keyed on $XDG_RUNTIME_DIR — probe D2 vs E3.
    A private HOME alone leaves the child's socket sitting in the shared cc-socks directory,
    where it is still addressable by path. NOT LISTED IS NOT NOT ADDRESSABLE, so we do both.

    Returns (None, None) when the fence is disabled, which restores the pre-hardening behaviour
    and is a config decision the operator can see rather than a silent fallback.
    """
    fence = cfg.get("ephemeral_home", {})
    if not fence.get("enabled", True):
        rlog.say(f"{gate}: ephemeral HOME fence DISABLED by config — the child will run on the "
                 f"real HOME and IS discoverable by other local sessions")
        return None, None
    root = Path(fence["root"])
    root.mkdir(parents=True, exist_ok=True)
    root.chmod(0o700)
    home = root / f"{gate}-{int(time.time())}"
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True)
    home.chmod(0o700)
    src_home = Path(os.path.expanduser("~"))
    seeded, missing = [], []
    for rel in fence.get("seed", EPHEMERAL_HOME_SEED):
        src = src_home / rel
        if not src.is_file():
            missing.append(rel)
            continue
        dst = home / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.parent.chmod(0o700)
        shutil.copyfile(src, dst)
        dst.chmod(0o600)
        seeded.append(rel)
    if missing:
        # Loud, never papered over: a missing credential means the gate cannot authenticate or
        # cannot push, and finding that out from the child's own confused output is worse.
        raise Halt(f"{gate}: ephemeral HOME seed is incomplete — {missing} not found under "
                   f"{src_home}. The gate would fail to authenticate or fail to push.",
                   "ephemeral-home")
    runtime = home / "xdg-runtime"
    runtime.mkdir()
    runtime.chmod(0o700)
    rlog.log(kind="ephemeral-home", gate=gate, home=str(home), runtime=str(runtime),
             seeded=seeded)
    rlog.say(f"{gate}: private HOME {home} (seeded {seeded}), private runtime dir {runtime}")
    return home, runtime


def teardown_ephemeral_home(home: Path | None, rlog: RunLog, gate: str) -> None:
    """Tear the ephemeral HOME down WITH the gate. It holds live credential copies."""
    if home is None:
        return
    try:
        shutil.rmtree(home)
        rlog.log(kind="ephemeral-home-torn-down", gate=gate, home=str(home))
    except Exception as e:
        # Loud: a surviving ephemeral HOME is two secrets left on disk.
        rlog.say(f"{gate}: WARNING — could not remove ephemeral HOME {home}: {e}")
        rlog.log(kind="ephemeral-home-teardown-failed", gate=gate, home=str(home), err=str(e))


# ------------------------------------------------------------- orphan reaper (BLOCKER 2)


def _libvirtd_active() -> bool:
    """Is libvirtd ALREADY running? Never socket-activate it just to look.

    docs/PHASE-J-STATE records that libvirtd on this box is monolithic and socket-activated: a
    bare `virsh list --all` STARTS it. A sweep that starts a daemon on every gate is a side
    effect the sweep exists to prevent, so the domain probe is conditional. Nothing is lost by
    skipping it — a libvirt domain always has a qemu-system process, which the PID scan sees
    regardless of who its parent is.
    """
    r = subprocess.run(["systemctl", "is-active", "--quiet", "libvirtd.service"], check=False)
    return r.returncode == 0


def residue_snapshot(cfg: dict) -> dict:
    """Snapshot the three things a gate can strand: guests, domains, credential-holding ports."""
    snap = {"qemu": {}, "domains": [], "listeners": {}, "notes": []}

    pat = cfg.get("reaper", {}).get("qemu_pattern", "qemu-system")
    r = subprocess.run(["pgrep", "-a", "-f", pat], capture_output=True, text=True, check=False)
    for line in r.stdout.splitlines():
        pid, _, cmdline = line.partition(" ")
        if pid.strip().isdigit():
            snap["qemu"][pid.strip()] = cmdline.strip()[:300]

    if _libvirtd_active():
        d = subprocess.run(["virsh", "list", "--all", "--name"],
                           capture_output=True, text=True, check=False, timeout=30)
        snap["domains"] = sorted(n for n in d.stdout.split() if n.strip())
    else:
        snap["notes"].append("libvirtd inactive — domain probe skipped, not socket-activated")

    ss = subprocess.run(["ss", "-lntpH"], capture_output=True, text=True, check=False)
    for line in ss.stdout.splitlines():
        f = line.split()
        if len(f) < 4:
            continue
        local = f[3]
        m = re.search(r"pid=(\d+)", line)
        snap["listeners"][f"{local}"] = m.group(1) if m else "?"
    return snap


def residue_diff(before: dict, after: dict) -> dict:
    """NEW survivors only. A guest that was already running when the gate started is not the
    gate's residue, and blaming a gate for its predecessor's mess is how a loud rule gets
    switched off."""
    new = {
        "qemu": {k: v for k, v in after["qemu"].items() if k not in before["qemu"]},
        "domains": [d for d in after["domains"] if d not in before["domains"]],
        "listeners": {k: v for k, v in after["listeners"].items() if k not in before["listeners"]},
    }
    new["any"] = bool(new["qemu"] or new["domains"] or new["listeners"])
    return new


def reap(cfg: dict, new: dict, rlog: RunLog, gate: str) -> list[str]:
    """Terminate every NEW survivor, one at a time, each named in the log. Enumerated, never
    globbed (EXECUTOR-RAILS §3) — the sweep says exactly what it killed and why."""
    grace = int(cfg.get("reaper", {}).get("terminate_grace_sec", 5))
    killed = []
    for name in new["domains"]:
        r = subprocess.run(["virsh", "destroy", name], capture_output=True, text=True,
                           check=False, timeout=60)
        killed.append(f"libvirt domain {name!r}: virsh destroy rc={r.returncode} "
                      f"{r.stderr.strip()[:160]}")
    pids = set(new["qemu"]) | {v for v in new["listeners"].values() if v.isdigit()}
    for pid in sorted(pids, key=int):
        what = new["qemu"].get(pid) or next(
            (f"listener on {k}" for k, v in new["listeners"].items() if v == pid), "unknown")
        try:
            os.kill(int(pid), 15)
        except ProcessLookupError:
            killed.append(f"pid {pid} ({what}): already gone at SIGTERM")
            continue
        except Exception as e:
            killed.append(f"pid {pid} ({what}): SIGTERM failed: {e}")
            continue
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            try:
                os.kill(int(pid), 0)
            except ProcessLookupError:
                break
            time.sleep(0.25)
        try:
            os.kill(int(pid), 0)
            os.kill(int(pid), 9)
            killed.append(f"pid {pid} ({what}): SIGTERM ignored for {grace}s, SIGKILLed")
        except ProcessLookupError:
            killed.append(f"pid {pid} ({what}): terminated by SIGTERM")
    for k in killed:
        rlog.log(kind="reaped", gate=gate, what=k)
        rlog.say(f"{gate}: REAPED {k}")
    return killed


# --------------------------------------------------------------------------- child


def build_child_env(cfg: dict, child_home: Path | None = None) -> dict:
    """Allowlist, not blacklist.

    Two reasons this is an allowlist. (1) A blacklist rots the next time the CLI adds a variable.
    (2) An interactive Claude Code session exports CLAUDE_CODE_MESSAGING_SOCKET and
    CLAUDE_CODE_MESSAGING_TOKEN — the cross-session steering channel. Never inheriting them IS
    the "refuse inbound cross-session messages" breaker: an address that was never handed over
    cannot be used to steer the gate.

    `child_home` overrides HOME with the gate's ephemeral HOME (GATE-RUNNER-HARDEN raw/06). Note
    what is deliberately NOT overridden here: XDG_RUNTIME_DIR stays REAL in this env, because
    `systemd-run --user` needs the real user bus to exist. The child's PRIVATE runtime dir is
    applied one level in, by an `env` prefix on the claude argv — measured in probe C1, where
    overriding it out here killed the launcher with
    "Failed to connect to user scope bus via local transport: No such file or directory".
    """
    lim = cfg["limits"]
    keep = ("HOME", "PATH", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL",
            "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    if child_home is not None:
        env["HOME"] = str(child_home)
    env["TERM"] = "dumb"
    env["CI"] = "1"
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(lim["max_output_tokens"])
    env["BASH_DEFAULT_TIMEOUT_MS"] = str(lim["bash_default_timeout_ms"])
    if cfg.get("_config_path"):
        env["WROUGHT_RUNNER_CONFIG"] = cfg["_config_path"]
    for extra in cfg.get("extra_child_env", {}).items():
        env[extra[0]] = str(extra[1])
    return env


def validate_hook_settings(path: Path) -> None:
    """raw/07 c4: a malformed settings file is SILENTLY ignored under -p and the hook layer
    vanishes with rc=0 and an empty stderr. So we parse it ourselves before every launch."""
    if not path.is_file():
        raise Halt(f"hook settings {path} is missing", "hook-settings")
    try:
        doc = json.loads(path.read_text())
    except Exception as e:
        raise Halt(f"hook settings {path} does not parse ({e}); "
                   f"claude -p would ignore it SILENTLY", "hook-settings") from e
    if not isinstance(doc.get("hooks"), dict) or "PreToolUse" not in doc["hooks"]:
        raise Halt(f"hook settings {path} carries no PreToolUse hook", "hook-settings")


def run_gate_child(cfg: dict, gate: str, prompt_text: str, allowed_tools: str,
                   budget_usd: float, unit: str, outdir: Path,
                   rlog: RunLog, deadman, add_dirs: list[str],
                   child_home: Path | None = None,
                   priv_runtime: Path | None = None) -> dict:
    """Launch one gate in a fresh, sessionless, kernel-contained, default-deny context."""
    lim = cfg["limits"]
    cmd = [
        "systemd-run", "--user", "--scope", "--quiet", f"--unit={unit}",
        "-p", f"MemoryMax={lim['memory_max']}",
        # MEASURED, raw/11: MemoryMax ALONE DOES NOT CAP MEMORY ON THIS BOX. memory.max is
        # applied correctly, but memory.swap.max defaults to `max`, so a 1 GiB allocation under a
        # 256M cap was paid out of the 8 GiB swap file and exited 0 in one second. With
        # MemorySwapMax=0 the same allocation is OOM-killed (rc=137) immediately. A memory cap
        # that a runaway can buy its way out of with swap is not a cap.
        "-p", f"MemorySwapMax={lim.get('memory_swap_max', '0')}",
        "-p", f"RuntimeMaxSec={lim['runtime_max_sec']}",
    ]
    # STEERING BREAKER, measured (GATE-RUNNER-HARDEN raw/06). The child's addressable
    # cross-session socket is created at $XDG_RUNTIME_DIR/cc-socks/<pid>.sock. Pointing that at a
    # per-gate private directory moves the socket OUT of the shared /run/user/<uid>/cc-socks,
    # where any other local session could reach it. This override must sit HERE — after the
    # scope, before the binary — because `systemd-run --user` itself needs the real runtime dir.
    if priv_runtime is not None:
        cmd += ["/usr/bin/env", f"XDG_RUNTIME_DIR={priv_runtime}"]
    cmd += [
        cfg["claude_bin"], "-p", prompt_text,
        "--setting-sources", "",
        "--settings", str(cfg["hook_settings"]),
        "--permission-mode", cfg["permission_mode"],
        "--allowedTools", allowed_tools,
        "--output-format", "json",
        "--max-budget-usd", str(budget_usd),
    ]
    # MEASURED, raw/14: under `dontAsk`, a Bash command whose target lies OUTSIDE the session's
    # working directory is DENIED even when --allowedTools explicitly permits that command. The
    # PreToolUse hook is not involved — the 2x2 matrix isolates it to the workspace boundary. A
    # gate therefore cannot write its own bundle into the courier without the courier being named
    # here. This WIDENS the surface, so it is explicit, minimal, and recorded per gate.
    for d in add_dirs:
        cmd += ["--add-dir", d]
    if cfg.get("model"):
        cmd += ["--model", str(cfg["model"])]
    # Redact only the prompt body, and find it by position relative to the claude binary —
    # systemd-run has its own `-p` flags before it, so cmd.index("-p") is the wrong one.
    _pi = cmd.index(cfg["claude_bin"]) + 2
    (outdir / "child-cmd.txt").write_text(
        "\n".join(cmd[:_pi] + ["<prompt text: see prompt.md>"] + cmd[_pi + 1:]) + "\n")

    env = build_child_env(cfg, child_home)
    started = time.monotonic()
    with (outdir / "child.stdout.json").open("wb") as so, \
         (outdir / "child.stderr.txt").open("wb") as se, \
         open(os.devnull, "rb") as devnull:
        proc = subprocess.Popen(cmd, stdout=so, stderr=se, stdin=devnull, env=env,
                                cwd=cfg["gate_cwd"], start_new_session=True)
        deadman.attach(unit, proc)
        rc = proc.wait()
        deadman.detach()
    wall = time.monotonic() - started

    raw = (outdir / "child.stdout.json").read_text(errors="replace")
    result = None
    try:
        result = json.loads(raw)
    except Exception:
        pass
    rlog.log(kind="child-done", gate=gate, rc=rc, wall_sec=round(wall, 1),
             json_parsed=result is not None,
             is_error=(result or {}).get("is_error"),
             terminal_reason=(result or {}).get("terminal_reason"),
             subtype=(result or {}).get("subtype"),
             api_error_status=(result or {}).get("api_error_status"),
             cost_usd=(result or {}).get("total_cost_usd"),
             denials=len((result or {}).get("permission_denials") or []))
    return {"rc": rc, "wall_sec": wall, "json": result, "raw_len": len(raw)}


class DeadMan:
    """If the runner stops making progress for T, kill the current scope and halt.

    RuntimeMaxSec already bounds a hung CHILD. This bounds a hung RUNNER — a git operation that
    never returns, a wedged post-condition check — which the kernel timeout does not cover.
    """

    def __init__(self, timeout_sec: int, rlog: RunLog):
        self.timeout = int(timeout_sec)
        self.rlog = rlog
        self.last = time.monotonic()
        self.unit = None
        self.proc = None
        self.tripped = None
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._watch, daemon=True)
        self._t.start()

    def progress(self) -> None:
        self.last = time.monotonic()

    def attach(self, unit: str, proc) -> None:
        self.unit, self.proc = unit, proc

    def detach(self) -> None:
        self.unit, self.proc = None, None

    def _watch(self) -> None:
        while not self._stop.wait(15):
            idle = time.monotonic() - self.last
            if idle > self.timeout and self.tripped is None:
                self.tripped = f"no progress for {int(idle)}s (> {self.timeout}s)"
                self.rlog.log(kind="deadman-trip", idle_sec=int(idle))
                if self.unit:
                    subprocess.run(["systemctl", "--user", "stop", self.unit],
                                   capture_output=True, check=False)
                if self.proc and self.proc.poll() is None:
                    self.proc.kill()

    def shutdown(self) -> None:
        self._stop.set()


# --------------------------------------------------------------------------- verdict


def classify(child: dict) -> tuple[str, str]:
    """Classify the CHILD RUN. This is not the gate verdict — it is the run's disposition.

    raw/06: the exit integer is not a classifier (every denial exited 0).
    raw/08: `subtype` is not a classifier either (it read 'success' on a hard failure).
    Only is_error / terminal_reason / api_error_status are load-bearing here.
    """
    j = child["json"]
    if j is None:
        # MEASURED kill signatures, raw/10 + raw/11: RuntimeMaxSec kills with rc=143 (SIGTERM),
        # a MemoryMax+MemorySwapMax OOM kills with rc=137 (SIGKILL). Either way the child never
        # finishes its result JSON, and no-parseable-JSON is the reliable discriminator — the
        # same doctrine as the project's own result envelope (CLAUDE.md, docs/03 S10.7).
        # MEASURED DEFECT, GATE-RUNNER-HARDEN raw/10: GATE-RUNNER recorded these kills as
        # rc=143 / rc=137, which is the SHELL's 128+signal convention. The runner does not go
        # through a shell — `subprocess.Popen.wait()` returns the NEGATED signal number, so a
        # RuntimeMaxSec kill arrives here as -15 and an OOM kill as -9. The old map missed both
        # and printed "unknown signal" for the two signatures it exists to name. The
        # classification was never wrong (no-parseable-JSON is the discriminator, exactly as in
        # docs/03 §10.7), but the detail line was, in the one place an operator would read it.
        sig = {143: "SIGTERM — RuntimeMaxSec deadline", -15: "SIGTERM — RuntimeMaxSec deadline",
               137: "SIGKILL — MemoryMax/MemorySwapMax OOM",
               -9: "SIGKILL — MemoryMax/MemorySwapMax OOM"}.get(child["rc"], "unknown signal")
        return "SUBSTRATE", (f"child produced no parseable result JSON "
                             f"(rc={child['rc']}: {sig}, {child['raw_len']} bytes captured)")
    if j.get("terminal_reason") == "budget_exhausted" or j.get("subtype") == "error_max_budget_usd":
        return "BUDGET", "the gate hit its --max-budget-usd cap"
    st = j.get("api_error_status")
    if st in RETRYABLE_HTTP:
        return "RETRYABLE", f"API {st}"
    if j.get("is_error"):
        return "ERROR", f"is_error=true terminal_reason={j.get('terminal_reason')!r}"
    return "COMPLETED", f"terminal_reason={j.get('terminal_reason')!r}"


def verify_gate_postconditions(cfg: dict, gate: str, rlog: RunLog) -> tuple[bool, list[str]]:
    """The gate verdict is MECHANICAL. The child's own account of itself is evidence, not proof.

    PASS requires all of: the QUEUE row moved to BUNDLED, bundles/<gate>/ exists and is
    non-empty, and its SHA256SUMS verifies.
    """
    courier = Path(cfg["courier_dir"])
    fails = []
    rows = {r["gate"]: r for r in parse_queue(courier / cfg.get("queue_file", "QUEUE.md"))}
    row = rows.get(gate)
    if not row or row["status"] != "BUNDLED":
        fails.append(f"QUEUE row for {gate} is {row['status'] if row else 'MISSING'!r}, not BUNDLED")
    bdir = courier / cfg.get("bundles_subdir", "bundles") / gate
    if not bdir.is_dir():
        fails.append(f"{bdir} does not exist")
    else:
        files = [p for p in bdir.rglob("*") if p.is_file()]
        if not files:
            fails.append(f"{bdir} is empty")
        sums = bdir / "SHA256SUMS"
        if not sums.is_file():
            fails.append(f"{sums} is missing")
        else:
            r = subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=bdir,
                               capture_output=True, text=True, check=False)
            if r.returncode != 0:
                fails.append(f"sha256sum -c SHA256SUMS failed: {r.stdout.strip()[-400:]}")
            rlog.log(kind="manifest-verify", gate=gate, rc=r.returncode,
                     out=r.stdout.strip()[-2000:])
    return (not fails), fails


# --------------------------------------------------------------------------- course check


def course_check(cfg: dict, summary: str, outdir: Path, rlog: RunLog) -> tuple[bool, str]:
    """Halt-only cloud course-correction. Returns (continue_ok, detail).

    ONE-WAY SAFETY VALVE, NEVER AN AUTHORITY. `OK` is not approval to proceed; it only means
    "no alarm". Forward progress is already gated by the APPROVED state the advisor and operator
    set at the daily ferry. ANYTHING that is not exactly `OK` — HALT, an unparseable answer, an
    empty answer, a transport error, an exhausted budget — stops the runner.
    """
    cc = cfg["course_check"]
    if not cc.get("enabled"):
        return True, "disabled"
    cmd = list(cc["command"])
    (outdir / "course-check-summary.txt").write_text(summary)
    try:
        r = subprocess.run(cmd, input=summary, capture_output=True, text=True,
                           timeout=int(cc.get("timeout_sec", 120)), check=False,
                           env=build_child_env(cfg))
    except Exception as e:
        return False, f"course-check transport error: {e}"
    (outdir / "course-check-stdout.txt").write_text(r.stdout)
    (outdir / "course-check-stderr.txt").write_text(r.stderr)
    token = r.stdout.strip()
    rlog.log(kind="course-check", rc=r.returncode, token=token[:64])
    if r.returncode != 0:
        return False, f"course-check exited {r.returncode}: {r.stderr.strip()[-300:]}"
    if token != "OK":
        return False, f"course-check returned {token[:200]!r} (only an exact 'OK' continues)"
    return True, "OK"


# --------------------------------------------------------------------------- STATUS


def push_status(cfg: dict, rlog: RunLog, *, gate: str, state: str, last: str, nxt: str) -> None:
    courier = Path(cfg["courier_dir"])
    (courier / cfg.get("status_file", "STATUS.md")).write_text(
        "# STATUS — forge-mini executor heartbeat\n"
        f"updated:  {utcnow()}\n"
        f"gate:     {gate}\n"
        f"state:    {state}\n"
        f"last:     {last}\n"
        f"next:     {nxt}\n"
        "usage:    n/a (wrought-runner)\n")
    try:
        git_push(courier, cfg, rlog, f"courier: status — wrought-runner {gate} {state}")
    except Halt:
        raise
    except Exception as e:
        rlog.log(kind="status-push-error", err=str(e))


# --------------------------------------------------------------------------- breaker


def breaker_path(cfg: dict) -> Path:
    return Path(cfg["state_dir"]) / "breaker.json"


def read_breaker(cfg: dict) -> dict:
    p = breaker_path(cfg)
    if not p.is_file():
        return {"halted": False, "consecutive_failures": 0, "reason": None, "at": None}
    return json.loads(p.read_text())


def write_breaker(cfg: dict, st: dict) -> None:
    p = breaker_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=2, sort_keys=True) + "\n")


def ledger_path(cfg: dict) -> Path:
    return Path(cfg["state_dir"]) / "ran.json"


def read_ledger(cfg: dict) -> dict:
    p = ledger_path(cfg)
    return json.loads(p.read_text()) if p.is_file() else {}


def write_ledger(cfg: dict, led: dict) -> None:
    p = ledger_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(led, indent=2, sort_keys=True) + "\n")


# --------------------------------------------------------------------------- one gate


def run_one_gate(cfg: dict, row: dict, rlog: RunLog, deadman: DeadMan, run_dir: Path) -> str:
    """Own the gate's ephemeral HOME and its post-gate orphan sweep, around the core run.

    Both duties are in a wrapper, not inline in the core, for one reason: THEY MUST RUN FOR A
    GATE THAT DIED, not only for one that finished. "A killed/dead gate must strand none"
    includes a gate that raised a Halt half way through, and a sweep on the happy path only
    would have missed exactly the case that produced this requirement — GATE-J0B-SURFACE, which
    stopped mid-Phase-4 and left a guest running for seven days with the inference API key held
    in a proxy's memory (docs/PHASE-J-STATE, "NEW SAFETY FINDING").
    """
    gate = row["gate"]
    home, runtime = make_ephemeral_home(cfg, gate, rlog)
    sweep_on = cfg.get("reaper", {}).get("enabled", True)
    before = residue_snapshot(cfg) if sweep_on else None
    if before is not None:
        (run_dir / gate).mkdir(parents=True, exist_ok=True)
        (run_dir / gate / "residue-before.json").write_text(
            json.dumps(before, indent=2, sort_keys=True) + "\n")

    pending: Halt | None = None
    verdict = "FAIL"
    try:
        verdict = _run_one_gate_core(cfg, row, rlog, deadman, run_dir, home, runtime)
    except Halt as h:
        pending = h
    finally:
        teardown_ephemeral_home(home, rlog, gate)

    if before is None:
        rlog.say(f"{gate}: orphan sweep DISABLED by config — residue is NOT being checked")
        if pending:
            raise pending
        return verdict

    after = residue_snapshot(cfg)
    new = residue_diff(before, after)
    (run_dir / gate / "residue-after.json").write_text(
        json.dumps({"after": after, "new": new}, indent=2, sort_keys=True) + "\n")
    if not new["any"]:
        rlog.say(f"{gate}: orphan sweep CLEAN — no new guest, domain or listener survived")
        if pending:
            raise pending
        return verdict

    killed = reap(cfg, new, rlog, gate)
    detail = (f"new qemu pids {sorted(new['qemu'])}; new domains {new['domains']}; "
              f"new listeners {sorted(new['listeners'])}")
    reason = (f"{gate} LEFT RESIDUE and was reaped — {detail}. Terminated: {killed}")
    if pending:
        # Do not let either halt hide the other: the residue is the new fault, and the reason
        # the gate died is very often why it leaked in the first place.
        reason += (f" | the gate had ALSO already halted: [{pending.breaker}] {pending.reason}")
    raise Halt(reason, "gate-residue")


def _run_one_gate_core(cfg: dict, row: dict, rlog: RunLog, deadman: DeadMan, run_dir: Path,
                       child_home: Path | None, priv_runtime: Path | None) -> str:
    """Run a single approved gate end to end. Returns 'PASS' or 'FAIL'. Raises Halt to stop."""
    gate = row["gate"]
    courier = Path(cfg["courier_dir"])
    queue = courier / cfg.get("queue_file", "QUEUE.md")
    outdir = run_dir / gate
    outdir.mkdir(parents=True, exist_ok=True)
    deadman.progress()

    # ---- pre-flight. Every failure here is LOUD; none is papered over with a default.
    if row["status"] in ("RUNNING", "BUNDLED"):
        raise Halt(f"{gate} is already {row['status']} — a stale or concurrent row. "
                   f"(GATE-J0B-SURFACE was left RUNNING with no bundle on 2026-08-20; that is "
                   f"exactly the state this refuses to run over.)", "stale-row")

    prompt = courier / cfg.get("prompts_subdir", "prompts") / f"{gate}.md"
    if not prompt.is_file():
        cands = sorted((courier / cfg.get("prompts_subdir", "prompts")).glob(f"{gate}-v*.md"))
        if len(cands) != 1:
            raise Halt(f"{gate}: expected exactly one prompt file "
                       f"({prompt.name} or a single {gate}-v*.md); found {len(cands)}",
                       "prompt-missing")
        prompt = cands[0]
    text = prompt.read_text()
    shutil.copyfile(prompt, outdir / "prompt.md")

    m = ALLOWED_TOOLS_RE.search(text)
    if not m:
        msg = (f"{gate}: prompt {prompt.name} declares no `ALLOWED-TOOLS:` header. A gate that "
               f"does not declare its own tool surface will NOT be given a default one.")
        if cfg["breakers"].get("missing_allowed_tools", "halt") == "halt":
            raise Halt(msg, "no-allowed-tools")
        rlog.say("SKIP — " + msg)
        return "SKIP"
    allowed_tools = m.group("tools").strip()
    budget = float(MAX_BUDGET_RE.search(text).group("usd")) if MAX_BUDGET_RE.search(text) \
        else float(cfg["limits"]["max_budget_usd_per_gate"])

    add_dirs = list(cfg.get("add_dirs") or [])
    m_dirs = ADD_DIRS_RE.search(text)
    if m_dirs:
        add_dirs += [d for d in m_dirs.group("dirs").split() if d]
    add_dirs = sorted(set(add_dirs))

    validate_hook_settings(Path(cfg["hook_settings"]))

    # ---- byte-freeze baseline (EXECUTOR-RAILS S2)
    before = hash_paths(cfg["freeze_paths"])
    (outdir / "freeze-before.json").write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")

    # ---- auto-memory fence baseline (raw/05)
    mem_dir = Path(cfg["memory_dir"]) if cfg.get("memory_dir") else None
    mem_before = memory_snapshot(mem_dir, outdir / "memory-before") if mem_dir else {}

    rlog.say(f"{gate}: launching. tools={allowed_tools!r} add_dirs={add_dirs} budget=${budget} "
             f"mode={cfg['permission_mode']} MemoryMax={cfg['limits']['memory_max']} "
             f"RuntimeMaxSec={cfg['limits']['runtime_max_sec']}")
    set_queue_status(queue, gate, "RUNNING", note_append="_(wrought-runner)_")
    git_push(courier, cfg, rlog, f"courier: wrought-runner starting {gate}")
    deadman.progress()

    # ---- the child, with bounded retry on retryable API status only
    unit = f"wrought-gate-{gate.lower()}-{int(time.time())}.scope"
    attempts = int(cfg["pacing"]["api_retry_max"])
    for attempt in range(1, attempts + 2):
        child = run_gate_child(cfg, gate, text, allowed_tools, budget,
                               f"{unit[:-6]}-{attempt}.scope", outdir, rlog, deadman, add_dirs,
                               child_home=child_home, priv_runtime=priv_runtime)
        deadman.progress()
        disposition, detail = classify(child)
        if disposition != "RETRYABLE":
            break
        if attempt > attempts:
            raise Halt(f"{gate}: {detail} persisted across {attempts} retries", "api-backoff")
        wait = min(int(cfg["pacing"]["api_backoff_base_sec"]) * (2 ** (attempt - 1)),
                   int(cfg["pacing"]["api_backoff_cap_sec"]))
        rlog.say(f"{gate}: {detail} — backing off {wait}s (attempt {attempt}/{attempts})")
        time.sleep(wait)
        deadman.progress()

    if deadman.tripped:
        raise Halt(f"dead-man: {deadman.tripped}", "deadman")

    # ---- byte-freeze re-assert. ANY change halts the whole runner.
    after = hash_paths(cfg["freeze_paths"])
    (outdir / "freeze-after.json").write_text(json.dumps(after, indent=2, sort_keys=True) + "\n")
    drift = freeze_diff(before, after)
    (outdir / "freeze-verdict.txt").write_text(
        ("HOLD — no change to any frozen path\n" if not drift
         else "TRIPWIRE — frozen paths changed:\n" + "\n".join(drift) + "\n"))
    if drift:
        raise Halt(f"{gate}: BYTE-FREEZE TRIPWIRE — {'; '.join(drift)}", "byte-freeze")

    # ---- auto-memory fence: fail SOFT. Preserve the delta, restore the baseline, record it.
    mem_note = "unchanged"
    if mem_dir:
        mem_after = memory_snapshot(mem_dir, outdir / "memory-after")
        if mem_after != mem_before:
            memory_restore(mem_dir, outdir / "memory-before")
            mem_note = (f"CHANGED — the gate wrote auto-memory. The delta is preserved at "
                        f"{outdir / 'memory-after'} and the pre-gate state was restored, so the "
                        f"next gate still starts from a clean context.")
            rlog.say(f"{gate}: auto-memory {mem_note}")

    # ---- the gate verdict, mechanically
    ok, fails = verify_gate_postconditions(cfg, gate, rlog)
    verdict = "PASS" if (ok and disposition == "COMPLETED") else "FAIL"
    rlog.log(kind="gate-verdict", gate=gate, verdict=verdict, disposition=disposition,
             detail=detail, postcondition_failures=fails, memory=mem_note,
             cost_usd=(child["json"] or {}).get("total_cost_usd"))
    (outdir / "verdict.json").write_text(json.dumps(
        {"gate": gate, "verdict": verdict, "child_disposition": disposition, "detail": detail,
         "postcondition_failures": fails, "memory_fence": mem_note,
         "wall_sec": round(child["wall_sec"], 1), "rc": child["rc"],
         "cost_usd": (child["json"] or {}).get("total_cost_usd")},
        indent=2, sort_keys=True) + "\n")
    if verdict == "FAIL":
        rlog.say(f"{gate}: FAIL — child={disposition} ({detail}); postconditions: {fails}")
        set_queue_status(queue, gate, "HALTED",
                         note_append=f"_(wrought-runner: {disposition}; {'; '.join(fails)[:200]})_")
        git_push(courier, cfg, rlog, f"courier: wrought-runner {gate} FAILED")
    else:
        rlog.say(f"{gate}: PASS — bundle present, manifest verifies, byte freeze held")
    return verdict


# --------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--reset-breaker", action="store_true",
                    help="operator action: clear a halted breaker and exit")
    ap.add_argument("--status", action="store_true", help="print breaker + ledger and exit")
    ap.add_argument("--max-gates", type=int, default=None, help="override the per-run gate cap")
    args = ap.parse_args()

    cfg = load_config(args.config)
    state = Path(cfg["state_dir"])
    state.mkdir(parents=True, exist_ok=True)

    if args.status:
        print(json.dumps({"breaker": read_breaker(cfg), "ledger": read_ledger(cfg)}, indent=2))
        return 0
    if args.reset_breaker:
        write_breaker(cfg, {"halted": False, "consecutive_failures": 0,
                            "reason": None, "at": utcnow(),
                            "reset_by": "operator via --reset-breaker"})
        print("breaker reset")
        return 0

    lock = (state / "runner.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit("wrought-runner: another instance holds the lock; refusing to start")

    started = utcnow()
    rlog = RunLog(state, started)
    run_dir = rlog.dir
    bk = read_breaker(cfg)
    if bk.get("halted"):
        rlog.say(f"BREAKER IS LATCHED ({bk.get('reason')!r} at {bk.get('at')}). "
                 f"Operator must run --reset-breaker.")
        return 3

    deadman = DeadMan(int(cfg["breakers"]["deadman_no_progress_sec"]), rlog)
    t0 = time.monotonic()
    ran = 0
    halt_reason = None
    breaker_name = None
    courier = Path(cfg["courier_dir"])
    queue = courier / cfg.get("queue_file", "QUEUE.md")
    max_gates = args.max_gates if args.max_gates is not None else int(cfg["breakers"]["max_gates_per_run"])

    try:
        while True:
            deadman.progress()
            git_pull(courier, cfg, rlog)
            rows = parse_queue(queue)
            led = read_ledger(cfg)
            todo = [r for r in rows if r["status"] == RUNNABLE_STATUS and r["gate"] not in led]
            if not todo:
                rlog.say("no APPROVED gates left to run — exiting cleanly")
                break
            if ran >= max_gates:
                raise Halt(f"per-run gate cap reached ({ran}/{max_gates}); "
                           f"waiting for the next daily ferry", "gate-cap")
            elapsed = time.monotonic() - t0
            if elapsed > int(cfg["breakers"]["max_wall_clock_sec"]):
                raise Halt(f"wall-clock budget exhausted ({int(elapsed)}s > "
                           f"{cfg['breakers']['max_wall_clock_sec']}s)", "wall-clock")

            row = todo[0]
            gate = row["gate"]
            push_status(cfg, rlog, gate=gate, state="RUNNING P-gate",
                        last=f"wrought-runner started {gate} ({ran + 1}/{max_gates} this run)",
                        nxt="gate execution, then byte-freeze re-assert and manifest verify")
            verdict = run_one_gate(cfg, row, rlog, deadman, run_dir)
            ran += 1

            led[gate] = {"verdict": verdict, "at": utcnow(), "run": run_dir.name}
            write_ledger(cfg, led)

            bk = read_breaker(cfg)
            bk["consecutive_failures"] = 0 if verdict == "PASS" else bk.get("consecutive_failures", 0) + 1
            write_breaker(cfg, bk)
            if bk["consecutive_failures"] >= int(cfg["breakers"]["max_consecutive_failures"]):
                raise Halt(f"{bk['consecutive_failures']} consecutive non-PASS gates "
                           f"(cap {cfg['breakers']['max_consecutive_failures']})",
                           "consecutive-failures")

            # ---- halt-only cloud course-correction, between gates
            rows_now = {r["gate"]: r for r in parse_queue(queue)}
            nxt_gate = next((r["gate"] for r in parse_queue(queue)
                             if r["status"] == RUNNABLE_STATUS and r["gate"] not in led), "(none)")
            summary = (f"gate={gate}\nverdict={verdict}\n"
                       f"queue_status={rows_now.get(gate, {}).get('status')}\n"
                       f"byte_freeze={(run_dir / gate / 'freeze-verdict.txt').read_text().splitlines()[0]}\n"
                       f"next_queued={nxt_gate}\n"
                       f"gates_this_run={ran}/{max_gates}\n")
            cont, detail = course_check(cfg, summary, run_dir / gate, rlog)
            if not cont:
                raise Halt(f"course-check said stop: {detail}", "course-check")

            push_status(cfg, rlog, gate=gate, state="RUNNING P-paced",
                        last=f"{gate} -> {verdict}; course-check {detail}",
                        nxt=f"pacing sleep, then {nxt_gate}")
            nap = int(cfg["pacing"]["inter_gate_sleep_sec"])
            rlog.say(f"pacing: sleeping {nap}s before the next gate")
            slept = 0
            while slept < nap:
                time.sleep(min(30, nap - slept))
                slept += min(30, nap - slept)
                deadman.progress()

    except Halt as h:
        halt_reason, breaker_name = h.reason, h.breaker
        rlog.say(f"HALT [{breaker_name}]: {halt_reason}")
    except KeyboardInterrupt:
        halt_reason, breaker_name = "interrupted by operator", "sigint"
        rlog.say("HALT [sigint]: interrupted by operator")
    finally:
        deadman.shutdown()

    bk = read_breaker(cfg)
    latched = bool(halt_reason) and breaker_name not in NON_LATCHING
    if halt_reason:
        bk.update({"halted": latched, "reason": f"[{breaker_name}] {halt_reason}",
                   "at": utcnow(), "latched": latched})
    write_breaker(cfg, bk)
    rlog.log(kind="run-end", gates_run=ran, halted=bool(halt_reason),
             reason=halt_reason, breaker=breaker_name,
             wall_sec=round(time.monotonic() - t0, 1))
    try:
        push_status(cfg, rlog,
                    gate="NONE" if not halt_reason else "GATE-BATCH",
                    state="HALTED" if latched else "IDLE",
                    last=(f"wrought-runner stopped after {ran} gate(s): [{breaker_name}] {halt_reason}"
                          if halt_reason else
                          f"wrought-runner finished cleanly after {ran} gate(s)"),
                    nxt="operator review at the next daily ferry"
                        + (" — breaker is LATCHED, needs --reset-breaker" if latched else ""))
    except Exception as e:
        rlog.log(kind="final-status-push-error", err=str(e))
    if halt_reason:
        print(f"\nwrought-runner: {ran} gate(s); STOPPED [{breaker_name}] {halt_reason}"
              f"{'  — BREAKER LATCHED, operator must --reset-breaker' if latched else ''}")
    else:
        print(f"\nwrought-runner: {ran} gate(s); clean exit")
    print(f"evidence: {run_dir}")
    # 0 clean, 4 batch bounded by its own cap (normal), 2 a real breaker (latched).
    return 0 if not halt_reason else (4 if not latched else 2)


if __name__ == "__main__":
    sys.exit(main())
