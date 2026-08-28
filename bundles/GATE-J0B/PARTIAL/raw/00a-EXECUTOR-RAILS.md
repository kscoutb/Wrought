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

## 9. Wind-down duty

Every session ends by doing all three, in this order:

1. **Update `docs/PHASE-J-STATE.md`** — the live rail position.
2. **Append a `BUILD-JOURNAL.md` entry.**
3. **Return the bundle through the courier.**

Step 1 is mandatory and is the reason this list exists. CLAUDE.md designates the journal as the
live rail position, and on the entire GATE-J0 campaign the journal was **silent** — so a prompt
author reconstructing prior state from the designated authority produced a premise the box
contradicted, and an entire session was spent refusing it (**J-156**). A state doc that is cheap to
read and mandatory to update is what stops that recurring.
