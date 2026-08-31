#!/usr/bin/env python3
"""GATE-HORIZON PHASE 4 TOP-UP — restore the two lineages the first panel run lost.

WHY THIS EXISTS. The first run used Appendix A verbatim. Two of its five slots were wasted, for
two different reasons, and both are recorded rather than quietly patched:

  * google  -- Appendix A's pick_models() sorts candidates by
                  ("pro" in s or "thinking" in s or "reasoning" in s, len(s))
              so "prefer non-'-pro' variants" is implemented as "prefer the SHORTEST SLUG". For
              the google lineage that selected `google/gemma-3-4b-it`, a 4B model, to perform a
              staff-level architecture review. Its output CONFABULATED: the packet states
              "Media generation / vision / computer-use -- Nothing. No component of any kind" and
              the 4B review reported that media generation, library organisation, avatar
              replacement and a screenshot+vision loop were all working. It read the VISION
              wish-list as the as-built inventory. Marked UNRELIABLE and excluded.
  * deepseek -- HTTP 400. The picker chose `deepseek/deepseek-r1`, whose endpoint caps at 64,000
              tokens; the request was ~99,760 (59,760 input + 40,000 max output). A hard failure,
              not a bad review.

THE FIX HERE IS EXPLICIT SLUGS, NOT A CLEVERER HEURISTIC. Both are taken from the LIVE
`GET /models?zdr=true` listing at run time -- nothing is invented, and each is verified present
in that listing before it is used, exactly as the original does. Both were also the slugs this
project's own GATE-REVIEW panel used on 2026-08-30, so they are precedented here rather than
newly chosen. Both carry >=1,048,576 context, so the FULL packet fits and no trimming is needed:
the 64k limit was a property of deepseek-r1, not of the deepseek lineage.

CREDENTIAL DISCIPLINE IS CARRIED OVER UNCHANGED from bin/gate-review-send-panel and Appendix A:
the key is read only from the service-private $CREDENTIALS_DIRECTORY tmpfs and exists only inside
the HTTP Authorization header. Never an argv, never an env value, never written, never printed.
ZDR is checked two ways -- pre-flight membership in /models?zdr=true, and router-side enforcement
via provider.zdr + data_collection="deny" -- so a non-ZDR endpoint is refused rather than silently
substituted.
"""
from __future__ import annotations
import json, os, pathlib, sys, time, urllib.request, urllib.error

BASE = "https://openrouter.ai/api/v1"
# Deliberately far below the operator's $15 authorisation: this is a top-up of two calls whose
# observed sibling costs were $0.67 and $0.41 at GATE-REVIEW. A ceiling that is only a little
# above the expectation is the one that actually catches a surprise.
CEILING_USD = 5.00
MAX_TOKENS = 20000

TOPUP = [("google",   "google/gemini-3.1-pro-preview"),
         ("deepseek", "deepseek/deepseek-v4-pro-0813")]

SYSTEM = ("You are an independent staff-level software architect. You are reviewing a working, "
          "security-hardened, single-node local-AI code-manufacturing pipeline against its "
          "operator's stated 1.0 vision. Be concrete and honest, and ground every claim in the "
          "packet you are given. The packet distinguishes sharply between what is BUILT and what "
          "is merely WISHED FOR in the vision; do not report a vision item as an existing "
          "capability. Where the packet says a subsystem does not exist, it does not exist.")


def key() -> str:
    d = os.environ.get("CREDENTIALS_DIRECTORY")
    if not d:
        sys.exit("no CREDENTIALS_DIRECTORY; launch under systemd LoadCredentialEncrypted")
    return (pathlib.Path(d) / "openrouter-review-key").read_text(encoding="utf-8").strip()


def GET(path: str, k: str):
    r = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {k}"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)


