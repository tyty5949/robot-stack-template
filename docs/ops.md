# Operations & Updates

This guide covers how to operate, update, and debug your stack.

---

## Updating the Stack

On robot:
```bash
cd /opt/robot-stack
git pull
sudo python3 tools/stack.py apply-native --profile pi4
```

- Safe to re-run anytime (idempotent).
- Only restarts services that changed (code or unit).

---

## Logs

- System logs:
  ```bash
  journalctl -u motor.service -f
  journalctl -u planner.service -f
  ```
- Mosquitto logs:
  ```bash
  journalctl -u mosquitto -f
  ```

---

## Auto Updates

1. Copy the timer/service:
   ```bash
   sudo cp system/stack-update.* /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now stack-update.timer
   ```
1. This pulls + reapplies stack nightly at 03:00.

---

## Debug Checklist

- `scripts/health.sh` for quick checks.
- Verify MQTT broker is running (`mosquitto_sub -t "#" -v`).
- If a node won’t start:
  - Check `manifest.yaml` exec path.
  - Ensure `make build-<profile>` completes cleanly.
