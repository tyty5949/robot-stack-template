#!/usr/bin/env bash
set -euo pipefail
NEW_NAME="${1:-}"
if [[ -z "$NEW_NAME" ]]; then
  echo "usage: scripts/bootstrap.sh <new-stack-name>"
  exit 1
fi
echo "Renaming references from robot-stack-template -> ${NEW_NAME}"
grep -rl 'robot-stack-template' . | xargs sed -i "s/robot-stack-template/${NEW_NAME}/g"
echo "Done. You may now: git init && git remote add origin <url> && git add . && git commit -m 'init' && git push -u origin main"
