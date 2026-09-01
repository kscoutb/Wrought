# src/wrought_orchestrator/fsm.py
Implements an explicit finite state machine using a hardcoded transition table that raises `UndefinedTransition` for any invalid `(state, event)` pair to enforce loud failures.
Key components include the `Transition` dataclass, the `TABLE` dictionary, and functions `next_state`, `guard_ok`, and `reachable_states`.
Direct dependencies are `__future__.annotations` and `dataclasses.dataclass`.
A primary risk is the decoupled guard logic in `guard_ok`, which must be manually enforced before state changes, combined with strict string matching for states and events that can trigger runtime failures if external emitters drift from the table.
