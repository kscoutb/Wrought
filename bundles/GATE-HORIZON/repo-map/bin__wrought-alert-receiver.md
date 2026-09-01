# bin/wrought-alert-receiver
Purpose: Local-only webhook receiver for Alertmanager that routes notifications to systemd journal and a persistent plain-text log.
Key functions/classes: main, journal_send, handle_payload, Handler, Server.
Direct imports/dependencies: http.server, socket, socketserver, json, pathlib, sys, time, and the JOURNAL_SOCKET constant.
Risks: The Handler class exposes an unauthenticated HTTP endpoint; journal_send silently swallows OSError exceptions, potentially dropping journal records; the LOG file lacks built-in rotation or explicit permission enforcement.
