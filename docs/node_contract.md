# Node Contract

Every node must follow these rules to integrate cleanly with the stack.

---

## Repository Layout

Each node lives in its own Git repository.  
At minimum:

```
my-node/
├── Makefile
├── Dockerfile.docker
├── src/...
└── README.md
```


---

## Required Make Targets

- `make build-pi` → builds for Raspberry Pi (arm64)  
- `make build-amd64` → builds for dev desktop (amd64)  
- `make build-docker` → prepares a Dockerfile for Compose builds  

> Each build should place binaries, virtualenvs, or launchable scripts in a predictable location (e.g. `build/` or `venv/`).

---

## Execution Contract

The stack’s `manifest.yaml` defines how a node is launched:

```yaml
- name: planner
  repo: https://github.com/YOURNAME/planner-node.git
  exec: venv/bin/python planner.py
  workdir: .
  build:
    pi: ["make","build-pi"]
    amd64: ["make","build-amd64"]
    docker:["make","build-docker"]
```

- **exec** → relative to `workdir` inside the repo clone.
- **env** → environment variables injected into the process.
- **logs** → all output goes to stdout/stderr (captured by systemd or Docker).

---

## Language Examples

- **Python node**
    - `Makefile` creates a venv and installs deps.
    - `exec` points to `venv/bin/python app.py`.
- **C++ node**
    - `Makefile` calls `cmake` → builds binary in `build/`.
    - `exec` points to `build/my_node`.
- **Rust/Go node**
    - Same idea: `cargo build --release` / `go build`.
