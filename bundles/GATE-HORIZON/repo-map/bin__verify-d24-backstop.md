# bin/verify-d24-backstop
Purpose: Read-only verification script that validates security acceptance D24 by comparing local ledger spend against OpenRouter API provider usage and enforcing a $50 exposure ceiling.
Key functions/classes: read_key, get, ledger_spend, main
Direct imports/dependencies: json, subprocess, sys, urllib.error, urllib.request, sqlite3
Obvious risk: The auto-top-up control is explicitly marked [UNVERIFIED] by the API and relies on operator assertion; credential extraction depends on sudo -n systemd-creds decrypt, and any provider-ledger usage mismatch immediately voids the security premise.
