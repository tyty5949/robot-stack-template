# Robot Stack Template 🚀

A lightweight, ROS-free framework for orchestrating multi-node robotic systems across Raspberry Pi, Jetson, and desktop Linux.
Nodes live in separate Git repositories; this stack repo declaratively installs, updates, builds, and runs them natively
(systemd) on robots and via Docker Compose for desktop integration tests.

## Features
- Manifest-driven nodes, profiles, and environments
- Native runtime with systemd (Pi/Jetson/x86)
- Docker Compose generation for integration tests
- Multi-language node contract via `make build-<platform>`
- Idempotent updates with code/unit change detection
- Optional lockfile to pin exact SHAs for deployments

## Quick start (robot)
```bash
sudo apt-get update && sudo apt-get install -y git python3-yaml python3-jinja2
git clone https://github.com/YOURNAME/robot-stack-template.git /opt/robot-stack
cd /opt/robot-stack
sudo python3 tools/stack.py apply-native --profile pi4
```

## Quick start (dev desktop)
```bash
python3 tools/stack.py gen-compose --profile dev-amd64
docker compose up --build
```

## Layout
- `manifest.yaml` – nodes, repos, execs, default env.
- `profiles/` – per-hardware overrides (pi4, dev-amd64, ...).
- `system/` – service templates, timers, udev rules.
- `tools/` – controller CLI `stack.py`.
- `broker/` – Mosquitto defaults.
- `docker/` – compose template & overrides.
- `docs/` – how-tos and conventions.
- `scripts/` – bootstrap, scaffolding, health checks.
- `examples/` – tiny Python and C++ nodes you can clone into separate repos.

## Create a new stack from this template
1. Click **Use this template** on GitHub and create your new repo.
2. Clone it locally and run `scripts/bootstrap.sh <your-stack-name>` to rename references.
3. Scaffold your first node with `scripts/new-node.sh python motor-node` (creates a local repo folder you can push).
4. Edit `manifest.yaml` to include your node’s repo URL and build targets.
5. Run `tools/stack.py apply-native --profile pi4` (on robot) or `gen-compose` on desktop.

## License
MIT
