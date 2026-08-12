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

*(No gates dispatched yet. The courier was bootstrapped empty; the advisor queues the first
gate, HJ1.)*
