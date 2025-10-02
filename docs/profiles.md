# Profiles

Profiles let you adapt the same manifest to multiple hardware setups.

---

## Example

`profiles/pi4.yaml`
```yaml
defaults:
  env:
    MQTT_URL: tcp://127.0.0.1:1883
nodes:
  - name: motor
    build: { use: pi }
  - name: planner
    build: { use: pi }
```

`profiles/dev-amd64.yaml`
```yaml
ipc:
  broker: { type: docker }
nodes:
  - name: motor
    build: { use: amd64 }
  - name: planner
    build: { use: docker }

```

---

## Common Profiles

- **pi4.yaml** → runs natively with systemd + mosquitto service.
- **dev-amd64.yaml** → runs in Docker with broker as container.
- **jetson.yaml** → same as pi but may use build: `{ use: jetson }`.
