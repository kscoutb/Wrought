# PROPOSED-PINS-DELTA — GATE-J0B-CLOSE, 2026-08-29

**PROPOSED, NOT APPLIED.** Every item below is a **new key**, and CLAUDE.md's first hard rule makes
a new configuration key a gate question, not a gate's own decision. The one numeric *value* here is
already ratified elsewhere in `pins.lock`; the keys that would carry these values are not.

`pins.lock` currently holds `virtualization.guest_agent_surface` with goose's tag, asset, size and
hashes — **but nothing about how goose is CONFIGURED**. Everything measured this gate about the
configuration shape lives only in evidence. That is the gap these entries close.

---

## P-1 — the goose extension configuration shape (`virtualization.guest_agent_surface`, additive)

Measured at `raw/23`, `raw/24`, `raw/26`, `raw/29`; acceptance taken from the tool list goose sends
a model, never from a config parse.

    # ---- ADDED BY GATE-J0B-CLOSE 2026-08-29. Measured, not chosen. ----
    # The single most load-bearing fact: for a FILESYSTEM-WRITE tool, NO `extensions:` stanza is
    # required at all. goose 1.46 ships `developer` (write/edit/shell) as type: platform,
    # enabled: true, with no config file present. GATE-J0B-RESUME's contrary conclusion --
    # "the agent had no filesystem tool to act with" -- was re-tested with ONE variable (its own
    # byte-identical 88-byte config.yaml) and is MEASURED FALSE.
    extension_schema:
      bundled_type: platform          # NOT "builtin". 13 bundled extensions, all type: platform.
      stdio_type: stdio               # for an external MCP server over stdio
      # The stdio shape, WRITTEN BY `goose configure` ITSELF under a pty driver -- which is what
      # makes it safe to pin. Field order as goose emits it.
      stdio_fields: [enabled, type, name, description, cmd, args, envs, env_keys, timeout, cwd, bundled]
      stdio_timeout_default: 300      # goose's own default, accepted at the prompt
      default_tools_advertised: 18    # with no extensions stanza; includes write, edit, shell
      write_tool_params: [path, content]   # both required, per the schema goose advertises
      # OPERATIONAL WARNING, measured (G-1): `goose configure` REWRITES config.yaml and DROPS the
      # flat top-level keys GOOSE_PROVIDER and GOOSE_MODEL, replacing them with a `providers:`
      # block and `active_provider:`. OPENAI_HOST survives. A harness that hand-writes the flat
      # keys and then runs `goose configure` loses them silently.
      configure_rewrites_config: true
      # C5: the configure walk wrote NO secrets.yaml. The guest still holds no credential in any
      # form. (Closes the hole GATE-J0B-RESUME stated it could not test.)
      configure_writes_secrets_file: false
      # goose's own MCP client negotiates this. GATE-J0B-RESUME's HAND-WRITTEN client negotiated
      # 2024-11-05, so the seam had been probed at a different version than the real client uses.
      mcp_protocol_version: "2025-11-25"
      mcp_client_info: "goose-cli/1.46.0"

## P-2 — the proxy's injected generation bound (NEW key, and the reason it is only proposed)

    # Injected by authproxy3.py into any chat/completions body whose max_tokens is null or absent.
    # THE NUMBER IS NOT NEW AND WAS NOT CHOSEN BY THIS GATE: 24000 is `serving.reasoning_budget`,
    # whose committed n=78 derivation calls it "the same bound already ratified for
    # --escalation-max-tokens". It is the only ratified per-generation token bound in pins.lock.
    # Against ctx_size: 65536 it cuts a worst-case abandoned generation by ~2.7x.
    #
    # WHAT IS ACTUALLY BEING ASKED: not "is 24000 right" but "may a KEY exist that carries it into
    # the guest-agent path". A value ratified for escalation is not automatically ratified for a
    # different consumer, and the box will not mint the key on that inference.
    guest_agent_max_tokens_bound: 24000

## P-3 — the pinhole transport (a CORRECTION to an established fact, not just a new key)

**This one changes something the project believes.** `docs/PHASE-J-STATE.md` ESTABLISHED FACTS says
*"The seam is QEMU user-mode networking"* and records the guestfwd pinhole as proven. It is proven
**for a single sequential connection only**, and that qualifier is not in the doc.

    # MEASURED GATE-J0B-CLOSE 2026-08-29, raw/45 and raw/46. One variable: the transport between
    # the guest and the proxy, same proxy, same upstream, same instant.
    #   guestfwd=tcp:10.0.2.100:8081-tcp:127.0.0.1:8081
    #     16 guest connections (8 sequential + 8 concurrent) -> 0 accepted by the proxy.
    #     libslirp opens ONE host-side chardev and funnels every guest connection into it, so a
    #     second concurrent connection is not served at all and the stream desynchronises. This is
    #     the HTTP/0.9 empty-response "wedge" GATE-J0B-RESUME recorded; its stated hypothesis
    #     (connection-table exhaustion) is MEASURED FALSE -- it reproduces on the FIRST concurrent
    #     pair and needs no retry storm.
    #   HOST, 8 concurrent, same proxy -> 8 accepted, 8x 200, all under 3 ms.
    #   ssh -N -R 18081:127.0.0.1:8081 (carried inside the ssh channel the gate already holds)
    #     -> 8 of 8 concurrent at 200; 3 concurrent goose runs, 12/12 chat calls answered, 0 lost.
    #     Egress unchanged and RE-PROVEN with the tunnel up: external curl exit 6, 10.0.2.2:8080
    #     curl exit 7. The guest keeps restrict=on and gains only a LOOPBACK listener, and the
    #     carrier is authenticated -- tighter than an unauthenticated IP-level forward.
    guest_pinhole_transport: ssh-reverse-forward     # supersedes guestfwd for any concurrent use
    guest_pinhole_guestfwd_concurrency_safe: false

**UN-PINNABLE UNTIL SOMEONE RULES, and named here rather than quietly pinned:** whether an
`ssh -N -R` process can be held by a **runner gate child** for a whole gate, inside the scope, and
reaped by rails §13. This gate proved the transport **attended**. That is not the same claim.

---

## What is deliberately NOT proposed

- **No change to `guest_base_image`.** The 16 G overlay (D-1) is an *overlay* parameter; the backing
  file is byte-identical after every boot and its pin is untouched.
- **No new goose version or asset pin.** The pinned v1.46.0 tag, asset size and both hashes
  reproduced exactly for the third and fourth time; nothing moved.
- **No cost-cap value.** This gate's cost is recorded (`raw/51`) but it is an attended-direct
  number, and §7 of the report argues it must not be used to set a runner child's cap.
