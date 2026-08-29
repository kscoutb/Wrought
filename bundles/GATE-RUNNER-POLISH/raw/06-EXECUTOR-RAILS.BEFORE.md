# EXECUTOR-RAILS — the invariant rails for any prompted session on this box

**Read this before running an advisor-authored prompt.** These rails do not change between gates,
so a prompt should say *"read `docs/EXECUTOR-RAILS.md`"* instead of restating them. A prompt may
**narrow** a rail for its session; nothing may widen one. Where a rule already has a home in this
repo, this file **points at it** — a rule copied into two places is a rule that drifts, and
reconciling the copies later costs more than the duplication ever saved.

## 1. Never touch

Never write to, and never delete anything under:

    /var/lib/wrought/state/**          /var/lib/wrought/jobs/**
    /etc/credstore.encrypted/**        /var/lib/wrought/oracle/**
    /var/lib/wrought/models/*.gguf     /var/lib/wrought/corpus/**
    /opt/wrought/venv*

**Hands off every `wrought-*` unit**: no `enable`, `start`, `stop`, `restart`, `daemon-reload`, no
unit-file edit. Reading is fine and expected — `is-active`, `show`, `status`, `cat`.

A session works in its own `/var/lib/wrought/<gate>/` workdir with a `raw/` beneath it. That
directory is the only place it creates state without being told to.

## 2. Byte freeze on the orchestrator store

At session start and again before finalizing, hash all three files and diff the two captures
mechanically — `raw/00` and `raw/99`:

    sha256sum /var/lib/wrought/state/orchestrator.db{,-wal,-shm}

**Any difference is STOP EVERYTHING**, not a line in the report. Production state is the one thing
a docs, recon, or audit session has no business moving, and the freeze is what makes "I did not
touch it" a measurement instead of a claim.

## 3. Deletes are enumerated, never globbed

Delete only paths written out one by one, each with its reason. No `rm -r` over a glob, no
"clean up the leftovers". If a delete's precondition cannot be checked — the target is absent, or
its hash does not match the one the prompt supplied — **report, do not delete.**

## 4. Evidence discipline

- **J-95: a measured value carries the exact command that produced it, or it is not evidence.**
  This is why `raw/` files start with the command that made them. Values whose commands were never
  committed have twice failed to reproduce (J-89, J-101); that is the rule's whole origin.
- **Never overwrite evidence** — prior-session or this-session. A new measurement gets a **new
  filename**. Correcting a number means adding the correction, not editing the record.
- **Commit as the gate closes** (ST-7, `docs/07`), and grep the diff for secret-shaped strings
  first. Uncommitted evidence is lost across sessions.
- Foundry commits are **operator-authored**: `git commit --author="Kalib <anthropic.spotlight807@passmail.net>"`.
  The box executes; the operator owns the history.

## 5. Secrets

`docs/06` §14.4 is canonical for what a secret *is* and how it is stored, and CLAUDE.md's hard rule
governs where one may appear. The **executor-facing** addition, which lives here because §14.4 does
not cover it: a secret reaches a command on **stdin only** — never in `argv` (world-readable in
`/proc`, and in shell history), never in an environment variable, never in a config file, and
**never inside a guest**. A disposable guest is an untrusted context by construction; anything
handed to it is disclosed.

**This binds the box's own tooling, including a secret *scan*.** `GATE-RECONCILE` proved the point
against itself: it verified a public bundle carried no key by doing `KEY=$(sudo cat …)` then
`grep -rlF "$KEY" …`, which expands the secret into `argv`. The finding was right and the method
was a §5 violation. The correct form passes the pattern on **stdin**:

    sudo cat /run/credentials/wrought-inference.service/inference-api-key | grep -rlFf - <tree>

Record: `bundles/RECONCILE/raw/20-secret-scan-method-defect.txt`.

## 6. Ultracode discipline

- **Subagents are read-only.** They search, read, and report; they do not edit, install, or
  configure.
- **State changes are serial, in the main thread.** Parallel writers to one box produce a history
  nobody can replay.
- **A short adversarial audit runs before any report ships** — proportionate to the session. Its
  job is to find the claim the report cannot support, and to say so in the report rather than
  leaving it for the reviewer.

## 7. Prompt transport

- Prompts arrive as **files**, not as pasted chat text.
- Every load-bearing literal — commands, paths, versions, hashes — lives in an **indented block**.
  Prose survives paraphrase in transit; an indented block does not survive markdown eating a `*`
  or a `\`.
- A prompt states its **block count**; the executor checks it before doing anything else.
- **A damaged prompt is a STOP.** Report it to the operator and wait. Never reconstruct the missing
  text — a reconstructed instruction is an invented one.

This rule exists because it was learned the hard way: the GATE-J0A v1.4 prompt arrived with its
abort-trigger regex mangled in transit (`docs`-side record: `build-evidence/j0a/ACCEPTANCE-2026-08-11.md` §4).

## 8. Courier

Prompts and bundles move through the public **Wrought courier** repo. Its protocol is canonical at
`/home/kalib/courier/Wrought/README.md` and is **not restated here** — read it there. Only the two
facts an executor needs to plan a session:

- the prompt is archived **verbatim** to `prompts/` and the gate set to `RUNNING` **before** work
  starts;
- the bundle is pushed **unzipped** to `bundles/<GATE-NAME>/` and the gate set to `BUNDLED`.

**The repo is public and carries text only.** No secret, key, image, overlay, or `.zip` — ever.

## 9. Heartbeat — `STATUS.md` is kept current, and pushed

The box keeps `STATUS.md` at the courier root current. It refreshes, commits, and **pushes** it at
every one of:

- **(a)** on first reading any prompt — state `RECEIVED`, *before* the transport verdict;
- **(b)** immediately after the transport check — `TRANSPORT-OK` / `TRANSPORT-FAIL`;
- **(c)** at each phase boundary — `RUNNING P<n>`;
- **(d)** on any STOP, abort, or question-to-operator — `HALTED`, with the reason in `last`;
- **(e)** at wind-down — `BUNDLED` or `IDLE`.

Additionally, the box ends **every operator turn** by refreshing and pushing `STATUS.md` — even a
turn that only answers a question or reports a halt. **A push is cheap; advisor blindness is not.**

`STATUS.md` is a single **overwritten** file, not a log. Its durable history lives in `bundles/`
and in the git history of `STATUS.md` itself. The schema is fixed:

    # STATUS — forge-mini executor heartbeat
    updated:  <UTC ISO-8601>
    gate:     <gate name, or NONE>
    state:    RECEIVED | TRANSPORT-OK | TRANSPORT-FAIL | RUNNING P<n> | HALTED | BUNDLED | IDLE
    last:     <one line: the last thing done>
    next:     <one line: the next expected step, or what is being waited on>
    usage:    <the session's /usage summary, or n/a>

This rule exists because `GATE-J0B-SURFACE` was dispatched and the advisor could not tell whether
it had started, stalled, or finished — and it had in fact stopped mid-Phase-4 and left a guest
running for seven days (`bundles/GATE-J0B/PARTIAL/WHAT-HAPPENED.md`).

## 10. Adjudications are carried in, and recorded on arrival

The advisor cannot push to the courier, so **adjudications arrive inside the next prompt**. When a
prompt carries a `PRIOR-ADJUDICATION` block, the box records it verbatim to
`bundles/<prior-gate>/ADJUDICATION.md` and sets that gate's `QUEUE.md` row to `ADJUDICATED` **as
its first courier action** — so the closed/open state of every gate is visible on the courier, not
only in the advisor's chat.

Extract the verdict **mechanically** (e.g. `sed -n` over the archived prompt), never by retyping:
"verbatim" that passes through a keyboard is a paraphrase waiting to happen.

If a prompt names a prior gate but supplies **no verdict text**, there is nothing to record —
say so in the QUEUE row and **invent nothing** (this happened once already: `GATE-RUNNER` named
`GATE-HJ2` with no verdict, and the box correctly recorded the absence).

## 11. Wind-down duty

Every session ends by doing all three, in this order:

1. **Update `docs/PHASE-J-STATE.md`** — the live rail position.
2. **Append a `BUILD-JOURNAL.md` entry.**
3. **Return the bundle through the courier.**

Step 1 is mandatory and is the reason this list exists. CLAUDE.md designates the journal as the
live rail position, and on the entire GATE-J0 campaign the journal was **silent** — so a prompt
author reconstructing prior state from the designated authority produced a premise the box
contradicted, and an entire session was spent refusing it (**J-156**). A state doc that is cheap to
read and mandatory to update is what stops that recurring.

## 12. A gate runs only when its row says `APPROVED`, and only if it declares its tools

Two rules the batch runner enforces mechanically. Both were **proposed** by `GATE-RUNNER` and
**ratified by the advisor and operator at the 2026-08-28 ferry**; they are written here because
`bin/wrought-runner` already refuses on them, and a control the code enforces but no doc states
is a control nobody can review.

**12.1 `APPROVED` is a QUEUE status, and it is the only runnable one.** The vocabulary is
`QUEUED → APPROVED → RUNNING → BUNDLED → ADJUDICATED`, with `RESET`, `FOLDED INTO <gate>` and
`HALTED` as terminal side-exits. `QUEUED` means the prompt exists; **`APPROVED` means the advisor
and the operator agreed at the daily ferry that this gate may actually run.** The runner walks the
queue and starts nothing else — `wrought-runner`'s `RUNNABLE_STATUS`. The gap between the two
statuses is deliberate: it is where a human still sits on the unattended path.

**12.2 Every gate prompt declares its minimal tool surface in an `ALLOWED-TOOLS:` header.**
A gate that does not declare one is **not given a default** — the runner halts on
`no-allowed-tools` (`breakers.missing_allowed_tools`). Optional companions: `MAX-BUDGET-USD:` and
`ADD-DIRS:`. Keep every one of them minimal; each entry widens the gate's surface, and
`ADD-DIRS` in particular is what lets a gate write outside its own cwd at all.

## 13. Nothing a gate starts may outlive it

`GATE-J0B-SURFACE` stopped mid-Phase-4 and left its guest running for **seven days**, with the
inference API key held in an authenticating proxy's memory the whole time. A dead gate reaps
nothing, so the reaping cannot be the gate's own last step. Two layers, and the second is the one
that is actually load-bearing.

**13.1 Launch reapable-by-scope, or own the teardown explicitly.** A process started as a
descendant of the gate's `systemd-run --scope` lives in the scope's cgroup and dies when the scope
does — **measured**: a plain background child was gone at the `RuntimeMaxSec` deadline with no
sweep needed (`build-evidence/runner-harden/raw/10`). A **`virsh` / `virt-install` domain does
NOT**: libvirtd is a separate daemon and the domain re-parents into its `machine.slice`, outside
the scope entirely. So a gate that needs a guest launches **plain `qemu-system` as a scope
descendant**, not via libvirtd. **A gate that does use libvirt owns its teardown explicitly** and
says so in its prompt — there is no scope that will do it for that gate.

**13.2 The runner sweeps after every gate, and residue is a latching fault.** `wrought-runner`
snapshots `{qemu-system processes, libvirt domains, listening sockets}` before the gate and diffs
after it. Any **new** survivor is enumerated, terminated, and the batch **HALTS with a latching
`gate-residue` fault** that only `--reset-breaker` clears. The sweep runs for a gate that **died**,
not only one that finished — it is in the wrapper's `finally`, because the seven-day guest came
from a gate that halted half way through. A gate that leaks a process is a defect, and it is
treated loud.

*(The domain probe is skipped unless `libvirtd` is already active: `virsh list` would otherwise
socket-activate the daemon, and a sweep that starts a daemon on every gate is the side effect the
sweep exists to prevent. Nothing is lost — a libvirt domain always has a `qemu-system` process,
and the PID scan sees it whoever its parent is.)*

## 14. A gate child is fenced from every other session on the box

Each gate runs under a **private ephemeral `$HOME`** and a **private `$XDG_RUNTIME_DIR`**, created
per gate and torn down with it (`ephemeral_home` in `/etc/wrought/runner.conf`). Both are needed,
because **there are two surfaces with two different keys** and closing one leaves the other open
(measured, `build-evidence/runner-harden/raw/06`):

- the **peer listing** — whether another local session can *see* the gate — is keyed on `$HOME`;
- the **addressable socket** — `$XDG_RUNTIME_DIR/cc-socks/<pid>.sock` — is keyed on the runtime dir.

A private HOME alone removes the child from the listing while **leaving its socket in the shared
directory, still addressable by path**. *Not listed* is not the same claim as *not addressable*,
and only both together close the steering breaker.

The private runtime dir must be applied to the `claude` process **only**, inside the scope
(`systemd-run --user --scope … /usr/bin/env XDG_RUNTIME_DIR=<private> claude -p …`): overriding it
for the whole invocation breaks the launcher, which needs the real user bus.

The ephemeral HOME is seeded with the **measured minimum** — `.claude/.credentials.json` for auth,
`.gitconfig` and `.git-credentials` for the gate's own courier push. It therefore **holds live
credential copies**: mode `0700`, rooted under the runner's `state_dir`, and removed with the gate.
It is never listed by contents in a bundle.

