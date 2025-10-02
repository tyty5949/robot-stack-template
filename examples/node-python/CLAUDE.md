# CLAUDE.md — Python Node Dev Guide

This repo is a template for a **Python MQTT node** in the robot stack.

## 🧠 What this node is expected to do

- Start via `venv/bin/python app.py`
- Read configuration from environment variables
- Publish/subscribe on MQTT (default: `MQTT_URL`)
- Log to stdout/stderr (systemd/Docker collect logs)
- Exit non-zero on unrecoverable errors

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
