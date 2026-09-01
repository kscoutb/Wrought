"""Scope lint module for detecting drift between a scoping index and the file tree."""

from typing import Any


def _is_valid_sha256(value: Any) -> bool:
    """Check whether *value* is a valid 64-character lowercase hexadecimal sha256 digest."""
    if not isinstance(value, str):
        return False
    if len(value) != 64:
        return False
    return all(c in "0123456789abcdef" for c in value)


def lint_index(index: dict, tree: dict[str, str]) -> dict:
    """Check a context-scoping index against the file tree and report every drift.

    Compares ``index["files"]`` against ``tree``, emitting findings for missing
    files, absent files, stale hashes, and invalid token counts.

    Args:
        index: Parsed scoping index. Must contain a ``"files"`` key mapping
               repository-relative paths to record dicts with at least
               ``"sha256"`` and ``"tokens"`` fields.
        tree: Dict mapping repository-relative paths to the current sha256
              digest for every file that should be indexed.

    Returns:
        A dict with three keys:

        * ``findings`` – list of finding dicts, each carrying at least
          ``kind``, ``severity``, and ``path``.
        * ``counts`` – mapping of finding ``kind`` to occurrence count
          (only kinds that occurred).
        * ``worst_severity`` – ``"high"``, ``"medium"``, or ``"none"``.

    Raises:
        ValueError: If the structural preconditions on *index* or *tree* are
                    violated, or if any record / tree value carries an invalid
                    sha256 digest.
    """
    # --- structural validation (REQ-008) -----------------------------------
    if not isinstance(index, dict):
        raise ValueError("index must be a dict")
    if "files" not in index:
        raise ValueError("index must contain a 'files' key")
    if not isinstance(tree, dict):
        raise ValueError("tree must be a dict")

    index_files = index["files"]
    if not isinstance(index_files, dict):
        raise ValueError("index['files'] must be a dict")

    # Validate every record and its corresponding tree value.
    for path, record in index_files.items():
        if not isinstance(record, dict):
            raise ValueError(f"Record for path '{path}' is not a dict")
        if "sha256" not in record:
            raise ValueError(f"Record for path '{path}' is missing 'sha256'")
        sha = record["sha256"]
        if not isinstance(sha, str):
            raise ValueError(f"sha256 for path '{path}' is not a string")
        if not _is_valid_sha256(sha):
            raise ValueError(
                f"sha256 for path '{path}' is not a valid 64-char lowercase hex string"
            )
        if path in tree:
            tree_val = tree[path]
            if not _is_valid_sha256(tree_val):
                raise ValueError(
                    f"tree value for path '{path}' is not a valid sha256 string"
                )

    # --- drift detection ---------------------------------------------------
    findings: list[dict] = []

    index_paths = set(index_files.keys())
    tree_paths = set(tree.keys())

    # REQ-002: present in tree but absent from index
    for path in tree_paths - index_paths:
        findings.append({
            "kind": "MISSING_FROM_INDEX",
            "severity": "high",
            "path": path,
        })

    # REQ-003: present in index but absent from tree
    for path in index_paths - tree_paths:
        findings.append({
            "kind": "ABSENT_FROM_TREE",
            "severity": "high",
            "path": path,
        })

    # REQ-004 / REQ-005: present in both
    for path in index_paths & tree_paths:
        record = index_files[path]

        # REQ-004: stale hash
        if record["sha256"] != tree[path]:
            findings.append({
                "kind": "STALE_HASH",
                "severity": "high",
                "path": path,
            })

        # REQ-005: bad token count
        tokens = record.get("tokens")
        if (
            tokens is None
            or isinstance(tokens, bool)
            or not isinstance(tokens, int)
            or tokens < 0
        ):
            findings.append({
                "kind": "BAD_TOKEN_COUNT",
                "severity": "medium",
                "path": path,
            })

    # --- sort (REQ-007) ----------------------------------------------------
    severity_order: dict[str, int] = {"high": 0, "medium": 1}
    findings.sort(
        key=lambda f: (severity_order[f["severity"]], f["path"], f["kind"])
    )

    # --- counts & worst severity (REQ-007) ---------------------------------
    counts: dict[str, int] = {}
    for f in findings:
        kind = f["kind"]
        counts[kind] = counts.get(kind, 0) + 1

    if any(f["severity"] == "high" for f in findings):
        worst_severity = "high"
    elif any(f["severity"] == "medium" for f in findings):
        worst_severity = "medium"
    else:
        worst_severity = "none"

    return {
        "findings": findings,
        "counts": counts,
        "worst_severity": worst_severity,
    }
