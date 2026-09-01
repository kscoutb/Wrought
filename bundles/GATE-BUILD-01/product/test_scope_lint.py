# tests/test_scope_lint.py -- THE ORACLE for TASK-2026-0901-scope-lint.
#
# PROVENANCE, STATED UP FRONT BECAUSE IT IS THE WEAKEST THING ABOUT THIS FILE AND THE SAME
# QUESTION IS ALREADY OPEN AGAINST products/queue-health/MANIFEST.json:
# these tests were authored by the GATE-BUILD-01 session, i.e. by a model, and the spec they grade
# was authored by the same session. What they are NOT is authored by the thing being graded: the
# candidate `scope_lint.py` is written by the resident Qwen3.6-27B, in another process, from the
# TASK.md text alone, with no sight of this file. That is the separation this probe needs and it is
# the one it has. It is NOT operator ratification, and D11 makes ratification the operator's.
#
# The values below were re-derived here rather than copied from the spec prose: the severity
# ordering, the bool-is-not-an-int boundary, and the exact-64-lowercase-hex rule are each asserted
# against a case the requirement text does not spell out.
import copy
import time as _time

import pytest
from scope_lint import lint_index

A = "a" * 64
B = "b" * 64
C = "c" * 64


def _index(**files):
    return {"files": {p: dict(rec) for p, rec in files.items()}}


def _rec(sha=A, tokens=100):
    return {"sha256": sha, "tokens": tokens, "purpose": "irrelevant to this function"}


def test_module_surface():
    assert callable(lint_index)


def test_clean_index():
    idx = _index(**{"bin/a": _rec(A), "src/b.py": _rec(B, 7)})
    r = lint_index(idx, {"bin/a": A, "src/b.py": B})
    assert r["findings"] == []
    assert r["worst_severity"] == "none"
    assert r["counts"] == {}


def test_missing_from_index():
    r = lint_index(_index(**{"bin/a": _rec(A)}), {"bin/a": A, "bin/new": C})
    assert [f["kind"] for f in r["findings"]] == ["MISSING_FROM_INDEX"]
    f = r["findings"][0]
    assert f["severity"] == "high" and f["path"] == "bin/new"
    assert r["worst_severity"] == "high"


def test_absent_from_tree():
    r = lint_index(_index(**{"bin/a": _rec(A), "bin/gone": _rec(B)}), {"bin/a": A})
    assert [f["kind"] for f in r["findings"]] == ["ABSENT_FROM_TREE"]
    assert r["findings"][0]["path"] == "bin/gone"
    assert r["findings"][0]["severity"] == "high"


def test_stale_hash():
    r = lint_index(_index(**{"bin/a": _rec(A)}), {"bin/a": B})
    assert [f["kind"] for f in r["findings"]] == ["STALE_HASH"]
    assert r["findings"][0]["severity"] == "high"
    # identical digests are NOT stale -- the negative half of the same boundary
    assert lint_index(_index(**{"bin/a": _rec(A)}), {"bin/a": A})["findings"] == []


@pytest.mark.parametrize("tokens", [None, "100", 1.5, -1, True, False])
def test_bad_token_count(tokens):
    rec = _rec(A)
    if tokens is None:
        del rec["tokens"]
    else:
        rec["tokens"] = tokens
    r = lint_index({"files": {"bin/a": rec}}, {"bin/a": A})
    assert [f["kind"] for f in r["findings"]] == ["BAD_TOKEN_COUNT"], tokens
    assert r["findings"][0]["severity"] == "medium"
    assert r["worst_severity"] == "medium"


def test_zero_tokens_is_valid():
    # an empty file measures zero tokens; zero is a real answer, not a missing one
    r = lint_index(_index(**{"bin/empty": _rec(A, 0)}), {"bin/empty": A})
    assert r["findings"] == []


def test_multiple_findings_per_path():
    # a path that is BOTH stale and carries a bad token count must surface both (REQ-006)
    rec = {"sha256": A, "tokens": -3}
    r = lint_index({"files": {"bin/a": rec}}, {"bin/a": B})
    assert {f["kind"] for f in r["findings"]} == {"STALE_HASH", "BAD_TOKEN_COUNT"}
    assert r["worst_severity"] == "high"
    assert r["counts"] == {"STALE_HASH": 1, "BAD_TOKEN_COUNT": 1}


def test_deterministic_sort_and_counts():
    idx = {"files": {
        "bin/zz": _rec(A),                    # STALE_HASH   (high)
        "bin/aa": {"sha256": B, "tokens": -1},  # BAD_TOKEN_COUNT (medium)
        "src/gone.py": _rec(C),               # ABSENT_FROM_TREE (high)
    }}
    tree = {"bin/zz": B, "bin/aa": B, "bin/absent-here": C}
    r = lint_index(idx, tree)
    order = [(f["severity"], f["path"], f["kind"]) for f in r["findings"]]
    assert order == [
        ("high", "bin/absent-here", "MISSING_FROM_INDEX"),
        ("high", "bin/zz", "STALE_HASH"),
        ("high", "src/gone.py", "ABSENT_FROM_TREE"),
        ("medium", "bin/aa", "BAD_TOKEN_COUNT"),
    ]
    assert r["counts"] == {"MISSING_FROM_INDEX": 1, "STALE_HASH": 1,
                           "ABSENT_FROM_TREE": 1, "BAD_TOKEN_COUNT": 1}
    assert r["worst_severity"] == "high"
    # byte-identical for identical input
    assert lint_index(idx, tree) == r


@pytest.mark.parametrize("idx,tree", [
    ("not a dict", {}),
    ({}, {}),
    ({"files": []}, {}),
    ({"files": {}}, "not a dict"),
])
def test_structural_malformed_raises(idx, tree):
    with pytest.raises(ValueError):
        lint_index(idx, tree)


@pytest.mark.parametrize("sha", [
    None, 123, "", "z" * 64, A.upper(), A[:63], A + "a",
])
def test_bad_sha_raises_names_path(sha):
    rec = _rec(A)
    if sha is None:
        del rec["sha256"]
    else:
        rec["sha256"] = sha
    with pytest.raises(ValueError) as e:
        lint_index({"files": {"bin/offender": rec}}, {"bin/offender": A})
    assert "bin/offender" in str(e.value)


def test_bad_tree_value_raises_names_path():
    with pytest.raises(ValueError) as e:
        lint_index(_index(**{"bin/a": _rec(A)}), {"bin/a": "nope"})
    assert "bin/a" in str(e.value)


def test_record_not_a_dict_raises_names_path():
    with pytest.raises(ValueError) as e:
        lint_index({"files": {"bin/a": "not a record"}}, {"bin/a": A})
    assert "bin/a" in str(e.value)


def test_no_io_and_no_clock(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("scope_lint reached outside its arguments")
    monkeypatch.setattr(_time, "time", boom)
    monkeypatch.setattr(_time, "monotonic", boom)
    monkeypatch.setattr("builtins.open", boom)
    lint_index(_index(**{"bin/a": _rec(A)}), {"bin/a": B})


def test_inputs_not_mutated():
    idx = {"files": {"bin/a": _rec(A), "bin/b": {"sha256": B, "tokens": -1}}}
    tree = {"bin/a": C, "bin/extra": B}
    si, st = copy.deepcopy(idx), copy.deepcopy(tree)
    lint_index(idx, tree)
    assert idx == si
    assert tree == st
