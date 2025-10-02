# Robot Stack Template 🚀

A lightweight, ROS-free framework for orchestrating multi-node robotic systems across Raspberry Pi, Jetson, and desktop Linux.

Nodes live in separate Git repositories. This stack repo declaratively installs, updates, builds, and runs them natively (systemd) on robots and via Docker Compose for desktop integration tests.

---

## 📖 Documentation

- [Quickstart](docs/quickstart.md)
- [Node Contract](docs/node_contract.md)
- [IPC Conventions](docs/ipc_conventions.md)
- [Profiles](docs/profiles.md)
- [Operations & Updates](docs/ops.md)
- [Time Synchronization](docs/time.md)
- [Adding a New Node](docs/new_node.md)
- [Integration Testing](docs/integration_testing.md)
- [Security Guide](docs/security.md)
- [Contributing Guide](docs/contributing.md)

---

## ✨ Features

- **Manifest-driven** stack definition
- **Systemd runtime** for SBCs (Pi/Jetson/NUC)
- **Docker Compose runtime** for integration tests
- **Language-agnostic nodes** via `make build-*`
- **Idempotent updates** (only restarts changed services)
- **Lockfile support** for reproducible deployments
- **Health checks** and auto-update timers
- **Simulators** for integration testing
- **Secure by default** (local broker, non-root users)

---

## 🚀 Quick Start

### Robot (native)
```bash
sudo apt-get update && sudo apt-get install -y git python3-yaml python3-jinja2
git clone https://github.com/YOURNAME/robot-stack-template.git /opt/robot-stack
cd /opt/robot-stack
sudo python3 tools/stack.py apply-native --profile pi4
````

### Dev desktop (docker)

```bash
python3 tools/stack.py gen-compose --profile dev-amd64
docker compose up --build
```

---

## 🛠️ Create a New Stack from this Template

1. Click **Use this template** on GitHub.
2. Clone locally and run `scripts/bootstrap.sh my-robot-stack`.
3. Scaffold a node with `scripts/new-node.sh python my-node`.
4. Add it to `manifest.yaml`.
5. Apply and test.

---

## 📜 License

MIT – see [LICENSE](LICENSE).
