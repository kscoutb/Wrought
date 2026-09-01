# bin/gate-review-send-panel
Purpose: Dispatches a security review packet to an independent LLM panel via OpenRouter, enforcing Zero-Data-Retention models and a hard `CEILING_USD` budget while saving structured results.
Key functions: `key()`, `get_json()`, `read()`, `build_user_message()`, `main()`
Direct imports: `json`, `os`, `pathlib`, `sys`, `time`, `urllib.request`, `urllib.error`
Obvious risk: Hard dependency on `$CREDENTIALS_DIRECTORY` and systemd `LoadCredentialEncrypted` causes immediate `SystemExit` if misconfigured; relies on external OpenRouter pricing/metadata endpoints and network stability, with a rigid budget check that may prematurely skip models if API rates change.
