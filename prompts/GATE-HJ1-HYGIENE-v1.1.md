# GATE-HJ1-HYGIENE — box session prompt v1.1

*(Executor: Claude Code on forge-mini, Opus, ultracode. Advisor: Fable. Standing operator
ruling: HYGIENE PRECEDES CAPABILITY — the project's biggest risk is becoming too complex or
disorganized for a fresh /clear'd session to maintain. This session consolidates state so any
future session can reconstruct the rail position from committed docs alone. J0b is held until
this closes. v1.1 change from v1.0: the courier repo now exists — this session's bundle is
returned through it, and the rails it writes reference it.)*

TRANSPORT INTEGRITY CHECK: this prompt travels as a FILE and contains exactly TWO indented
command blocks. If either appears empty or garbled, STOP and tell the operator.

COURIER: per the protocol in /home/kalib/courier/Wrought/README.md, before running: copy this
prompt verbatim to that repo's prompts/GATE-HJ1-HYGIENE-v1.1.md, set HJ1 to RUNNING in
QUEUE.md, and push. At wind-down this session's bundle returns through the same repo (Phase 6).

## Executor mode (ultracode)

Subagents read-only. State changes serial in the main thread. Short adversarial audit before
the report ships (this is a docs session — keep it proportionate).

## Session scope

Authorized: edits to the FOUNDRY repo (pins.lock, docs/, CLAUDE.md, BUILD-JOURNAL.md) and its
operator-authored commits; and the COURIER repo writes named above and in Phase 6. NO packages,
NO unit changes, NO firewall changes, NO VM work, NO deletes under /var/lib/wrought.

## Rails

- NEVER write to or delete: /var/lib/wrought/state/**, /etc/credstore.encrypted/**,
  /var/lib/wrought/models/*.gguf, /opt/wrought/venv*, /var/lib/wrought/jobs/**,
  /var/lib/wrought/oracle/**, /var/lib/wrought/corpus/**.
- Byte freeze on /var/lib/wrought/state/orchestrator.db{,-wal,-shm}: sha256 to raw/00 at start,
  raw/99 at end, mechanical diff; any change = STOP EVERYTHING.
- Do not touch wrought-* units. J-95: every claim with its command. Evidence never overwritten.
- Foundry commits: git commit --author="Kalib <anthropic.spotlight807@passmail.net>".
- Workdir /var/lib/wrought/hj1/ with raw/ for byte-freeze + diffs.

## Guiding constraint

Each new doc is ONE PAGE. No ceremony (STOP-41's lesson). Every rule gets exactly ONE canonical
home — if a rule already lives in an existing repo doc, REFERENCE it, never duplicate. Where
completeness and maintainability conflict, choose maintainability and state what you dropped.

## Phase 1 — baseline

Byte-freeze baseline; quick health:

    systemctl is-active wrought-inference.service
    curl -s -o /dev/null -w '%{http_code}\n' --max-time 5 http://127.0.0.1:8080/health
    for c in /sys/class/drm/card*/device; do [ "$(cat $c/device 2>/dev/null)" = "0x744c" ] && echo "dGPU=$c vram_used=$(cat $c/mem_info_vram_used)"; done

## Phase 2 — ratify the substrate pins (operator has ruled; execute)

1. Read build-evidence/j0a/PROPOSED-*.md and build-evidence/j0a/round2/PROPOSED-*.md. The
   round2 versions are the measured reality; where they differ from the v1.1 candidates, round2
   wins.
2. Fold into pins.lock using THAT FILE'S existing conventions (do not invent schema): the eight
   named packages + their closure at installed versions (systemd baseline 259.5-0ubuntu3.4),
   and the guest base image
   noble-server-cloudimg-amd64.img = 0533b0655c32e68b31d792ecd6ccfca95abdbc536c4446874fe0513bd4140ffe.
   Record two ratified policies in whichever of pins.lock/docs/10 fits: (a) the OS substrate
   tracks resolute-security via unattended-upgrades — drift recorded per gate, not fought (U-1);
   (b) cloud-image GPG signature verification waived in favor of the hash pin.
3. Update the docs/10 COTS record for the substrate (KVM/QEMU/libvirt) and record Goose as the
   SELECTED agent surface, marked selected-not-yet-adopted pending GATE-J0B evidence.
4. Commit: pins: virtualization substrate ratified (GATE-J0A); goose selected pending J0B

## Phase 3 — docs/EXECUTOR-RAILS.md (new, canonical, one page)

