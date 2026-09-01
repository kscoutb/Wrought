# bin/gate21-bwrap-smoke
Purpose: Validates that `bwrap` sandboxes correctly resolve merged-/usr symlinks for `/bin`, `/lib`, and `/sbin` while executing `python3.14` with required imports and isolated networking.
Key function: `check`
Dependencies: `bwrap`, `python3.14`, `ssl`, `secrets`, `multiprocessing`, `socket`, `os`
Risk: Deliberately omits seccomp filtering (`seccomp-deny.bpf`) and relies entirely on `bwrap` namespace isolation, making execution vulnerable to host symlink misconfigurations or `bwrap` bug #686.
