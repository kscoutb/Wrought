# QUEUE — live dispatch state

One row per gate, newest at the bottom. See `README.md` for the loop.

**Statuses**

| Status | Meaning | Set by |
|---|---|---|
| `QUEUED` | Prompt written and dispatched to the operator; the box has not started it. | advisor |
| `RUNNING` | Box has archived the prompt to `prompts/` and is running it in a fresh context. | box |
| `BUNDLED` | Box has pushed `bundles/<GATE-NAME>/` and the gate is awaiting review. | box |
| `ADJUDICATED` | Advisor has reviewed the bundle; the gate is closed and the next one queued. | advisor |

**Dispatch**

| Gate | Status | Notes |
|---|---|---|
| `GATE-HJ1-HYGIENE` | `BUNDLED` | v1.1 archived to `prompts/GATE-HJ1-HYGIENE-v1.1.md`; bundle at `bundles/GATE-HJ1/` (16-entry `SHA256SUMS`, verifies 16/16, covers the whole directory bar itself). Pins ratified — the closure is pinned at **versions**, not just names. Byte freeze **held**. Two foundry commits, local (the foundry repo has no remote): `624f1b9`, `bc27359`. **Surfaced, not answered: the running kernel is `7.0.0-29-generic` against a pinned `7.0.0-28-generic`, so ST-1 now has two unsatisfied triggers.** J0B unblocks on adjudication. |

*(HJ1 is the first gate through the courier. It was dispatched to the operator as a file and
archived here verbatim before the box began work.)*
