# ADVERSARIAL AUDIT — GATE-RUNNER-ARM

Rails §6: *"a short adversarial audit runs before any report ships. Its job is to find the claim
the report cannot support, and to say so in the report rather than leaving it for the reviewer."*

**Counts.** **34** `raw/` files (numbered 00–28, 30–32, 99, 99b — **there is no `raw/29`**: the
queue-parse regression was appended to `raw/28` rather than given its own file, so the sequence has
a gap and no file is missing). 4 of them carry no `# cmd:` header — `raw/06`, `raw/21`
(`wrought-runner` BEFORE/AFTER source snapshots), `raw/27` (the scratch prompt), `raw/30`
(`PHASE-J-STATE.md` BEFORE). Those are **verbatim artefact copies**, where the file *is* the
evidence; the other 30 carry the command that produced them (J-95). **8 distinct `session_id`s**
are recorded across the gate's real `claude` children. 2 files edited outside the repo
(`/home/kalib/.claude/settings.json`, with a BEFORE copy at `raw/07`; `/etc/wrought/runner.conf`
NOT touched). 3 files changed in the repo: `bin/wrought-runner`, `pins.lock`,
`docs/PHASE-J-STATE.md`.

## Findings against this gate's own report

**A-1 — THE REPORT OVERCLAIMED, AND THE CLAIM WAS REPAIRED BY MEASUREMENT, NOT BY HEDGING.**
The report asserted "**Nothing** is left UNVERIFIED-ON-THE-INSTALLED-BUILD." The prompt's four
properties (b)(c)(d)(a) do **not** cover the `--add-dir` workspace boundary, which
`GATE-RUNNER-HARDEN`'s own delta lists among the things the self-update invalidated (`raw/14` of
`GATE-RUNNER`). The audit caught it before shipping; rather than soften the sentence, the gap was
closed — `raw/31`, both arms, PASS. **This is the audit's one substantive catch, and it is against
the executor.**

**A-2 — "The runner is ARMED" rests on a COMPOSITION, not on a single run, and that seam is
named rather than hidden.** Two facts were measured separately: (i) the runner **starts** on the
installed config, rc=0, clean exit; (ii) the runner **drives a real gate to PASS** on a *derived*
config differing from the installed one by 8 path leaves out of 103. **No real gate has ever run
under the installed config**, and none could here: doing so requires an `APPROVED` row in the real
`QUEUE.md`, which would run a real gate against the real courier and the real byte-freeze paths —
precisely what the prompt forbade. The composition is sound because the 8 differing leaves are all
paths and every threshold/mode/breaker is byte-identical (proven mechanically, `raw/25`) — but it
**is** a composition. The first supervised batch is the first time (i) and (ii) are the same run.

**A-3 — the budget figure is TWO SAMPLES and the report must not be read as reporting a trend.**
6.94x here, 4.6x at `GATE-RUNNER`, one run each. The report says so; repeating it here because the
derived "$55 worst case" number is the kind of figure that gets quoted without its error bar. It is
an *implication of a provisional cap times a two-sample multiple*, not a measurement.

**A-4 — the (d2b) "the model raises the timeout" finding is ONE observation of a MODEL BEHAVIOUR,
not a property of the build.** It is non-deterministic by nature: a different prompt or a different
sampling could produce either behaviour. What IS solid is the isolated re-run with the override
forbidden, which reproduced 2.1.238's backgrounding message exactly. The report leans on the
latter for its verdict and treats the former as an observation; that is the right weighting, but
the distinction is easy to lose when quoting.

**A-5 — property (a)'s isolation result DIFFERS from HARDEN's and the difference is not fully
explained.** HARDEN saw the socket move to the private runtime dir; this gate saw **no socket at
all**. The stated likely cause is the seed (`.claude.json` absent here, present in some HARDEN
arms) — that is a **hypothesis, not a measurement**; it was not isolated by varying the seed. The
report's claim is therefore deliberately narrow ("in the exact shape the runner launches gates")
and the weaker HARDEN result is kept as the thing to design against. Nothing depends on resolving
it, but it is unresolved.

**A-6 — the "no update attempt" bracket is a WEAK negative and is labelled as one in `raw/10`.**
If no build newer than 2.1.250 exists upstream, nothing would have happened either way, and this
box cannot see the release channel. The load-bearing evidence is the resolver's own verdict via
`claude doctor` (`disabled (set by env: …)` vs the control's `enabled`), which is a positive
reading. The report rests on the latter.

**A-7 — the reaper's two unexercised branches are STILL unexercised**, exactly as at HARDEN:
`virsh destroy` (libvirtd inactive throughout — the domain probe was skipped on every run of this
gate too) and the SIGTERM→SIGKILL escalation (`terminate_grace_sec`, PROVISIONAL and unmeasured).
The orphan sweep reported CLEAN twice; **a clean sweep exercises the detect path, not the kill
path.** No claim to the contrary is made anywhere in this bundle.

**A-8 — the queue-parse fix is proven on the CURRENT queue, and `FOLDED INTO` is a PREFIX match.**
`status.startswith("FOLDED INTO")` accepts `FOLDED INTO <anything>`, including a malformed or
empty gate name. That is deliberate — the status is parametric — but it means the parser no longer
validates the absorbing gate's name. Neither status is `RUNNABLE_STATUS`, so nothing runs on a
malformed one; it would simply be carried as a terminal row. Recorded so nobody discovers it later
and calls it a hole.

**A-9 — one prompt instruction was NOT followed as literally written, deliberately.** Phase 6 says
to write `PHASE-J-STATE.md` with "runner ARMED — ... next = supervised GATE-J0B". That text was
written **before** the queue-parse defect existed. The state doc records what was measured — the
defect, its authorized fix, and the clean start — rather than the dictated sentence. This is the
J-156 discipline (the box and the file win over a prompt's premise) applied to a wind-down
instruction rather than an opening one.

**A-10 — scope honesty.** One change outside the authorized set was made: the queue parser. It was
**refused first**, reported with a specified fix (`raw/24`), and applied only after an explicit
advisor+operator ruling recorded verbatim. `NOT RUN` was left alone because the ruling did not
cover it. `/etc/wrought/runner.conf` was **not edited at all**. No scale number moved.

**A-11 — the audit's own first draft miscounted, and so did the report and the journal.** They
said 32, 31 and 32 `raw/` files respectively; the true figure is **34**. All three were written at
different points while evidence was still being added, and none was re-derived before shipping.
Corrected in all three. Trivial in itself — recorded because a bundle whose own counts disagree is
exactly what a reviewer should not have to notice first, and because "re-derive the number at the
end" is the cheap habit that prevents it.

## What the audit did NOT find

No claim in the report is unsupported after A-1's repair. Every PASS/FAIL verdict traces to a
named `raw/` file whose header carries the command that produced it. The byte freeze held and the
diff is mechanical, not eyeballed. The two courier side effects were surfaced, not repaired
quietly, and the one wrong sentence this session wrote is corrected **by addition** with the wrong
text left standing (`raw/23`).
