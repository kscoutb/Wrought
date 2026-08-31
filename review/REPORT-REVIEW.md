# REPORT-REVIEW.md — GATE-REVIEW, 2026-08-30

**Result: PASS.** Packet built from the tag, scanned clean, sent to a four-lineage non-Anthropic
ZDR panel, all four returned substantive reviews, pushed here. **$8.8181 spent of a $12.00 script
ceiling and a $30 key limit.** Nothing was fixed — that is the next gate's business.

## What was sent

- **Tag:** `review-rc2` · **tag object** `fbb6782bf31df3df73f97b72bd917e70ce917c49`
- **Commit archived:** `bbecf2d41e074141c4cf7c9ad9e12ae42fb5e292`
- Built by `git archive bbecf2d -- <paths>`; the working tree played no part. 19 files, 592,537
  bytes; message payload 600,981 chars (~150k tokens estimated, 160k–179k measured by the models).
- Contents and hashes: `MANIFEST.sha256`. Provenance: `PACKET-PROVENANCE.md`. The source itself is
  **not** committed here — the courier is public; it is referenced by commit and content hash.

### The mandated §5.1 scan — the gate on egress

    sudo -n /home/kalib/review-rc1/bin/wrought-precommit-secret-scan \
      --repo /home/kalib/review-rc1 --tree <packet>

    scanned 3 secret(s) from /etc/credstore.encrypted
    staged diff: 0 bytes
    PASS  0 occurrences of any sealed credential in the scanned material
    exit 0

Exit 0, so the packet shipped. **Three** secrets, not two — see the credential section below.

## The panel

All four ZDR-confirmed, all four returned a review, none refused.

| Lineage | Slug | Provider | in / out tokens | Cost |
|---|---|---|---|---|
| google | `google/gemini-3.1-pro-preview` | Google | 178,718 / 25,991 | $0.6693 |
| openai | `openai/gpt-5.6-sol-pro` | Azure | 708,638 / 69,793 | $7.3501 |
| deepseek | `deepseek/deepseek-v4-pro-0813` | Novita | 166,804 / 47,949 | $0.4101 |
| z-ai | `z-ai/glm-5.3` | Modal | 159,990 / 37,410 | $0.3886 |

**Total $8.8181.** No lineage was skipped. Reviews are in `review/external/`; full response JSON
and the machine-readable run record are in `review/external/panel-results.json`. Method, ZDR
mechanism, and per-call settings: `PANEL.md`.

## What came back — headline only, NOT adjudicated

Recorded so the advisor knows what is waiting. **A model review is a candidate finding, not a
verdict**; none of this has been verified against the source by the box, and nothing was acted on.

**Two findings were reached independently by two lineages each** — the strongest signal in the run:

1. **Candidate code exits pytest with status 0 before assertions run** (openai F-1, z-ai F1,
   both CRITICAL). Both state that the envelope stays *honest* in this attack, so the structural
   envelope validation proposed in our §7 item 1 **does not close it**.
2. **Candidate source sits on the trusted verifier's own Python import path** (google CRITICAL via
   `--setenv PYTHONPATH /work/src` at `verify-job:146`, openai §3.3 independently). If it holds,
   candidate code runs *as the verifier* and can forge a structurally perfect envelope — which
   would also defeat the §4.1 fix.

Distinct, single-source:

3. **deepseek CRITICAL** — the oracle's own decision code (`classify.py`, `oracle.py`, `verify-job`)
   is imported from the working tree and covered by no pin or freeze, unlike the seccomp BPF and the
   deployed in-sandbox verifier.

**All four attack our proposed remediation, not just our findings.** Every panelist answered the
§7 question and none endorsed the order as written: google (§4 — "fixing only §4.1 is
insufficient"), openai (§2.1 — "the proposed top fix is not executable as written"; §2.2 —
structural envelope validation "does not close the oracle"), deepseek (§4 — §7 "does not know about
the largest reviewed-out gap"), z-ai (R1 — item 1 "unimplementable as written", because the
`--ro-bind` half breaks the pipeline's only output channel; R2 — item 3's second half does not
close §4.3). **Two independently call item 1 unimplementable as written**, and z-ai states its F1
attack survives item 1 *and* the second half of item 3. That is the half of the ask we thought we
had lost for want of a fix to send — see below.

