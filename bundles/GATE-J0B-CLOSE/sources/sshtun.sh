#!/bin/bash
# GATE-J0B-CLOSE — the pinhole, carried inside the EXISTING authenticated ssh channel instead of
# over the SLIRP guestfwd. `-R` opens a listener IN THE GUEST on 18081 that forwards to the host's
# 127.0.0.1:8081. The guest's own egress stays restrict=on; nothing is added to its IP stack except
# a loopback listener, and the carrier is the ssh connection the gate already has.
exec ssh -N -p 2222 -i /var/lib/wrought/j0a/j0a_key \
  -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
  -o BatchMode=yes -o ExitOnForwardFailure=yes -o LogLevel=ERROR \
  -R 18081:127.0.0.1:8081 probe@127.0.0.1
