# bin/test-f8-signal-teardown
Purpose: Validates that signal handlers correctly terminate child process groups, escalate ignored SIGTERM to SIGKILL, and preserve finally block execution during KeyboardInterrupt.
Key functions/classes: _Log, alive, reset_registry, runner.kill_live_children, runner._register_child, runner.install_signal_handlers.
Direct imports/dependencies: importlib.machinery, importlib.util, os, pathlib, signal, subprocess, sys, time, and dynamically loaded runner from wrought-runner.
Obvious risk: Unsafe dynamic execution of wrought-runner via spec.loader.exec_module(runner); relies on /proc filesystem parsing and external pgrep which may fail in non-Linux environments or under load.
