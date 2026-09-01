# `index/` — the compact artifact `bin/wrought-scope` reads instead of the tree

Two files, and **they have opposite rules**:

| File | Rule |
|---|---|
| `scope-index.json` | **GENERATED. Never hand-edit it.** `bin/wrought-scope rebuild` produces it from `git ls-files bin src docs`, the `GATE-HORIZON` repo-map, `CLAUDE.md`'s document map, and the served `/tokenize` endpoint. Editing it by hand is a defect for exactly the reason editing a shipping verification pack is (CLAUDE.md hard rules): it is a derived artifact, and a derived artifact that has been touched no longer derives from anything. |
| `scope-fixtures.json` | **HAND-AUTHORED, and it is the definition of done.** Queries mapped to the files a session must be given. `bin/test-wrought-scope` grades the tool against it. |

## Why this directory exists at all

`GATE-HORIZON` measured the live state documents at **70,810 real tokens against a served `n_ctx`
of 65,536**. The project's own documentation does not fit the project's own model. Operator ruling
3 (`docs/ROADMAP-1.0.md` §1) settles the response: **the local model gets scoped slices, and only
the current task's slice has to fit.** `bin/wrought-scope` is what does the scoping, and this
index is what it consults so that scoping does not itself cost a tree-read.

## Properties the index holds on purpose

- **No timestamps, every key sorted.** Two rebuilds of the same tree are byte-identical, so
  `rebuild` stability is a property of the file rather than a hope. `bin/test-wrought-scope` arm C
  asserts it and also asserts that the *committed* index matches a fresh rebuild.
- **Every `tokens` value is MEASURED** by `POST /tokenize` against the served model — never
  `chars ÷ 3`. `pins.lock`'s `input_token_estimator_chars_per_token: 3.0` is a cost estimator, not
  a tokenizer; this gate measured **3.6–3.8 chars/token** on this corpus, so the estimator
  over-reads token count here by roughly a fifth to a quarter. A scoping tool whose one output is
  a token cost may not report a guess as a measurement.
- **Every `purpose` carries its `purpose_source`**, so a reader can tell a `GATE-HORIZON`
  groundedness-`RELIABLE` summary from an `UNCHECKABLE` one, from `CLAUDE.md`'s own committed
  document-map line, from a fresh local-model summary. A summary with no provenance is a claim.

## Rebuilding

    sudo -n cat /run/credentials/wrought-inference.service/inference-api-key \
        | bin/wrought-scope rebuild --key-stdin

The key reaches the process on **stdin only** (rails §5). `rebuild` **refuses to run** without the
tokenizer rather than falling back to an estimate — P4, fail loudly. A file whose content hash is
unchanged keeps its cached token count and purpose, so a rebuild after a one-file edit costs one
tokenize call and, at most, one model call.
