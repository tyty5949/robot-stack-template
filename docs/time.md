# Time Synchronization

Accurate timestamps are critical for sensor fusion.

---

## Recommended Setup

- Install `chrony`:
  ```bash
  sudo apt-get install -y chrony
  ```
- If GPS with PPS available:
    - Run `gpsd` to expose `/dev/ttyGPS`.
    - Configure `chrony` to discipline system clock with PPS.

---

## Verification

- Check sync:
  ```bash
  chronyc tracking
  ```
- PPS signal:
  ```bash
  sudo ppstest /dev/pps0
  ```

---

## Why it matters

- Odometry + GPS + lidar fusion, for example, requires timestamps <10ms accurate.
- If clocks drift, maps and localization will degrade.
