# bin/secpack-fetch
Purpose: Fetches and pins stable security tools, computing separate archive and binary SHA256 hashes while explicitly separating integrity checks from authenticity verification.
Key functions: fetch_go_tool, say, sha
Dependencies: curl, sha256sum, tar, awk, /opt/wrought/venv-orch/bin/python, gh
Risk: Relies on integrity-only upstream checksums without cryptographic signature verification, and performs blind tar extraction into bin/ without path validation, creating documented authenticity gaps and potential zip-slip exposure.
