#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: scripts/new-node.sh <python|cpp> <node-repo-name>"
  echo "example: scripts/new-node.sh cpp my-cpp-node"
  exit 1
}

LANG="${1:-}"; NAME="${2:-}"
[[ -z "$LANG" || -z "$NAME" ]] && usage

# Destination as a sibling repo (keeps stack clean)
DEST="../${NAME}"
if [[ -e "$DEST" ]]; then
  echo "❌ Destination already exists: $DEST"
  exit 1
fi

case "$LANG" in
  python)
    cp -R examples/node-python "$DEST"
    echo "✅ Scaffolded Python node at: $DEST"
    echo "   Next: (cd $DEST && git init && git commit -m 'init' && gh repo create ...)"
    ;;
  cpp)
    cp -R examples/node-cpp "$DEST"
    echo "🔧 Personalizing C++ template for target '${NAME}'"

    CMAKE="$DEST/CMakeLists.txt"
    DOCKER="$DEST/Dockerfile.docker"
    README="$DEST/README.md"

    # --- Replace project() and add_executable() target names ---
    if [[ -f "$CMAKE" ]]; then
      # project(example_cpp) -> project(${NAME})
      sed -i.bak -E "s/^(project\\()[^)]+(\\))/\\1${NAME}\\2/" "$CMAKE" || true

      # add_executable(example_cpp src/main.cpp) -> add_executable(${NAME} src/main.cpp)
      sed -i.bak -E "s/^(add_executable\\()[^[:space:]]+([[:space:]].*)$/\\1${NAME}\\2/" "$CMAKE" || true

      # Optionally adjust runtime output folder message in comments (no-op if absent)
      rm -f "$CMAKE.bak"
    else
      echo "⚠️  Missing $CMAKE; skipping CMake renames."
    fi

    # --- Update Dockerfile CMD to use new binary name ---
    if [[ -f "$DOCKER" ]]; then
      # ./build/example_cpp -> ./build/${NAME}
      sed -i.bak -E "s|(./build/)[A-Za-z0-9_.-]+|\\1${NAME}|g" "$DOCKER" || true
      rm -f "$DOCKER.bak"
    fi

    # --- Optional: mention new name in README ---
    if [[ -f "$README" ]]; then
      sed -i.bak -E "s/node-cpp/${NAME}/g; s/node_cpp/${NAME}/g" "$README" || true
      rm -f "$README.bak"
    fi

    # --- Global: replace all occurrences in file contents and rename files/dirs ---
    # Replace textual occurrences inside files (skip binary-ish files by letting sed fail harmlessly)
    echo "🔎 Replacing all in-file occurrences of 'node-cpp' / 'node_cpp' with '${NAME}'..."
    # Use | as sed delimiter to avoid issues if NAME contains slashes
    find "$DEST" -type f -print0 |
      xargs -0 -I{} sh -c "sed -i.bak -E 's|node-cpp|${NAME}|g; s|node_cpp|${NAME}|g' \"{}\" 2>/dev/null || true"
    # Remove any sed backups
    find "$DEST" -name '*.bak' -type f -print0 | xargs -0 -r rm -f --

    # Rename files and directories containing node-cpp or node_cpp
    echo "🔁 Renaming files and directories containing 'node-cpp' or 'node_cpp'..."
    # Use depth so we rename children before parents
    find "$DEST" -depth -print0 |
      while IFS= read -r -d '' path; do
        base="$(basename "$path")"
        dir="$(dirname "$path")"
        newbase="${base//node-cpp/${NAME}}"
        newbase="${newbase//node_cpp/${NAME}}"
        if [[ "$newbase" != "$base" ]]; then
          mv -v "$path" "$dir/$newbase"
        fi
      done

    # (Optional) ensure CMake/Docker targeted renames still present — existing per-file edits are retained above.

    echo "✅ Scaffolded C++ node at: $DEST"
    echo "   Target name set to '${NAME}' in CMakeLists and Dockerfile."
    echo "   Build locally:  (cd $DEST && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j)"
    echo "   Next:           (cd $DEST && git init && git add . && git commit -m 'init: ${NAME}')"
    ;;
  *)
    echo "❌ unknown lang: $LANG"
    usage
    ;;
esac

echo "ℹ️  Remember to add the new repo URL to your stack's manifest.yaml and set the correct build target in profiles."
