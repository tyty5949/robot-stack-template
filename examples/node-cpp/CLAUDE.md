## 🎯 Project Context

This is a **standalone C++ MQTT node** for a robot stack. It's designed to:

- Run as an independent process (systemd service or Docker container)
- Communicate via MQTT broker (`MQTT_URL` environment variable)
- Build for multiple platforms: Pi 4/5, Jetson, x86_64, Docker
- Be deployed and managed by the parent stack's `manifest.yaml`

**Key principle**: This repo is self-contained. The stack repo orchestrates deployment, but all build logic lives here.

## 🧠 What this node does

- Builds an executable (target name = **repo name**, e.g. `my-cpp-node`)
- Logs to stdout/stderr (captured by systemd/Docker)
- Exits non-zero on fatal errors
- Communicates via MQTT (optional: link Paho client lib)

## 📦 Layout

````

.
├── src/
│   └── main.cpp           # main entrypoint
├── CMakeLists.txt         # builds target named after repo
├── Makefile               # build targets (pi5/jetson/amd64/docker)
└── Dockerfile.docker      # multi-stage build to produce runtime image

````

## 🔧 Build targets

```bash
make build-pi       # Raspberry Pi 4 (arm64)
make build-pi5      # Raspberry Pi 5 (arm64, tuned)
make build-jetson   # Jetson (arm64, optional CUDA flags)
make build-amd64    # Desktop dev (x86_64)
make build-docker   # Prepare Dockerfile for Compose builds
````

Artifacts land in `build/`. By default, the executable is `build/<repo-name>`.

## ▶️ Run locally

Native build:

```bash
make build-amd64
./build/<your-binary>
```

With env:

```bash
MQTT_URL=tcp://localhost:1883 ./build/<your-binary>
```

Inside Docker/Compose:

* Ensure your stack’s `docker-compose.yml` points to this repo and `Dockerfile.docker`.
* Run from the **stack** repo: `docker compose up --build`.

## 🐳 Dockerfile (multi-stage)

Provided `Dockerfile.docker` builds on Debian slim, installs runtime libs (`libstdc++6`, `libgcc-s1`), and copies the binary:

```dockerfile
# syntax=docker/dockerfile:1.7
ARG DEBIAN_RELEASE=bookworm

FROM --platform=$BUILDPLATFORM debian:${DEBIAN_RELEASE}-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ cmake make ninja-build ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
RUN cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
 && cmake --build build -j

FROM debian:${DEBIAN_RELEASE}-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 libgcc-s1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# IMPORTANT: this path must match your built target name
COPY --from=build /src/build/<your-binary> /usr/local/bin/<your-binary>
ENTRYPOINT ["<your-binary>"]
```

> The **scaffolder** updates `<your-binary>` automatically to your new repo name.

## 🧪 Linking MQTT (optional)

If you add Paho MQTT C/C++:

* Install dev libs in the **builder** stage:

  ```dockerfile
  apt-get install -y libpaho-mqttpp3-dev libpaho-mqtt3c-dev
  ```
* In `CMakeLists.txt`:

  ```cmake
  find_package(PahoMqttC CONFIG QUIET)
  find_package(PahoMqttCpp CONFIG QUIET)
  target_link_libraries(my-cpp-node PRIVATE paho-mqttpp3 paho-mqtt3c)
  target_compile_definitions(my-cpp-node PRIVATE HAVE_PAHO)
  ```

## 🧰 Debugging

* Exec into container:

  ```bash
  docker compose run --rm --entrypoint sh <service>
  ```
* Check binary and deps:

  ```bash
  file /usr/local/bin/<your-binary>
  ldd  /usr/local/bin/<your-binary>
  ```
* Tail logs (Compose): `docker compose logs -f <service>`
* Tail logs (systemd): `journalctl -u <node>.service -f`

## 🧪 Sanitizers (recommended for dev)

In `CMakeLists.txt` (guard with `if(CMAKE_BUILD_TYPE MATCHES Debug)`):

```cmake
target_compile_options(my-cpp-node PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
target_link_options(my-cpp-node PRIVATE -fsanitize=address,undefined)
```

Run binary with `ASAN_OPTIONS=...` as needed.

## 📏 Warnings/flags

Already enabled:

```cmake
target_compile_options(my-cpp-node PRIVATE -Wall -Wextra -Wpedantic)
```

Add more (e.g., `-Werror`) during CI to keep quality high.

## 🚀 Deploy expectations

`manifest.yaml` (stack repo):

```yaml
- name: your-cpp-node
  repo: https://github.com/YOU/your-cpp-node.git
  ref: main
  workdir: .
  exec: build/your-cpp-node
  build:
    pi:     ["make","build-pi"]
    pi5:    ["make","build-pi5"]
    jetson: ["make","build-jetson"]
    amd64:  ["make","build-amd64"]
    docker: ["make","build-docker"]
```

## 🔎 Common errors

* **Container won't start** → usually wrong arch binary or missing runtime libs.

  * Check: `file /usr/local/bin/<your-binary>` (should be `x86_64` on desktop)
  * Ensure Dockerfile installs `libstdc++6 libgcc-s1`
* **Exec path wrong** → `ENTRYPOINT` must match the copied binary path.
* **No binary built** → confirm `add_executable(<your-name> src/main.cpp)` exists and target name matches repo name.

---

## 🤖 Development Workflow (Claude Code)

### Common Tasks

**Building for local testing:**
```bash
make build-amd64        # Desktop dev build
./build/<repo-name>     # Run directly
```

**Testing with Docker Compose:**
1. Return to the parent stack repo
2. Regenerate compose: `python3 tools/stack.py gen-compose --profile dev-amd64`
3. Run: `docker compose up --build`
4. Check logs: `docker compose logs -f <service-name>`

**Adding new source files:**
1. Create files under `src/`
2. Update `CMakeLists.txt` to add new source files to `add_executable()`
3. Rebuild: `make build-amd64`

**Adding dependencies (e.g., MQTT library):**
1. Update `Dockerfile.docker` builder stage to install dev packages
2. Update `CMakeLists.txt` with `find_package()` and `target_link_libraries()`
3. Update `Makefile` build commands if cross-compilation needs special flags
4. Test locally, then test in Docker

**Debugging compilation issues:**
```bash
# Clean rebuild
rm -rf build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j --verbose
```

### File Reference

| File | Purpose |
|------|---------|
| `src/main.cpp` | Main entry point - start here for logic changes |
| `CMakeLists.txt` | Build configuration - update when adding files/libs |
| `Makefile` | Build targets for different platforms - rarely modified |
| `Dockerfile.docker` | Container build recipe - update for dependencies |

### Integration with Stack

This node is referenced in the parent stack's `manifest.yaml`:

```yaml
- name: <repo-name>
  repo: https://github.com/YOU/<repo-name>.git
  ref: main
  workdir: .
  exec: build/<repo-name>
  build:
    pi5:    ["make","build-pi5"]
    amd64:  ["make","build-amd64"]
    docker: ["make","build-docker"]
```

After making changes:
1. Commit and push this repo
2. In the stack repo, run `sudo python3 tools/stack.py update --profile <profile>` to pull and rebuild

### Best Practices

- **Keep binary name matching repo name** - the scaffolder ensures this, maintain it
- **Log to stdout/stderr only** - systemd and Docker capture these
- **Exit cleanly** - return non-zero on unrecoverable errors (triggers systemd restart)
- **Read `MQTT_URL` from environment** - don't hardcode broker addresses
- **Test locally before Docker** - faster iteration with native builds
- **Use sanitizers during development** - catches memory issues early
