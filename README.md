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

**4. Nothing but text.** No secret, key, image, overlay, or `.zip` is ever committed here.
Bundles are pushed unzipped precisely so the contents are reviewable as text. The push
credential lives outside every git work tree and is listed in `.gitignore` as a second line of
defence. This repo is public — treat every commit as permanent and world-readable.
