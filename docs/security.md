# Security Guide

Securing MQTT and stack services is important for production robots.

---

## Broker Security

Edit `broker/mosquitto.conf` or use `broker/mosquitto.remote.template` for remote deployments.

### Options
- **Authentication**: `password_file /etc/mosquitto/passwd`
- **TLS**: enable `cafile`, `certfile`, `keyfile`
- **Allowlist**: `allow_anonymous false`

---

## Secrets

- Never commit secrets to Git.
- Use `.env` files with `EnvironmentFile=` in systemd units.
- Add `.env.template` to repo to show expected variables.

---

## Node Security

- Run nodes as non-root user (`robot`).
- Use systemd hardening: `ProtectSystem=full`, `ProtectHome=yes`, `NoNewPrivileges=yes`.

---

## Network Security

- Keep broker bound to `127.0.0.1` unless remote access required.
- Use VPN or TLS if controlling over WAN.
