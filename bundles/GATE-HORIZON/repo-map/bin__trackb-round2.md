# bin/trackb-round2
Purpose: Executes three sequential 10-task reasoning batches for Track B round 2 to generate rate estimates with error bars and bounded wall-clock timing.
Key functions or classes: None defined; invokes `./bin/trackb-run` and shell built-ins `date` and `echo`.
Direct imports/dependencies: Bash runtime (`set -uo pipefail`), GNU `date` formatting, hardcoded path `/home/kalib/foundry`.
Obvious risk: `set -uo pipefail` will abruptly terminate on unset variables or pipeline failures without cleanup, and the fixed directory assumption breaks environment portability.
