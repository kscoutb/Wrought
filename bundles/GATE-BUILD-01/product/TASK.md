---
task_id: "TASK-2026-0901-scope-lint"
spec_version: "1.0"
canon_version: "canon_v2"
spec_sha256: "<computed by canon_v2; EXCLUDED from its own hash input - never hand-written>"
complexity_signals:
  requirement_count: 8
  cross_file_scope: false
  has_concurrency: false
  dependency_count: 0
tests:
  fail_to_pass:
    - test_id: "test_clean_index"
      path: "tests/test_scope_lint.py::test_clean_index"
      verifies: ["REQ-001"]
    - test_id: "test_missing_from_index"
      path: "tests/test_scope_lint.py::test_missing_from_index"
      verifies: ["REQ-002"]
    - test_id: "test_absent_from_tree"
      path: "tests/test_scope_lint.py::test_absent_from_tree"
      verifies: ["REQ-003"]
    - test_id: "test_stale_hash"
      path: "tests/test_scope_lint.py::test_stale_hash"
      verifies: ["REQ-004"]
    - test_id: "test_bad_token_count"
      path: "tests/test_scope_lint.py::test_bad_token_count"
      verifies: ["REQ-005"]
    - test_id: "test_zero_tokens_is_valid"
      path: "tests/test_scope_lint.py::test_zero_tokens_is_valid"
      verifies: ["REQ-005"]
    - test_id: "test_multiple_findings_per_path"
      path: "tests/test_scope_lint.py::test_multiple_findings_per_path"
      verifies: ["REQ-006"]
    - test_id: "test_deterministic_sort_and_counts"
      path: "tests/test_scope_lint.py::test_deterministic_sort_and_counts"
      verifies: ["REQ-007"]
    - test_id: "test_structural_malformed_raises"
      path: "tests/test_scope_lint.py::test_structural_malformed_raises"
      verifies: ["REQ-008"]
    - test_id: "test_bad_sha_raises_names_path"
      path: "tests/test_scope_lint.py::test_bad_sha_raises_names_path"
      verifies: ["REQ-008"]
    - test_id: "test_bad_tree_value_raises_names_path"
      path: "tests/test_scope_lint.py::test_bad_tree_value_raises_names_path"
      verifies: ["REQ-008"]
    - test_id: "test_record_not_a_dict_raises_names_path"
      path: "tests/test_scope_lint.py::test_record_not_a_dict_raises_names_path"
      verifies: ["REQ-008"]
    - test_id: "test_no_io_and_no_clock"
      path: "tests/test_scope_lint.py::test_no_io_and_no_clock"
      verifies: ["CON-001"]
    - test_id: "test_inputs_not_mutated"
      path: "tests/test_scope_lint.py::test_inputs_not_mutated"
      verifies: ["CON-002"]
  pass_to_pass:
    - test_id: "test_module_surface"
      path: "tests/test_scope_lint.py::test_module_surface"
      verifies: ["REQ-001"]
---

# TASK SPECIFICATION

## Overview
Implement `scope_lint.py` exposing a PURE function

    lint_index(index: dict, tree: dict[str, str]) -> dict

that checks a context-scoping index against the file tree it claims to describe, and reports every
way the two have drifted apart. It performs no I/O: a thin operational wrapper (outside this task)
reads `index/scope-index.json` and hashes the tracked files, and passes both in.

`index` is the parsed scoping index. Only one key is in scope here: `index["files"]`, a dict
mapping a repository-relative path (str) to a record (dict). A record has `sha256` (a 64-character
lowercase hexadecimal string — the digest of the file's bytes as of the last index build) and
`tokens` (a non-negative int — the measured cost of loading that file). Records carry other keys;
they are ignored.

`tree` is a dict mapping repository-relative path (str) to the file's CURRENT sha256, for exactly
the files that ought to be indexed.

An index that has drifted from its tree is worse than no index: it reports a token cost for bytes
that are not there any more, and it silently omits files a session needed. This function is what
makes that drift loud.

## Requirements
- **REQ-001**: WHEN every path in `tree` is present in `index["files"]`, every indexed path is
  present in `tree`, every pair of digests agrees, and every record's `tokens` is valid, THE SYSTEM
  SHALL return a result whose `findings` list is empty and whose `worst_severity` is `"none"`.
- **REQ-002**: WHEN a path is present in `tree` and absent from `index["files"]`, THE SYSTEM SHALL
  emit a finding with `kind = "MISSING_FROM_INDEX"` and `severity = "high"` — a file a session
  could be asked to load that the index cannot offer.
- **REQ-003**: WHEN a path is present in `index["files"]` and absent from `tree`, THE SYSTEM SHALL
  emit `kind = "ABSENT_FROM_TREE"`, `severity = "high"` — the index is quoting a token cost for a
  file that no longer exists.
- **REQ-004**: WHEN a path is present in both and `index["files"][path]["sha256"]` differs from
  `tree[path]`, THE SYSTEM SHALL emit `kind = "STALE_HASH"`, `severity = "high"` — the file was
  edited after the index was built, so its recorded cost and summary describe bytes that are gone.
- **REQ-005**: WHEN a record for a path present in `tree` has no `tokens` key, or a `tokens` value
  that is not an `int`, or an `int` below zero, THE SYSTEM SHALL emit `kind = "BAD_TOKEN_COUNT"`,
  `severity = "medium"`. A `bool` is NOT an acceptable `tokens` value even though Python makes it
  an `int`.
- **REQ-006**: WHEN a single path satisfies more than one of REQ-004 and REQ-005, THE SYSTEM SHALL
  emit one finding PER matched condition and SHALL NOT collapse them — nothing hides behind a
  higher-severity sibling.
- **REQ-007**: THE SYSTEM SHALL return `findings` sorted by descending severity (`high` before
  `medium`), ties broken by `path` then `kind`, so identical inputs yield a byte-identical result;
  and SHALL include `counts` (a dict of kind -> int, containing only kinds that occurred) and
  `worst_severity` (`"high"`, `"medium"`, or `"none"`). Every finding SHALL include the 3 keys
  `kind`, `severity` and `path`; additional keys on a finding are permitted.
- **REQ-008**: IF `index` is not a dict, OR has no `"files"` key, OR `index["files"]` is not a
  dict, OR `tree` is not a dict, THEN THE SYSTEM SHALL raise `ValueError` and SHALL NOT return a
  partial result. IF any record in `index["files"]` is not a dict, OR its `sha256` is missing, is
  not a `str`, or is not exactly 64 lowercase hexadecimal characters, OR the corresponding `tree`
  value is not such a string, THEN THE SYSTEM SHALL raise `ValueError` whose message contains the
  offending path.

## Constraints & Invariants
- **CON-001**: The implementation MUST be pure — no filesystem access, no network, no subprocess,
  and no reading of the clock. Everything it needs is in its two arguments. Determinism is what
  lets a wrapper run this on every commit and lets this oracle judge it.
- **CON-002**: `index` and `tree`, and the dicts inside them, MUST NOT be mutated.

## Acceptance
All fail_to_pass tests newly pass; all pass_to_pass tests still pass; lint (ruff F,S) and type
(basedpyright standard) and coverage per the pinned pack.
