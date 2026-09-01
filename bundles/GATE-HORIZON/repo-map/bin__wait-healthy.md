# bin/wait-healthy
Purpose: Polls the llama-server health endpoint until HTTP 200 is received or TIMEOUT expires, enabling systemd ExecStartPost to defer startup until the model is resident.
Key functions or classes: None defined; executes as a top-level bash script with inline control flow.
Direct imports/dependencies: curl, sleep, WROUGHT_CONF, WROUGHT_HOST, WROUGHT_PORT, CREDENTIALS_DIRECTORY, inference-api-key.
Obvious risks: curl network failures silently yield 000 and retry, masking infrastructure outages as health timeouts; credentials are injected via cat into command-line arguments, risking exposure in process listings.
