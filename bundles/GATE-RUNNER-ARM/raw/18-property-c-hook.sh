#!/bin/bash
cat >> "$HOOKMARKER"
echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"GATE-RUNNER-ARM property (c) probe"}}'
