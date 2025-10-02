#!/usr/bin/env bash
set -euo pipefail
LANG="${1:-}"
NAME="${2:-}"
if [[ -z "$LANG" || -z "$NAME" ]]; then
  echo "usage: scripts/new-node.sh <python|cpp> <node-repo-name>"
  exit 1
fi
DEST="../${NAME}"
if [[ -e "$DEST" ]]; then
  echo "Destination ${DEST} already exists"; exit 1
fi
case "$LANG" in
  python) cp -R examples/node-python "${DEST}" ;;
  cpp)    cp -R examples/node-cpp "${DEST}" ;;
  *) echo "unknown lang: $LANG"; exit 1 ;;
esac
echo "Scaffolded ${LANG} node at ${DEST}"
echo "Remember to create a GitHub repo and push it, then add it to manifest.yaml."