The invariant session rails, so future prompts say "read docs/EXECUTOR-RAILS.md" instead of
restating them. Terse contents: the never-touch path list; the byte-freeze procedure; wrought-*
hands-off; J-95 evidence discipline; enumerated deletes only; secrets on stdin only, never
argv/env/config/guest; evidence never overwritten (new measurement, new filename); ultracode
discipline (subagents read-only, state changes serial, adversarial audit before any report
ships); the COURIER PROTOCOL (reference /home/kalib/courier/Wrought/README.md as the canonical
copy — do not duplicate it; state only that prompts are archived to prompts/ and bundles are
pushed unzipped to bundles/<gate>/, text-only); the PROMPT TRANSPORT RULE (prompts arrive as
files; load-bearing literals in indented blocks; block-count marker; a damaged prompt = STOP,
never reconstruct); and the WIND-DOWN DUTY: every session ends by updating docs/PHASE-J-STATE.md,
appending a BUILD-JOURNAL.md entry, and returning its bundle through the courier — the v1.4
stale-premise incident (J-156) is why the state doc is mandatory.

## Phase 4 — docs/PHASE-J-STATE.md (new, the live rail position, one page)

The single doc a fresh session reads first. Sections:
- CLOSED: GATE-J0-RECON (2026-08-10); GATE-J0A (2026-08-10, accepted 08-11, J-155) — with
  build-evidence/ paths.
- ESTABLISHED FACTS (one line each): seam = QEMU user-net, guest reaches host loopback at
  10.0.2.2 (NAT bridge refused by bind scope); boot-to-ssh ~15 s, full discard-revert ~15 s;
  base image immutable by hash; daemon model monolithic socket-activated libvirtd; dGPU
  selected by id 0x744c never by card index; kalib in kvm+libvirt groups.
- RESIDUE (deliberate, operator-accepted): libvirt default network autostart + virbr0 + two
  dnsmasq listeners + nft 91->182; libvirt-guests/qemu-kvm/machines.target enabled; the dirty
  boot-2 overlay slated for deletion by J0B Phase 0.
- RULINGS: hygiene precedes capability; substrate tracks resolute-security; GPG waiver; C4
  relaxed to audited-not-replayable; vision is a separate lower-assurance lane; commits
  operator-authored; prompts travel as files; transport = the public Wrought courier.
- OPEN: GATE-J0B next (surface = Goose; authenticating-proxy + restrict/guestfwd pinhole design;
  prompt exists advisor-side); ST-1 re-run queued (AppArmor beta->stable moved under the
  oracle's bwrap, S-1); B-1 attended chown fix; STOP-44 candidate unratified; V-1 native-login
  KVM open unverified; GPU passthrough untested; guest egress control untested; SOAK-3
  pids.peak=112 stands.
- ADVISOR-SIDE NOTE: the advisor's project doc titled "...RX 7900 XT.md" has a stale TITLE only;
  its content correctly says XTX; box docs are clean. Also: a day-old idle Claude Code peer
  session ("foundry-24") was observed on the box — operator to close it; stale sessions are
  maintainability debt.

## Phase 5 — CLAUDE.md minimal edit

Add pointers only, smallest possible diff (show it in the report): read docs/EXECUTOR-RAILS.md
before any advisor-prompted session; docs/PHASE-J-STATE.md is the live rail position for Phase J;
every session appends a BUILD-JOURNAL.md entry and returns its bundle through the courier at
wind-down.

## Phase 6 — journal, commit, and RETURN THE BUNDLE THROUGH THE COURIER

1. Verify J-155/J-156 exist in BUILD-JOURNAL.md; append J-157 for this session: pins ratified,
   rails + state docs created, CLAUDE.md pointers, courier integrated.
2. Foundry commit: docs: executor rails + phase-j state, journal J-157 (GATE-HJ1)
3. Byte-freeze re-assert (raw/99) + mechanical diff BEFORE finalizing.
4. Write REPORT-HJ1.md (what changed; full diffs of pins.lock and CLAUDE.md captured under
   raw/; the audit counts). Assemble the bundle contents as TEXT (report + raw/ + SHA256SUMS).
5. Return it through the courier: copy the bundle contents UNZIPPED into
   /home/kalib/courier/Wrought/bundles/GATE-HJ1/, set HJ1 to BUNDLED in QUEUE.md, commit
   (courier: GATE-HJ1 bundle) and push. Then:

    git -C /home/kalib/foundry status --porcelain
    git -C /home/kalib/courier/Wrought status --porcelain

   BOTH must be empty at the end — nothing uncommitted, nothing stray, in either repo. Report
   the two pushed commit shas (foundry + courier) and STOP. The advisor pulls the courier to
   adjudicate; the next gate (J0B) follows.
