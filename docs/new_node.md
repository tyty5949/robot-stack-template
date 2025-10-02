# Adding a New Node

This guide explains how to scaffold, build, and integrate a new node into your robot stack.

---

## 1. Scaffold

Use the helper script to generate a node repo:

```bash
scripts/new-node.sh python motor-node
scripts/new-node.sh cpp planner-node
````

This creates a sibling directory `../motor-node` or `../planner-node`. Initialize it as a Git repo and push to GitHub.

---

## 2. Implement Node Contract

Follow the [Node Contract](node_contract.md):

* Include `Makefile` with `build-pi`, `build-amd64`, `build-docker`.
* Provide `Dockerfile.docker` for Compose.
* Place source code in `src/` or equivalent.

---

## 3. Add to Manifest

In `manifest.yaml`:

```yaml
- name: motor
  repo: https://github.com/YOURNAME/motor-node.git
  ref: main
  workdir: .
  exec: build/motor
  build:
    pi: ["make","build-pi"]
    amd64: ["make","build-amd64"]
    docker:["make","build-docker"]
```

---

## 4. Test Locally

* **Native (Pi):**

  ```bash
  sudo python3 tools/stack.py apply-native --profile pi4
  ```
* **Docker (dev):**

  ```bash
  python3 tools/stack.py gen-compose --profile dev-amd64
  docker compose up --build
  ```
