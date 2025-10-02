# Integration Testing

The stack supports running all nodes in Docker Compose for development and testing.

---

## Simulators

- Create lightweight simulators in `sim/` (e.g., fake odometry, GPS, lidar publishers).
- Add them to `docker/docker-compose.override.tmpl.yml` to spin up alongside nodes.

Example service:

```yaml
  sim-gps:
    build: ./sim/gps
    environment:
      MQTT_URL: tcp://mqtt:1883
    depends_on: ["mqtt"]
````

---

## Running Tests

1. Generate docker-compose:

   ```bash
   python3 tools/stack.py gen-compose --profile dev-amd64
   ```

2. Run integration test stack:

   ```bash
   docker compose up --build -d
   ```

3. Run your test harness (Python, Go, etc.) that subscribes to topics and verifies outputs.
