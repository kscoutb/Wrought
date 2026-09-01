# bin/test-f4-allowed-tools
Purpose: Validates that validate_allowed_tools correctly parses tool allowlists, halting on unsafe bare Bash entries while permitting properly scoped tools.
Key functions/classes: validate_allowed_tools, Halt, spec_from_loader, SourceFileLoader, module_from_spec, exec_module, fullmatch.
Direct imports: importlib.machinery, importlib.util, pathlib, re, sys.
Risk: Dynamically executes wrought-runner via spec.loader.exec_module, posing a code execution risk if the target path is altered or points to untrusted code.
