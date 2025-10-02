# CLAUDE.md — Python Node Dev Guide

## 🎯 Project Context

This is a **standalone Python MQTT node** for a robot stack. It's designed to:

- Run as an independent process (systemd service or Docker container)
- Communicate via MQTT broker (`MQTT_URL` environment variable)
- Build for multiple platforms: Pi 4/5, Jetson, x86_64, Docker
- Be deployed and managed by the parent stack's `manifest.yaml`

**Key principle**: This repo is self-contained. The stack repo orchestrates deployment, but all application logic and dependencies live here.

## 🧠 What this node does

- Starts via `venv/bin/python app.py`
- Reads configuration from environment variables
- Publishes/subscribes on MQTT (broker specified by `MQTT_URL`)
- Logs to stdout/stderr (captured by systemd/Docker)
- Exits non-zero on unrecoverable errors

## 📦 Layout

```

.
├── app.py                 # main entrypoint
├── requirements.txt       # default deps
├── requirements-jetson.txt# optional Jetson-specific wheels
├── Makefile               # build targets (pi5/jetson/amd64/docker)
└── Dockerfile.docker      # container build recipe

```

## 🔧 Build targets

```bash
make build-pi       # Raspberry Pi 4 (arm64)
make build-pi5      # Raspberry Pi 5 (arm64)
make build-jetson   # Jetson (arm64, CUDA-friendly wheels)
make build-amd64    # Desktop dev (x86_64)
make build-docker   # Prepare Dockerfile for Compose builds
````

* Creates a local virtualenv at `venv/`
* Installs `requirements.txt` (or `requirements-jetson.txt` on Jetson)

## ▶️ Run locally

Native (uses local broker or what you set via env):

```bash
make build-amd64
MQTT_URL=tcp://localhost:1883 TOPIC=robot/demo venv/bin/python app.py
```

Inside Docker (Compose):

* Ensure the stack repo generated `docker-compose.yml` pointing to `Dockerfile.docker`.
* Run from the **stack** repo: `docker compose up --build`.

## 🌐 Environment variables

* `MQTT_URL` (default for Compose: `tcp://mqtt:1883`; native default often `tcp://127.0.0.1:1883`)
* Any node-specific env (document them here), e.g.:

  * `TOPIC` — topic to publish (default: `robot/demo`)
  * `LOG_LEVEL` — `DEBUG|INFO|WARN|ERROR` (optional)

## 🧪 Tests (suggested)

* Add `tests/` with pytest:

  * unit tests for message formatting
  * integration test using a local Mosquitto (`docker run -p 1883:1883 eclipse-mosquitto:2`)

Example `tests/test_msg.py`:

```python
def test_payload_fields():
    import json, time
    msg = {"seq": 1, "ts": time.time()}
    s = json.dumps(msg)
    d = json.loads(s)
    assert "seq" in d and "ts" in d
```

Run:

```bash
venv/bin/pip install pytest
venv/bin/pytest -q
```

## 🐳 Docker

Minimal `Dockerfile.docker` (provided):

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements*.txt ./
RUN pip install -r requirements.txt || true \
 && if [ -f requirements-jetson.txt ]; then pip install -r requirements-jetson.txt || true; fi
COPY . .
CMD ["python", "app.py"]
```

* Compose will build using this file.
* The stack’s generator forces `MQTT_URL=tcp://mqtt:1883` inside Compose.

## 🧰 Debugging

* Tail logs (Compose): `docker compose logs -f <service>`
* Tail logs (systemd): `journalctl -u <node>.service -f`
* Quick MQTT sanity:

  ```bash
  mosquitto_sub -h localhost -t '#' -v
  ```

## 🚀 Deploy expectations

* In `manifest.yaml` (stack repo):

  ```yaml
  - name: your-python-node
    repo: https://github.com/YOU/your-python-node.git
    ref: main
    workdir: .
    exec: venv/bin/python app.py
    build:
      pi:     ["make","build-pi"]
      pi5:    ["make","build-pi5"]
      jetson: ["make","build-jetson"]
      amd64:  ["make","build-amd64"]
      docker: ["make","build-docker"]
  ```

## 🧪 Health checks (optional)

* Publish liveness to `robot/status/<name>` periodically.
* Exit non-zero if critical dependencies fail (stack restarts you).

---

## 🤖 Development Workflow (Claude Code)

### Common Tasks

**Building for local testing:**
```bash
make build-amd64                    # Create venv and install deps
MQTT_URL=tcp://localhost:1883 venv/bin/python app.py  # Run
```

**Testing with Docker Compose:**
1. Return to the parent stack repo
2. Regenerate compose: `python3 tools/stack.py gen-compose --profile dev-amd64`
3. Run: `docker compose up --build`
4. Check logs: `docker compose logs -f <service-name>`

**Adding Python dependencies:**
1. Add package to `requirements.txt`
2. Rebuild venv: `make build-amd64`
3. For Jetson-specific packages (e.g., CUDA libs), add to `requirements-jetson.txt`
4. Test locally, then test in Docker

**Adding new Python modules:**
1. Create `.py` files alongside `app.py` or in subdirectories
2. Import in `app.py` as needed
3. Test with `venv/bin/python app.py`
4. No build configuration needed (Python is interpreted)

**Running tests:**
```bash
# Add pytest to requirements.txt first
venv/bin/pip install pytest
venv/bin/pytest -v
```

**Debugging runtime issues:**
```bash
# Verbose logging
LOG_LEVEL=DEBUG MQTT_URL=tcp://localhost:1883 venv/bin/python app.py

# Interactive debugging
venv/bin/python -m pdb app.py

# Check dependency versions
venv/bin/pip list
```

### File Reference

| File | Purpose |
|------|---------|
| `app.py` | Main entry point - start here for logic changes |
| `requirements.txt` | Python dependencies - add packages here |
| `requirements-jetson.txt` | Jetson-specific wheels (optional) |
| `Makefile` | Build targets for different platforms - rarely modified |
| `Dockerfile.docker` | Container build recipe - update for system packages |

### Integration with Stack

This node is referenced in the parent stack's `manifest.yaml`:

```yaml
- name: <repo-name>
  repo: https://github.com/YOU/<repo-name>.git
  ref: main
  workdir: .
  exec: venv/bin/python app.py
  build:
    pi5:    ["make","build-pi5"]
    amd64:  ["make","build-amd64"]
    docker: ["make","build-docker"]
```

After making changes:
1. Commit and push this repo
2. In the stack repo, run `sudo python3 tools/stack.py update --profile <profile>` to pull and rebuild

### Best Practices

- **Keep repo name simple** - no spaces, use hyphens (e.g., `motor-controller`)
- **Log to stdout/stderr only** - use `print()` or `logging` module; systemd and Docker capture output
- **Exit cleanly** - use `sys.exit(1)` for errors, `sys.exit(0)` for success (triggers systemd restart on failure)
- **Read config from environment** - use `os.environ.get('MQTT_URL')` etc., don't hardcode
- **Pin major versions in requirements.txt** - e.g., `paho-mqtt>=2.0,<3.0` for stability
- **Test locally before Docker** - faster iteration with native venv
- **Use type hints** - improves code clarity and catches errors with mypy
- **Handle MQTT reconnection** - broker may restart, implement retry logic
