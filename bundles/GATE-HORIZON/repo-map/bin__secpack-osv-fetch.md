# bin/secpack-osv-fetch
Purpose: Fetches and pins the `osv-scanner` raw ELF binary and offline vulnerability databases for `§10.6 vuln-scan slot`, recording integrity hashes and partial SLSA attestation claims.
Key functions: `get`, `sha256_file`, `_snapshot_span`, `pae`, `verify_attestation`, `main`.
Direct imports: `argparse`, `base64`, `email.utils`, `hashlib`, `json`, `os`, `pathlib`, `subprocess`, `sys`, `urllib.parse`, `urllib.request`.
Risk: Explicitly skips Rekor/Fulcio chain verification (`no cosign/slsa-verifier`), relies on unpinned external CLIs (`openssl`, `date`), and fetches `releases/latest` from GitHub without static version pinning.
