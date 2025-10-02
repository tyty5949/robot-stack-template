# Quickstart

This guide walks you through getting the stack running on **a robot (Pi/Jetson)** and on **a dev desktop (Docker)**.

---

## Robot (native/systemd)

1. Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y git python3-yaml python3-jinja2 make gcc g++
   ```
1. Clone the stack:
   ```bash
   git clone https://github.com/YOURNAME/my-robot-stack.git /opt/robot-stack
   cd /opt/robot-stack
   ```
1. Apply the stack (installs broker + systemd units + nodes):
   ```bash
   sudo python3 tools/stack.py apply-native --profile pi4
   ```
1. Check services:
   ```
   systemctl status motor.service
   systemctl status planner.service
   ```

---

## Desktop (integration via Docker)

1. Ensure Docker + Compose are installed:
   ```bash
   docker --version
   docker compose version
   ```
1. Generate docker-compose:
   ```bash
   python3 tools/stack.py gen-compose --profile dev-amd64
   ```
1. Run it:
   ```bash
   docker compose up --build
   ```
1. Observe logs:
   ```bash
   docker compose logs -f
   ```

---

## Next Steps

- [Add a new node](node_contract.md)
- [Understand MQQT topic conventions](ipc_conventions.md)
- [Operational guide](ops.md)
