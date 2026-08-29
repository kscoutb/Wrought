#!/bin/bash
# GATE-J0B-CLOSE — the interception tee shim, on goose's OWN stdio-MCP path.
# Both directions are captured verbatim; the shim itself is unprivileged and two live lines.
exec 2>>/home/probe/mcp-tee.err
tee -a /home/probe/mcp-in.jsonl | goose mcp memory | tee -a /home/probe/mcp-out.jsonl