def main() -> int:
    packet_f, ask_f, outdir = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
    outdir.mkdir(parents=True, exist_ok=True)
    k = key()

    rem = (GET("/key", k).get("data") or {}).get("limit_remaining")
    print(f"key limit_remaining: {rem}", flush=True)
    if rem is not None and rem < CEILING_USD + 1:
        sys.exit(f"limit_remaining {rem} below ceiling {CEILING_USD}+1; aborting")

    catalog = {m["id"]: m for m in GET("/models", k)["data"]}
    zdr = {m["id"] for m in GET("/models?zdr=true", k)["data"]}

    user = (pathlib.Path(packet_f).read_text(encoding="utf-8", errors="replace")
            + "\n\n" + pathlib.Path(ask_f).read_text(encoding="utf-8", errors="replace"))
    approx_in = len(user) / 4.0
    print(f"payload: {len(user)} chars", flush=True)

    spent, rows = 0.0, []
    for lineage, slug in TOPUP:
        rec = {"lineage": lineage, "slug": slug, "zdr_prechecked": slug in zdr}
        if slug not in zdr:
            rec |= {"status": "SKIPPED", "reason": "not ZDR-eligible at send time; a non-ZDR send "
                    "is not an acceptable substitute"}
            print(f"[{lineage}] SKIP {slug}: not ZDR", flush=True); rows.append(rec); continue

        pr = catalog[slug]["pricing"]
        bound = approx_in * float(pr["prompt"]) + MAX_TOKENS * float(pr["completion"])
        rec["precall_cost_bound_usd"] = round(bound, 4)
        # KNOWN-OPEN item 15: this bound is MEASURED unsound for reasoning models (8x under on one
        # observation). It is kept because it is the committed convention, and it is labelled here
        # so nobody reads it as a guarantee. The real guard is the ceiling plus a two-call run.
        if spent + bound > CEILING_USD:
            rec |= {"status": "SKIPPED", "reason": f"bound ${bound:.2f} would cross ${CEILING_USD}"}
            print(f"[{lineage}] SKIP {slug}: budget", flush=True); rows.append(rec); continue

        body = {"model": slug,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}],
                "max_tokens": MAX_TOKENS,
                "provider": {"zdr": True, "data_collection": "deny"},
                "usage": {"include": True}}
        req = urllib.request.Request(
            BASE + "/chat/completions", data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {k}",      # the ONLY place the key exists
                     "Content-Type": "application/json",
                     "X-Title": "Wrought Foundry GATE-HORIZON topup"})
        print(f"[{lineage}] -> {slug} (bound ${bound:.2f})", flush=True)
        t0 = time.time()
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=1800))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:1500]
            rec |= {"status": f"HTTPError {e.code}", "body": detail,
                    "elapsed_s": round(time.time() - t0, 1)}
            print(f"[{lineage}] HTTP {e.code}: {detail[:300]}", flush=True); rows.append(rec); continue
        except Exception as e:
            rec |= {"status": "ERROR", "error": f"{type(e).__name__}: {e}"}
            print(f"[{lineage}] ERROR {e}", flush=True); rows.append(rec); continue

        (outdir / f"{lineage}-{slug.split('/')[-1]}.raw.json").write_text(
            json.dumps(resp, indent=2), encoding="utf-8")
        u = resp.get("usage") or {}
        cost = float(u.get("cost") or 0.0)
        if not cost:
            cost = (u.get("prompt_tokens", 0) * float(pr["prompt"])
                    + u.get("completion_tokens", 0) * float(pr["completion"]))
            rec["cost_source"] = "computed from pricing x tokens (usage.cost absent)"
        else:
            rec["cost_source"] = "usage.cost returned by OpenRouter"
        spent += cost
        ch = (resp.get("choices") or [{}])[0]
        msg = ch.get("message") or {}
        text = msg.get("content") or ""
        if not text.strip() and (msg.get("reasoning") or "").strip():
            text = ("_(model returned no `content`; the following is its `reasoning` trace, "
                    "preserved so the call is not lost)_\n\n" + msg["reasoning"])
            rec["used_reasoning_fallback"] = True
        rec |= {"status": "OK", "elapsed_s": round(time.time() - t0, 1),
                "provider": resp.get("provider"), "generation_id": resp.get("id"),
                "finish_reason": ch.get("finish_reason"), "usage": u,
                "cost_usd": round(cost, 4), "cumulative_usd": round(spent, 4),
                "response_chars": len(text)}
        (outdir / f"{lineage}-{slug.split('/')[-1]}.md").write_text(
            f"# External review (TOP-UP) — {lineage} / `{slug}`\n\n"
            f"- Provider: `{resp.get('provider')}` · generation `{resp.get('id')}`\n"
            f"- ZDR: pre-checked in `/models?zdr=true`; enforced via `provider.zdr=true` + "
            f"`provider.data_collection=\"deny\"`\n"
            f"- finish_reason: `{ch.get('finish_reason')}` · cost ${cost:.4f} · "
            f"{u.get('prompt_tokens','?')} in / {u.get('completion_tokens','?')} out\n\n---\n\n"
            f"{text if text.strip() else '_(model returned empty content)_'}\n", encoding="utf-8")
        print(f"[{lineage}] OK {len(text)} chars, ${cost:.4f}, cum ${spent:.4f}", flush=True)
        rows.append(rec)

    (outdir / "panel-topup-results.json").write_text(
        json.dumps({"ceiling_usd": CEILING_USD, "max_tokens": MAX_TOKENS,
                    "total_spend_usd": round(spent, 4), "results": rows}, indent=2),
        encoding="utf-8")
    print(f"\nTOP-UP TOTAL ${spent:.4f} of ${CEILING_USD:.2f} ceiling", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
