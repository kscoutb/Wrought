# Wrought courier

The transport between the off-box advisor and the build box (`forge-mini`). This repo is
**public** and carries **text only**: the prompts that were dispatched, and the review bundles
that came back. It is not the Wrought source tree — the foundry repo never leaves the box.

## The loop

1. **Operator hands the box a prompt file.** Prompts are authored off-box by the advisor and
   delivered to the box as a file.
2. **Box archives and runs it.** The box copies the prompt verbatim to
   `prompts/<GATE-NAME>-vN.md`, sets that gate to `RUNNING` in `QUEUE.md`, and runs it in a
   **fresh context**.
3. **Box pushes the bundle.** The gate's review bundle goes to `bundles/<GATE-NAME>/`
   **unzipped** — the report `.md`, `raw/` files, proposals, and `SHA256SUMS`. The box sets
   `BUNDLED` in `QUEUE.md` and `git push`es.
4. **Advisor adjudicates.** The advisor pulls (read-only, unauthenticated — the repo is public),
   sets `ADJUDICATED`, and writes the next prompt. Back to (1).

## Layout

| Path | Direction | Contents |
|---|---|---|
| `prompts/` | advisor → box | Each dispatched prompt, verbatim, as `<GATE-NAME>-vN.md`. The archive of exactly what was sent. |
| `bundles/` | box → advisor | One directory per gate, unzipped: report `.md`, `raw/`, proposals, `SHA256SUMS`. |
| `QUEUE.md` | both | Live dispatch state. Box sets `RUNNING`/`BUNDLED`; advisor sets `ADJUDICATED` and queues the next gate. |

## The hard rules

**1. Transport.** Prompts travel as **files**, and every load-bearing literal — commands, paths,
versions, hashes — lives in an **indented block**. Prose can be paraphrased in transit; an
indented block cannot. A prompt whose blocks arrive empty or garbled is not run: the box stops
and tells the operator.

**2. Heartbeat.** The box keeps `STATUS.md` at this repo's root current — refreshed, committed and
**pushed** on reading a prompt (`RECEIVED`), after the transport check, at every phase boundary, on
any halt, at wind-down, and at the end of **every** operator turn. It is one overwritten file, not
a log. A push is cheap; advisor blindness is not. Canonical rule: `docs/EXECUTOR-RAILS.md` §9.

**3. Adjudications are carried in.** The advisor cannot push here, so a verdict arrives inside the
next prompt. When a prompt carries a `PRIOR-ADJUDICATION` block, the box records it verbatim to
`bundles/<prior-gate>/ADJUDICATION.md` and sets that gate's `QUEUE.md` row to `ADJUDICATED` as its
**first** courier action. Canonical rule: `docs/EXECUTOR-RAILS.md` §10.

**4. A gate runs only when APPROVED, and only if it declares its tools.** `QUEUED` means the prompt exists; `APPROVED` means the advisor and operator agreed at the ferry that it may run — the only status the batch runner starts. Every prompt declares an `ALLOWED-TOOLS:` header; one that does not is halted, not given a default. **Every `Bash` entry must be SCOPED (`Bash(cmd:*)`), never bare `Bash`** — the runner refuses a bare one — and every out-of-cwd tree the gate needs must be named in `ADD-DIRS:`. Canonical: `docs/EXECUTOR-RAILS.md` §12.

The full status vocabulary the runner's parser accepts. Only `APPROVED` is runnable; the rest are
waiting states or terminal side-exits:

| Status | Meaning | Set by |
|---|---|---|
| `QUEUED` | Prompt written and dispatched; the box has not started it. | advisor |
| `APPROVED` | Advisor **and** operator agreed at the ferry that this gate may run. **The only runnable status.** | advisor + operator |
| `RUNNING` | Prompt archived to `prompts/`; the gate is executing. | box / runner |
| `BUNDLED` | `bundles/<GATE-NAME>/` pushed; awaiting review. | box |
| `ADJUDICATED` | Advisor has reviewed the bundle; the gate is closed. | advisor |
| `RESET` | Started but produced no bundle. Partial evidence preserved, residue cleaned; must be re-dispatched fresh. Terminal. | box |
| `NOT RUN` | Dispatched, then deliberately **never started** — superseded, withdrawn, or overtaken before it ever ran. Unlike `QUEUED` it is a decision, not a waiting state; unlike `RESET` nothing executed. Terminal. | advisor + operator |
| `FOLDED INTO <gate>` | Never ran as its own session; its items were completed inside the named gate. Parametric — matched by prefix. Terminal. | box |
| `HALTED` | The runner stopped this gate on a breaker. Terminal until re-dispatched. | runner |

`NOT RUN` was **documented** on 2026-08-29 by `GATE-RUNNER-POLISH`, not introduced: it had been in
the runner's accept-set and in no document at all. It has **never appeared in a row** (`git log -S
'NOT RUN' -- QUEUE.md README.md` finds no such commit) and the runner never writes it, so the
meaning above is the minimal one the vocabulary needs and its **wording is flagged for the ferry**.

**5. Nothing a gate starts may outlive it.** The runner diffs {qemu processes, libvirt domains, listening sockets} across every gate and treats any new survivor as a latching fault — because `GATE-J0B-SURFACE` left a guest running for seven days with an API key in a proxy's memory. Canonical: `docs/EXECUTOR-RAILS.md` §13–14.

**6. Nothing but text.** No secret, key, image, overlay, or `.zip` is ever committed here.
Bundles are pushed unzipped precisely so the contents are reviewable as text. The push
credential lives outside every git work tree and is listed in `.gitignore` as a second line of
defence. This repo is public — treat every commit as permanent and world-readable.
