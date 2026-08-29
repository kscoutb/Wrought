# GATE-ST-1 — PROPOSED-PINS-DELTA

**Not applied.** The ST-1 prompt is internally split on who applies this: Phase 3 says
"Re-pin in `pins.lock`", Phase 4 says "PROPOSED-PINS-DELTA", and the prompt's own rails
line says "Re-pinning is a foundry commit (**operator-authored**)". The box prepares the
exact diff and leaves authorship to the operator; that is the reading that satisfies all
three, and it is the ambiguity flagged rather than resolved by fiat.

The evidence that licenses each change is named per line (J-95: a measured value carries
the command that produced it, or it is not evidence).

---

## 1. `substrate.kernel` — MOVE (pins.lock:517)

```diff
 substrate:
-  kernel: 7.0.0-28-generic
+  kernel: 7.0.0-30-generic          # ST-1-VALIDATED 2026-08-29: build-evidence/st-1/raw/09
```

**Licensed by** `raw/09`: at the pinned shape, fresh-process first request, with
`llama-server`, the model GGUF and Mesa all verified bit-identical to their pins
(`raw/03`, `raw/02`), all four trigger prompts produced **token streams byte-identical to
the 2026-08-02 GATE-16 run**. The kernel was the only variable, so this is a direct
measurement of the bump, not an inference from a proxy.

## 2. `substrate.kernel_cmdline_full` — MOVE (pins.lock:538)

This line **embeds the kernel version** and must move with it, or the two copies drift:

```diff
-  kernel_cmdline_full: "BOOT_IMAGE=/boot/vmlinuz-7.0.0-28-generic root=UUID=d05b8e41-3ced-4c77-83e0-b1fbf56589c6 ro amdgpu.runpm=0 quiet splash crashkernel=2G-4G:320M,4G-32G:512M,32G-64G:1024M,64G-128G:2048M,128G-:4096M"
+  kernel_cmdline_full: "BOOT_IMAGE=/boot/vmlinuz-7.0.0-30-generic root=UUID=d05b8e41-3ced-4c77-83e0-b1fbf56589c6 ro amdgpu.runpm=0 quiet splash crashkernel=2G-4G:320M,4G-32G:512M,32G-64G:1024M,64G-128G:2048M,128G-:4096M"
```

**Licensed by** `raw/02` (`cat /proc/cmdline`, verbatim). **`amdgpu.runpm=0` survived the
bump** — checked explicitly, because pins.lock:535 warns that a kernel update dropping it
silently returns the box to a wedge-capable configuration. `grep -c 'amdgpu.runpm=0'` = 1.

## 3. AppArmor — NEEDS AN OPERATOR DECISION ON *WHERE*, because there is no key to move

`grep -nE '^\s+(apparmor|libapparmor)' pins.lock` returns **nothing**: AppArmor has never
been a pinned key, only a `drift_observed` narrative entry. So "re-pin AppArmor as
validated" cannot be a move — it is either a NEW KEY or an edit to the drift entry.
**The box will not invent a configuration key** (CLAUDE.md hard rule). Two options:

**Option A — new key, following the file's own OPERATOR-AUTHORIZED convention** (the same
provenance comment used for `kernel_cmdline_params` and `os_update_policy`):

```diff
   mesa: 26.0.3-1ubuntu1
+  # OPERATOR-AUTHORIZED KEY (not in pins.lock.template). Added on the 2026-08-29 in-session
+  # ruling that the AppArmor half of the ST-1 drift be MEASURED, not validated by association.
+  apparmor: 5.0.2-0ubuntu1~26.04.1   # ST-1-VALIDATED 2026-08-29 via GATE-21: build-evidence/st-1/raw/12
```

**Option B —** leave the pin surface unchanged and only resolve the drift entry (§4).

Either way the **scope limit stands and must be written down**: GATE-21 passed 9/9, which
covers the sandbox BUILDING correctly and remaining offline on this kernel + AppArmor. It
does **not** re-classify the GATE-23/25 exit-code taxonomy, which pins.lock:571 explicitly
records as not re-done. That half is still open.

## 4. `drift_observed` — RESOLVE two entries (pins.lock:568, 570, 571)

Per the file's own rule ("a pin moves only in the gate that re-measures it"), these entries
should be marked resolved **by this gate**, not deleted — the history is the point:

- **2026-08-28 kernel -30 entry (:568)** → append:
  `RESOLVED 2026-08-29 by GATE-ST-1: ST-1-VALIDATED, pin moved. Token streams byte-identical to the 2026-08-02 GATE-16 baseline on all four trigger prompts (build-evidence/st-1/raw/09). NOTE the header-removal half of this entry is NOT resolved — linux-headers-7.0.0-28 are still gone and the -28 kernel is still not fully rebuildable from the box; validating -30 does not restore -28.`
- **2026-08-12 kernel -29 entry (:570)** → append:
  `SUPERSEDED and now moot: the box is on -30, validated 2026-08-29 by GATE-ST-1.`
- **2026-08-11 apparmor entry (:571)** → append:
  `PARTIALLY RESOLVED 2026-08-29 by GATE-ST-1: GATE-21 bwrap smoke re-run on kernel 7.0.0-30 + AppArmor 5.0.2, 9/9 checks pass, merged-/usr symlink layout resolves the interpreter and the netns holds only lo (build-evidence/st-1/raw/12). The GATE-23/25 exit-code taxonomy remains NOT re-classified, so this entry is downgraded from ST-1-TRIGGER-UNSATISFIED to a NARROWER open item, not closed.`

## 5. NOT proposed, and why

- **`substrate.mesa`** — unchanged at `26.0.3-1ubuntu1` (`raw/02`). Nothing to move. Its
  being unchanged is load-bearing evidence for §1: it is why the kernel is the only variable.
- **The 15 libvirt point-release pins** — still drifted, still not an ST-1 trigger, still
  an open question for the advisor (pins.lock:569). This gate did not touch them.
- **A `long_context` trigger prompt** — see the report's A-2. The trigger set has no
  long-context member, so no pin claim about long context is made here.
