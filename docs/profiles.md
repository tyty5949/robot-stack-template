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

- **pi4.yaml** → runs natively with systemd + mosquitto service  
- **pi5.yaml** → same as pi4 but tuned for arm64 and GPU-enabled nodes  
- **jetson.yaml** → optimized for NVIDIA Jetson devices (CUDA/cuDNN support)  
- **dev-amd64.yaml** → runs in Docker with broker as container
