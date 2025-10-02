#!/usr/bin/env bash
set -euo pipefail

NEW_NAME="${1:?usage: bootstrap.sh <new-stack-name>}"

# Run replacement across tracked files, but skip this script
rg -l 'robot-stack-template' \
  | grep -v "scripts/bootstrap.sh" \
  | xargs sed -i "s/robot-stack-template/${NEW_NAME}/g"

echo "✅ Renamed references from 'robot-stack-template' to '${NEW_NAME}'."
echo "Next steps:"
echo "  git add . && git commit -m 'Initialized ${NEW_NAME}'"
echo "  git push -u origin main"