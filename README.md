# Robot Stack Template 🚀

A lightweight, ROS-free framework for running multi-node robotic systems across Raspberry Pi, Jetson, and desktop Linux.  
Nodes are separate Git repos; this repo ties them together declaratively.

## Features
- **Manifest-driven**: declare nodes, repos, builds, env.
- **Systemd runtime**: services on SBCs (Pi, Jetson, NUC, etc.).
- **Docker runtime**: integration testing on desktop.
- **Language agnostic**: each node repo defines `make build-<platform>`.
- **Idempotent updates**: re-run to pull new code, rebuild, and restart only changed services.

## Quick start

### On robot (Pi/Jetson)
```bash
sudo apt-get update && sudo apt-get install -y git python3-yaml python3-jinja2
git clone https://github.com/YOURNAME/robot-stack-template.git /opt/robot-stack
cd /opt/robot-stack
sudo python3 tools/stack.py apply-native --profile pi4
```

### On dev machine (integration via Docker)
```bash
cd robot-stack
python3 tools/stack.py gen-compose --profile dev-amd64
docker compose up --build
```

## Structure
- `manifest.yaml` - declarative node + profile definitions.
- `profiles/` - per-hardware overrides (Pi4, Jetson, amd64).
- `system/` - service templates (systemd by default).
- `tools/stack.py` - controller CLI (install, update, generate compose).
- `broker/` - default Mosquitto config.
- `docker/` - compose template for dev integration.

## Adding a new node
1. Create a new Git repo for your node (C++, Python, Rust, Go...).
1. Add a Makefile with `build-pi`, `build-amd64`, and `build-docker` targets.
1. Update `manifest.yaml` with the repo URL and build instructions.
1. Run `stack.py apply-native` (on robot) or `gen-compose` (on dev).
