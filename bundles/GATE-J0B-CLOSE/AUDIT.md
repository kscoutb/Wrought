# AUDIT — GATE-J0B-CLOSE, adversarial pass before shipping (rails §6)

Run against `REPORT-J0B-CLOSE.md` and the raw evidence, looking for the claim the report cannot
support. Counts: **17** evidence files this session (`raw/10`–`raw/51`, `raw/99`, `raw/99b`);
prior-gate evidence untouched (J0B `raw/00–42`, J0B-RESUME `raw/50–65`). **3** deviations, all mine,
all recorded. `SHA256SUMS` generated last.

---

## A. The headline is TRUE but NARROWER than the words "the surface manufactures"

**What is proven:** the real model, in an egress-locked disposable guest, called a filesystem tool
and produced a 5-byte file with exact content, and did it again three times concurrently.

**What is NOT proven, and the report's headline could be read as claiming it:** that this surface can
manufacture **software**. `FORGE.txt` is a one-token write. No compilation, no test run, no repair
loop, no oracle, no multi-file change, no task where the model could be *wrong* rather than merely
silent. **The capability demonstrated is "the agent can reach the model and act on the filesystem",
not "the agent can build things."** GATE-41's ten fixture tasks are where the second claim gets
tested, and they are an operator deliverable that does not exist yet.

## B. "F-5 is CLOSED" — closed against a mechanism that is NOT the one F-5 described

This is the most important honest qualification in the gate, and it cuts both ways.

- The report **does** measure that the guestfwd cannot carry concurrency (16→0 vs host 8→8), and it
  **does** measure a clean concurrent goose burst after the fix (12/12, 0 lost). Those stand.
- But **the original F-5 wedge was never reproduced in this gate.** No run here triggered goose's
  3× retry, and no retry storm was staged. The report says so in §8; the audit repeats it because
  the phrase "F-5 is closed" in the headline is doing more work than the evidence underneath it.
  **The accurate statement is: the transport that could not carry goose has been replaced, and the
  unbounded generation that made abandonment expensive has been bounded — and under the shape that
  previously wedged, nothing wedged.** That is strong. It is not the same as "the failure mode was
  reproduced and then fixed."

## C. The causal attribution for runs 1 and 2 is an INFERENCE, and the report should not be read as
having measured it directly

The chain is: (i) runs 1/2 over guestfwd produced no file; (ii) the server, streaming, goose's own
22-tool body and the model's willingness were each independently proven fine; (iii) the guestfwd
was measured unable to carry concurrency; (iv) changing **only** the transport produced a PASS.

That is a good A/B — one variable between run 2 and run 3 — but it is **between runs, not
simultaneous**, and runs 1/2 additionally shared an already-poisoned stream. **The exact frame at
which runs 1 and 2 gave up was never reconstructed**, because goose's `llm_request.*.jsonl` captured
only the title call and never the agent turn. So: mechanism measured, per-run post-mortem not.

## D. The rails §5 evidence is a PROXY, not the committed scan

`raw/32` shows the proxy's argv contains only a path and that **0 environment variables carry a
64-byte value** — the credential's exact length. That is a sound indirect test, and it is the right
one to run *live against a process*, since the direct form would put the key in `argv` (the §5.1
defect this repo has now committed three times). **But it is not the committed scan.**
`bin/wrought-precommit-secret-scan` is, and it was run over the staged diff and the bundle tree
before pushing; its exit code is read with all three meanings distinguished (0 clean / 1 secret
present / **2 = the scan could not run, which is NOT a pass**).

## E. The cost figure is dominated by an assumption the box could not source

Stated in the report, repeated here because a number in a report gets quoted without its caveat:
**$33.45 rests on cache multipliers (1.25× / 0.10×) that the reference this session actually read
does not carry.** At the full input rate the same tokens cost **$214.89 — 6.4×**. The **token counts
are exact and durable; the dollar figure is not.** Anyone re-calibrating a cap should price the
counts against a billing source, and should not carry this number across session shapes (§7).

## F. THE DEFECT THIS GATE FOUND IN ITS OWN WORK, and it is the same one three times

`pgrep -f` / `pkill -f` matching the **command line** rather than the executable killed a shell
**twice in this gate** (Phase 2 `raw/25`; Phase 5 `raw/50`), after `GATE-RUNNER-POLISH` had already
found and fixed exactly this class in the reaper one day earlier. Both were loud and cost nothing
but a retry. **The significant part is not the slips — it is that the fix was applied to the
reaper's code and never turned into a habit for ad-hoc commands, and that the very same file
(`raw/50`) contains a CORRECT `pgrep -x` three lines above the incorrect `pgrep -f`.** A rule that
lives only in one code path is a rule that keeps being re-learned at the console. **Recommend to the
ferry: state it as a rails line, not just as a fixed function.**

## G. Claims checked and found SOUND (the audit did not only find problems)

- `authproxy2.py` **is** unedited: `ea2974ce…d99e` re-hashed at `raw/30`, matching J0B-RESUME.
- The `max_tokens` value **is not** invented: `24000` is `pins.lock serving.reasoning_budget`, quoted
  with its committed derivation. The **key** is new, and is proposed rather than minted.
- Both truncated prompt hashes were matched against **full** `pins.lock` values, not the ellipsis.
- The byte-freeze verdict is taken by `diff` over extracted hash lines, not by eye.
- The Phase-2 stub result (goose executes `write`) is **corroborated by the Phase-4 run with the
  real model**, so the gate does not rest a capability claim on an instrument the box wrote.
- The extension-schema claim is taken from **goose's own output** twice over — `goose info -v`, and
  `config.yaml` as `goose configure` wrote it — never from a shape the box guessed.
- `wrought-inference.service` was never touched: same `ActiveEnterTimestamp` and `NRestarts=0` at
  Phase 1 and Phase 5.

## H. One number in the report worth pinning down before it is quoted

The §4.1 table cites the non-streaming tool-call control at **3.3 s**. That is arm A of the A/B in
`raw/43`. The **first** non-streaming measurement in the same file, taken minutes earlier on a
colder server, was **8.3 s**. Both are real; the table's figure is the one measured under the same
conditions as its comparators. Flagged so nobody reads 3.3 s as a cold-start latency.

## I. What the advisor should rule on

1. **P-3 is a correction to an ESTABLISHED FACT**, not just a new pin. `docs/PHASE-J-STATE.md` says
   *"The seam is QEMU user-mode networking"* and records the guestfwd pinhole as proven. It is proven
   **for a single sequential connection**, and the qualifier is not in the doc. This gate has written
   the correction **by addition** into that file; the ferry should confirm the wording.
2. **May the `ssh -R` transport be used by a RUNNER gate child?** Proven attended only. Whether the
   tunnel process survives inside the scope for a whole gate, and is reaped by §13, is **untested**.
3. **P-2:** may a key exist that carries a bound already ratified for escalation into the
   guest-agent path?
4. **B-1 and B-3 from the v1.0 pre-flight are STILL UN-RULED** and bind the next runner-run gate.
5. **F above** — make "match the executable, never the command line" a rails line.
6. **Transport: seventh miss in eight.** Prompts keep arriving as pasted text with no block count.
