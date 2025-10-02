## 🤖 Purpose

This file collects **common development tasks** you’ll use when working with the robot stack template:

* Scaffolding new nodes (Python, C++)
* Building and testing nodes locally
* Running integration tests with Docker Compose
* Deploying/updating on Raspberry Pi / Jetson
* Day-to-day developer workflows

Think of this as your **“cheat sheet”**.

---

## 📋 Understanding manifest.yaml

The `manifest.yaml` file is the **single source of truth** for your robot stack. It defines:

* What nodes run on your robot
* Where each node's code lives (Git repos)
* How to build each node for different platforms
* Environment configuration (MQTT broker, URLs)
* Deployment profiles for different robots/scenarios

### Structure

**`stack_root`**: Base directory where everything gets deployed (e.g., `/opt/robot`)

**`ipc`**: Message broker configuration
* `adapter`: Protocol type (e.g., `mqtt`)
* `broker.type`: Broker implementation (`mosquitto` or `docker` for Compose)
* `broker.conf`: Path to broker config file

**`defaults`**: Common settings applied to all nodes
* `user`: System user to run services as
* `unit`: systemd unit defaults (`after`, `restart` policy)
* `env`: Environment variables (e.g., `MQTT_URL`)

**`nodes`**: List of all available nodes in your stack
* `name`: Node identifier (used for systemd service names)
* `repo`: Git repository URL
* `ref`: Branch/tag to check out
* `workdir`: Working directory inside the cloned repo
* `exec`: Command to run the node
* `build`: Build commands per platform (`pi`, `pi5`, `amd64`, `jetson`, `docker`)

**`profiles`**: Deployment configurations that specify which nodes to run and how
* Each profile can override `ipc` settings
* Lists which nodes to include
* Specifies which build variant to use (e.g., `build: { use: pi5 }`)

### Example Workflow

1. Define all your nodes in the `nodes` section
2. Create profiles for different robots (e.g., `pi4`, `pi5`, `jetson`)
3. Use profiles for Docker testing (`dev-amd64`) or production deployment
4. Generate Docker Compose: `python3 tools/stack.py gen-compose --profile dev-amd64`
5. Deploy to robot: `sudo python3 tools/stack.py apply-native --profile pi5`

When you add a new node via `scripts/new-node.sh`, remember to add it to `manifest.yaml` so it's included in your stack!

---

## 🆕 Creating a New Node

Scaffold a new node repo with:

```bash
scripts/new-node.sh python my-python-node
scripts/new-node.sh cpp my-cpp-node
```

This creates a sibling repo at `../my-python-node` or `../my-cpp-node`.
The script also updates **CMakeLists.txt** (for C++ nodes) and **Dockerfile.docker** so your target binary matches your repo name.

### Next steps

```bash
cd ../my-cpp-node
git init
git add .
git commit -m "init: my-cpp-node"
gh repo create YOURNAME/my-cpp-node --public --source=. --push
```

Then add it to your stack’s `manifest.yaml`.

---

## 🛠️ Building Nodes

Each node repo provides a `Makefile` with consistent targets:

```bash
make build-pi       # build on Raspberry Pi 4
make build-pi5      # build on Raspberry Pi 5
make build-jetson   # build on Jetson
make build-amd64    # build on x86_64 dev machine
make build-docker   # prepare Dockerfile for Compose
```

These ensure your builds are reproducible across devices.

---

## 🧪 Integration Testing (Docker)

Generate and run the Compose stack:

```bash
python3 tools/stack.py gen-compose --profile dev-amd64
docker compose up --build
```

* `mqtt` runs as a container broker
* Nodes run as services built from sibling repos
* Inside Compose, all nodes use `MQTT_URL=tcp://mqtt:1883`

Run checks with:

```bash
docker compose logs -f my-python-node
```

Optional: add simulators (fake GPS, odometry, lidar) under `sim/`.

---

## 🚀 Deploying to a Robot

On your Pi / Jetson:

```bash
sudo python3 tools/stack.py apply-native --profile pi5
# or
sudo python3 tools/stack.py apply-native --profile jetson
```

This:

* Clones/pulls node repos
* Builds each node with the correct profile
* Installs systemd units for runtime
* Starts services (auto-restart on crash/boot)

To update everything later:

```bash
sudo python3 tools/stack.py update --profile pi5
```

---

## 🔧 Useful Daily Tasks

* **Check broker logs:**

  ```bash
  journalctl -u mqtt.service -f
  ```

* **Restart a node:**

  ```bash
  sudo systemctl restart my-cpp-node.service
  ```

* **View node logs:**

  ```bash
  journalctl -u my-cpp-node.service -f
  ```

* **Validate Compose config before running:**

  ```bash
  docker compose config
  ```

* **Rebuild one node only:**

  ```bash
  cd ../my-python-node
  make build-amd64
  ```

---

## 📝 Tips

* Use `requirements-jetson.txt` in Python repos for Jetson-specific wheels.
* Keep each node repo language-agnostic; don’t assume Pi-only.
* Always regenerate Compose after editing `manifest.yaml`.
* CI tip: run `docker compose config` in your PR checks to catch YAML errors.
