# bin/gate19-fresh
Purpose: Gates MTP promotion by comparing fresh-process baseline and MTP runs on token identity, wall-clock latency, and acceptance rates, outputting a verdict without auto-flipping active-profile.
Key Functions: first_req
Dependencies: $CONF, $LLAMA, curl, python3 (json, sys), bc, ldd, strings, kill
Risks: Fragile backend detection via strings/ldd output parsing, unhandled process cleanup (kill $pid), hardcoded port 8096, and inline Python lacking JSON load error handling.
