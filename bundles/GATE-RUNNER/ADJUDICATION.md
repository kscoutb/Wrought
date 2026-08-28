# ADJUDICATION — GATE-RUNNER

Recorded by `GATE-RUNNER-HARDEN` on 2026-08-28 per `docs/EXECUTOR-RAILS.md` §10.
Extracted **mechanically** (`sed -n '17,25p'`) from the dispatching prompt, archived verbatim
at `prompts/GATE-RUNNER-HARDEN-v1.0.md`. Not retyped.

## Verdict, verbatim

PRIOR-ADJUDICATION — GATE-RUNNER: **ACCEPTED as an attended build (advisor Fable, 2026-08-28).**
Runner correct; containment MEASURED not assumed (dontAsk + kernel scope + MemorySwapMax=0 + env
allowlist + a mechanical verdict that ignores the child's self-report); course-check is halt-only
on its own spend path and ships disabled. **NOT CLEARED for unattended use** — three conditions:
(1) close the steering breaker via a private $HOME per gate child; (2) add the reaper; (3) first
real use is a SUPERVISED batch that sets the provisional scale numbers. Operator ratifications:
APPROVED status YES, ALLOWED-TOOLS header YES, runner.conf structure/safety RATIFIED with scale
numbers PROVISIONAL, course-check credential HELD (stays disabled).


## Queue note

build accepted; unattended-blocked pending this gate + a supervised batch
