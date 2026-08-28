# GATE-SCRATCH-PROBE — trivial end-to-end probe

ALLOWED-TOOLS: Bash
MAX-BUDGET-USD: 2.0

You are a gate running under wrought-runner. Do exactly this, then stop:

1. Create the directory `bundles/GATE-SCRATCH-PROBE/` inside the courier repo at
   the path given by COURIER below.
2. Write a file `REPORT.md` in it containing one line: `scratch probe ok`.
3. From inside that directory, run: `sha256sum REPORT.md > SHA256SUMS`
4. Edit `QUEUE.md` in the courier root: change the `GATE-SCRATCH-PROBE` row's status
   from `APPROVED` to `BUNDLED`. Keep the table format `| `GATE-SCRATCH-PROBE` | `BUNDLED` | ...notes... |`.
5. From the courier root, run: `git add -A && git commit -q -m "scratch probe bundle" && git push -q origin HEAD`
6. Reply with exactly: SCRATCH-PROBE-DONE

COURIER = the courier repo path is in the environment as the only git repo under the
directory this prompt was read from; it is: /tmp/claude-1000/-home-kalib-foundry/c7320a0f-9ba2-4fda-81e1-9a40647bd286/scratchpad/p5/courier
