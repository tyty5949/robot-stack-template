# IPC Conventions (MQTT)

The stack defaults to MQTT (Mosquitto). All nodes must follow these conventions.

---

## Topic Names

- Root: `robot/`
- Use lowercase with slashes:  
  - `robot/sensors/imu`  
  - `robot/sensors/lidar`  
  - `robot/cmd/vel`  
  - `robot/status/motor`

---

## QoS Levels

- **QoS 0** – high-rate telemetry (e.g., lidar scans, odometry)
- **QoS 1** – control/state messages (e.g., velocity commands, goals)
- **QoS 2** – not used (performance penalty)

---

## Retained Messages

- Use `retain` for configs and last-known state.
- Example: `robot/config/planner/max_speed`.

---

## Node Liveness (Last Will Testament)

Every node publishes to `robot/status/<name>`:
- `"1"` when alive
- `"0"` when dead/disconnected

System monitors can subscribe to `robot/status/#`.
