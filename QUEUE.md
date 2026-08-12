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
| `GATE-HJ1-HYGIENE` | `RUNNING` | v1.1 archived to `prompts/GATE-HJ1-HYGIENE-v1.1.md`. Consolidation session: ratify J0A substrate pins, create `docs/EXECUTOR-RAILS.md` + `docs/PHASE-J-STATE.md`, integrate the courier. J0B is held until this closes. |

*(HJ1 is the first gate through the courier. It was dispatched to the operator as a file and
archived here verbatim before the box began work.)*
