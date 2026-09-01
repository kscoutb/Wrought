# src/wrought_orchestrator/redact.py
Purpose: Implements pre-persistence secret redaction (§14.4) that scans text for provider prefixes and high-entropy tokens, replacing matches with SHA-256 correlators before event logging.
Key functions/classes: `redact`, `redact_obj`, `_tag`, `shannon_bits_per_char`, `_fenced_spans`, `_in_fence`.
Direct imports/dependencies: `__future__.annotations`, `hashlib`, `math`, `re`.
Obvious risk: Documented spec defects allow hyphenated vendor keys and hexadecimal secrets to bypass the entropy screen (strict `>4.0` threshold) and original regexes, leaving prefix matching as a fragile single point of failure.
