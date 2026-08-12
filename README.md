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

## The two hard rules

**1. Transport.** Prompts travel as **files**, and every load-bearing literal — commands, paths,
versions, hashes — lives in an **indented block**. Prose can be paraphrased in transit; an
indented block cannot. A prompt whose blocks arrive empty or garbled is not run: the box stops
and tells the operator.

**2. Nothing but text.** No secret, key, image, overlay, or `.zip` is ever committed here.
Bundles are pushed unzipped precisely so the contents are reviewable as text. The push
credential lives outside every git work tree and is listed in `.gitignore` as a second line of
defence. This repo is public — treat every commit as permanent and world-readable.