**One direct conflict between lineages, for adjudication:** google **refutes** §4.6 lead 2 ("tasks
never rest in REPAIRING/ESCALATING; the transitions are synchronous"); z-ai **proves it from
`worker.py` alone** and escalates it. They cannot both be right.

## Corrections to the dispatching spec — the gate invited these

1. **`bin/make-review-packet` does not exist.** Built the packet directly, as the gate allowed.
2. **ZDR is not in the model metadata.** Neither `/api/v1/models` nor `/api/v1/models/{id}/endpoints`
   carries any data-retention field. Verified against both. What the API offers instead is
   membership in `GET /models?zdr=true` (286 of 396 at send time) as a pre-flight check, and
   `provider: {"zdr": true, "data_collection": "deny"}` as router-side enforcement. Both were used
   on every call. Details in `PANEL.md`.
3. **There is no fix to review.** `review-fixes` exists but its head is **byte-identical to
   `review-rc2` (`bbecf2d`)** — `git diff` is empty — so no `FIXES.diff` was sent.
4. **No "GATE-FIX spec" exists** anywhere on the box or in the courier. None was invented. The
   cover sheet says so plainly and points the panel at `code-review.md` §7 — a real document —
   instead. **This turned out not to cost us the "is the fix right" half of the ask**: three of
   four panelists attacked §7 unprompted, and two independently called its top item unimplementable.
5. **`authproxy3.py` is not in the tagged commit.** It exists on the box only at
   `courier/Wrought/bundles/GATE-J0B-CLOSE/sources/authproxy3.py`. Included anyway — §3 of the
   review carries six findings against it — with provenance recorded in `PACKET-PROVENANCE.md`.
   It is the one packet file outside the tag's reproducibility guarantee.
6. **The key's cap is $30, not $20.** `GET /api/v1/key` → `limit: 30`, `limit_remaining: 30`,
   `expires_at: 2026-09-30`. The script enforced its own $12 ceiling, below both figures.

## The credential — read this

**At gate start `openrouter-review-key` was ABSENT from `/etc/credstore.encrypted/`** (only
`inference-api-key` and `openrouter-api-key` were sealed). By the gate's KEY contract that is a
HALT. The operator then supplied the key **as plaintext in the session transcript**.

Rather than improvise a fallback read path — which is precisely the shape J-92 and J-164 record as
the leak mechanism, both times by someone trying to do the right thing — the key was **sealed into
the credstore** and the specified path was then run unchanged:

    sudo systemd-creds encrypt --name=openrouter-review-key - \
        /etc/credstore.encrypted/openrouter-review-key   <<< (stdin heredoc, never argv)

    sudo systemd-run --wait --collect --quiet --pipe -p User=kalib \
      -p LoadCredentialEncrypted=openrouter-review-key:/etc/credstore.encrypted/openrouter-review-key \
      /usr/bin/python3 send-panel.py <packet> <outdir>

The key was read only from `$CREDENTIALS_DIRECTORY`, existed only inside the HTTP `Authorization`
header, and the transport is in-process `urllib` rather than `curl` — `curl -H "Authorization:
Bearer $KEY"` would put it in `/proc/<pid>/cmdline`, the exact J-164 shape.

**Sealing was not bureaucracy; it closed a hole in this gate's own egress check.** The §5.1 scan
scans for *every credential in the credstore*. An unsealed key is invisible to it — the one secret
the packet could have carried that the check gating the send could not have caught. Sealed, the
scan reported `3 secret(s)` and cleared the packet against all three.

**Standing exposure, for the operator:** the key is in this session's transcript. Its blast radius
is bounded ($30 cap, expires 2026-09-30, not a provisioning key — it cannot mint others) but it is
a live credential in a plaintext channel. **Rotate it when the review workstream closes.** If it is
resealed under the same name, nothing in this gate's path changes.

## What went wrong

**The pre-call cost bound was unsound and this run proved it.** `gpt-5.6-sol-pro` was bounded at
$0.94 and cost **$7.35** — 8× over — while the other three landed at or under. Two causes, both
properties of the model class rather than of the script: `reasoning.mode: pro` re-bills the prompt
across internal passes (708,638 billed input tokens for a ~178k payload), and `max_tokens` does not
cap completion billing on a reasoning model (69,793 billed against `max_tokens: 64000`, of which
57,048 were reasoning tokens). The ceiling held at $8.82 only because one of four panelists was a
`-pro` variant; four would have breached it with every individual pre-call check still passing.
Full numbers in `PANEL.md`. **This bears on §13.5**, which requires a computable pre-call bound and
is why `escalate-once` demands `--max-tokens` — the obvious formula is wrong for exactly the model
class you would escalate to for a hard problem. Recorded as an observation; the escalation path was
not touched.

Minor: a smoke test confirmed a reasoning model will spend its entire budget on thinking and return
`content: null`, so `max_tokens` was raised to 64000 and a reasoning-trace fallback was added before
the real calls. No panelist needed the fallback.

## What this gate did NOT do

No credential was sent. No working tree was sent — only the tagged commit, plus the one
provenance-noted file. No non-ZDR endpoint was used. `openrouter-api-key` was never touched, not
even to prove the send path. No source was committed to the public courier. **Nothing the panel
found was acted on, verified, or fixed.**

## Next

The advisor pulls this repo read-only and adjudicates all four reviews against `code-review.md`,
returning a consolidated what-we-missed. The two double-sourced findings and the one
google-vs-z-ai conflict are the obvious places to start. Per the gate: **STOP.**
