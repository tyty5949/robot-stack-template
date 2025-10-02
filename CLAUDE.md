## 🤖 Purpose

This file collects **common development tasks** you’ll use when working with the robot stack template:

* Scaffolding new nodes (Python, C++)
* Building and testing nodes locally
* Running integration tests with Docker Compose
* Deploying/updating on Raspberry Pi / Jetson
* Day-to-day developer workflows

Think of this as your **“cheat sheet”**.

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
