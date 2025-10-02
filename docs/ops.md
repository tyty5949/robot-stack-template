# Ops

- **Update**: rerun `tools/stack.py apply-native` anytime; safe & idempotent.
- **Lockfile**: use `manifest.lock.yaml` to pin SHAs; apply with `--use-lock` (extend tools/stack.py accordingly).
- **Logs**: `journalctl -u <node>.service -f`.
- **Timers**: enable the auto-update timer:
  ```bash
  sudo cp system/stack-update.* /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now stack-update.timer
  ```
