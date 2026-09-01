# src/wrought_escalation/client.py
Purpose: Stdlib-only HTTP client enforcing strict backend routing, explicit cache-off policy, and separated connect/stall/TTFT/total-generation timeouts for escalation API calls.
Key functions/classes: `EscalationTimeout`, `ProviderError`, `_connection_factory`, `build_request_body`, `_extract_usage`, and `call`.
Direct dependencies: `http.client`, `json`, `time`, `urllib.error`, and `urllib.request`.
Risk: Mid-stream `TimeoutError` creates unknown billing liabilities (STOP-29a), and the transport assumes external ledger reservation, risking budget bypass if callers neglect pre-call checks.
