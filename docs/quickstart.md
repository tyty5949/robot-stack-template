# Quickstart

## Robot (Pi/Jetson/x86 with systemd)
```bash
sudo apt-get update && sudo apt-get install -y git python3-yaml python3-jinja2
git clone https://github.com/YOURNAME/robot-stack-template.git /opt/robot-stack
cd /opt/robot-stack
sudo python3 tools/stack.py apply-native --profile pi4
```

## Desktop Dev
```bash
python3 tools/stack.py gen-compose --profile dev-amd64
docker compose up --build
```
