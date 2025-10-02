This repo is a template for a **C++ MQTT node** in the robot stack.

## 🧠 What this node is expected to do

- Build an executable (target name = **repo name**, e.g. `my-cpp-node`)
- Log to stdout/stderr
- Exit non-zero on fatal errors
- (Optional) Link MQTT client lib (Paho, etc.)

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

* **Container won’t start** → usually wrong arch binary or missing runtime libs.

  * Check: `file /usr/local/bin/<your-binary>` (should be `x86_64` on desktop)
  * Ensure Dockerfile installs `libstdc++6 libgcc-s1`
* **Exec path wrong** → `ENTRYPOINT` must match the copied binary path.
* **No binary built** → confirm `add_executable(<your-name> src/main.cpp)` exists and target name matches repo name.
