# bin/reclassify-corpus
Purpose: Re-runs the shipped classifier over stored Track-B attempt records to diff against originally saved classifications and verify a historical re-baselining claim.
Key functions/classes: main, classify
Direct imports/dependencies: argparse, collections, glob, json, pathlib, sys, wrought_supervisor.classify
Obvious risk: Hardcoded absolute JOB_ROOT path (/var/lib/wrought/jobs) and sys.path.insert(0, ...) mutation break portability and risk import shadowing.
