# IPC Conventions (MQTT)

- Topic root: `robot/` by default
- Use lowercase with slashes: `robot/sensors/imu`, `robot/cmd/vel`
- QoS:
  - 0 for high-rate telemetry
  - 1 for commands/state
- Retain configs and last-known commands where useful
- LWT (Last Will) for node liveness: `robot/status/<node>`
