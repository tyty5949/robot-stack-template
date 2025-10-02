# Node Contract

Each node lives in its own repo and exposes Make targets:

- `build-pi` - produce the native artifact (binary or venv)
- `build-amd64` - same for desktop
- `build-docker` - prepare a `Dockerfile` at repo root for Compose

Your stack manifest references:
- `workdir` - path where builds run (relative to repo root)
- `exec` - command to run the node in native/systemd (relative to workdir)
- `env` - environment variables passed to the service
