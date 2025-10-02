#!/usr/bin/env python3
# tools/stack.py
#
# Lightweight, ROS-free robot stack controller
# - Native/systemd runtime on Linux SBCs (Pi, Jetson, NUC)
# - Docker Compose generation for desktop integration
#
# Requirements: Python 3.8+, PyYAML
#   sudo apt-get update && sudo apt-get install -y python3-yaml
#
# Usage:
#   python3 tools/stack.py apply-native --profile pi4
#   python3 tools/stack.py gen-compose --profile dev-amd64
#   python3 tools/stack.py status
#   python3 tools/stack.py doctor
#
import argparse, os, sys, subprocess, shlex, hashlib, textwrap, pathlib, shutil
from typing import Dict, Any, List
try:
    import yaml
except ImportError:
    print("PyYAML is required. Install with: sudo apt-get install -y python3-yaml", file=sys.stderr)
    sys.exit(1)

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
STATE_DIR = pathlib.Path("/var/lib/robot-stack")  # stores last commit SHAs, etc.

def run(cmd: List[str], cwd: str | None = None, check: bool = True, capture: bool = False):
    print(f"+ {' '.join(cmd)}", flush=True)
    if capture:
        return subprocess.run(cmd, cwd=cwd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return subprocess.run(cmd, cwd=cwd, check=check)

def which(prog: str) -> bool:
    return shutil.which(prog) is not None

def read_yaml(path: str | pathlib.Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def ensure_dir(p: str | pathlib.Path):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def sha256_file(p: str | pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def write_if_changed(dst: str | pathlib.Path, content: str) -> bool:
    dst = pathlib.Path(dst)
    new_hash = sha256_bytes(content.encode("utf-8"))
    old_hash = sha256_file(dst) if dst.exists() else None
    if new_hash != old_hash:
        ensure_dir(dst.parent)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def sudo() -> List[str]:
    return ["sudo"] if os.geteuid() != 0 else []

# ------------------------ manifest & profiles ------------------------
def deep_merge(base: Any, over: Any) -> Any:
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for k, v in over.items():
            out[k] = deep_merge(base.get(k), v)
        return out
    if isinstance(base, list) and isinstance(over, list):
        return list(over)
    return over if over is not None else base

def apply_profile(manifest: Dict[str, Any], profile_name: str | None) -> Dict[str, Any]:
    m = dict(manifest)
    if not profile_name:
        return m
    profiles = m.get("profiles", {})
    if profile_name not in profiles:
        raise SystemExit(f"Profile '{profile_name}' not found in manifest.")
    prof = profiles[profile_name] or {}
    for key in ["stack_root", "ipc", "defaults"]:
        if key in prof:
            m[key] = deep_merge(m.get(key, {}), prof[key])
    base_nodes = m.get("nodes", []) or []
    prof_nodes = prof.get("nodes", []) or []
    over_by_name = {n["name"]: n for n in prof_nodes if "name" in n}
    new_nodes = []
    for n in base_nodes:
        ov = over_by_name.get(n["name"])
        new_nodes.append(deep_merge(n, ov) if ov else n)
    m["nodes"] = new_nodes
    return m

# ------------------------ git & build ------------------------
def clone_or_checkout(node: Dict[str, Any], dest_root: str) -> str:
    node_dir = pathlib.Path(dest_root) / node["name"]
    repo = node["repo"]; ref = node.get("ref", "main")
    if not node_dir.exists():
        run(["git", "clone", "--branch", ref, repo, str(node_dir)])
    else:
        run(["git", "fetch", "origin"], cwd=str(node_dir))
        run(["git", "checkout", ref], cwd=str(node_dir))
        run(["git", "pull", "--ff-only", "origin", ref], cwd=str(node_dir), check=False)
    return str(node_dir)

def get_head_commit(repo_dir: str) -> str:
    r = run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture=True)
    return (r.stdout or "").strip()

def read_prev_sha(node_name: str) -> str | None:
    p = STATE_DIR / f"{node_name}.sha"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return None

def write_sha(node_name: str, sha: str):
    ensure_dir(STATE_DIR)
    (STATE_DIR / f"{node_name}.sha").write_text(sha + "\n", encoding="utf-8")

def run_build(node: Dict[str, Any], repo_dir: str, build_key: str):
    build = node.get("build", {})
    use = node.get("build", {}).get("use")
    if use:
        cmds = build.get(use)
    else:
        cmds = build.get(build_key)
    if not cmds:
        print(f"[WARN] Node '{node['name']}' has no build entry for '{build_key}' (or build.use). Skipping build.")
        return
    if isinstance(cmds, str):
        cmd_list = shlex.split(cmds)
        run(cmd_list, cwd=repo_dir)
    elif isinstance(cmds, list):
        run([str(x) for x in cmds], cwd=repo_dir)
    else:
        raise SystemExit(f"Invalid build command for node {node['name']}")

# ------------------------ systemd units ------------------------
def render_systemd_unit(manifest: Dict[str, Any], node: Dict[str, Any]) -> str:
    tmpl_path = ROOT / "system" / "unit.systemd.tmpl"
    if not tmpl_path.exists():
        raise SystemExit(f"Missing template: {tmpl_path}")
    tmpl = tmpl_path.read_text(encoding="utf-8")

    defaults = manifest.get("defaults", {})
    d_env = defaults.get("env", {}) or {}
    n_env = node.get("env", {}) or {}
    env = dict(d_env); env.update(n_env)
    env_lines = " ".join(f"{k}={v}" for k, v in env.items())

    unit = defaults.get("unit", {}) or {}
    after = " ".join(node.get("unit", {}).get("after", unit.get("after", ["network-online.target"])))

    user = node.get("user", defaults.get("user", "robot"))
    workdir = pathlib.Path(manifest["stack_root"]) / node["name"] / node.get("workdir", ".")
    exec_cmd = node["exec"]
    if not os.path.isabs(exec_cmd):
        exec_cmd = str(workdir / exec_cmd)
    restart = node.get("unit", {}).get("restart", unit.get("restart", "on-failure"))

    return tmpl.format(
        name=node["name"],
        after=after,
        user=user,
        workdir=str(workdir),
        exec=exec_cmd,
        restart=restart,
        env_lines=env_lines
    )

def systemctl(*args: str):
    run(sudo() + ["systemctl", *args])

def ensure_systemd_available():
    if not which("systemctl"):
        raise SystemExit("systemd not found. apply-native requires systemd.")

# ------------------------ broker (mosquitto) ------------------------
def install_or_update_broker(manifest: Dict[str, Any]) -> bool:
    ipc = manifest.get("ipc", {}) or {}
    adapter = ipc.get("adapter", "mqtt")
    if adapter != "mqtt":
        print("Non-MQTT adapter configured; broker install skipped.")
        return False
    broker = ipc.get("broker", {}) or {}
    btype = broker.get("type", "mosquitto")
    if btype not in ("mosquitto", "docker"):
        print(f"Broker type '{btype}' not handled natively; skipping.")
        return False
    if btype == "docker":
        print("Broker handled via Docker in this profile; skipping native install.")
        return False

    conf_rel = broker.get("conf", "broker/mosquitto.conf")
    conf_src = ROOT / conf_rel
    if not conf_src.exists():
        raise SystemExit(f"Broker conf not found: {conf_src}")

    if not which("mosquitto"):
        run(sudo() + ["apt-get", "update"])
        run(sudo() + ["apt-get", "install", "-y", "mosquitto", "mosquitto-clients"])

    ensure_dir("/etc/mosquitto")
    changed = write_if_changed("/etc/mosquitto/mosquitto.conf", conf_src.read_text(encoding="utf-8"))

    systemctl("enable", "mosquitto")
    if changed:
        try:
            systemctl("reload-or-restart", "mosquitto")
        except subprocess.CalledProcessError:
            systemctl("restart", "mosquitto")
    else:
        print("Broker config unchanged.")
    return changed

# ------------------------ apply-native ------------------------
def apply_native(manifest: Dict[str, Any], profile_name: str, build_key: str):
    ensure_systemd_available()

    view = apply_profile(manifest, profile_name)
    stack_root = view["stack_root"]
    ensure_dir(stack_root)
    ensure_dir(STATE_DIR)

    install_or_update_broker(view)

    any_unit_changed = False
    changed_units: List[str] = []
    restarted_nodes: List[str] = []
    for node in view.get("nodes", []):
        name = node["name"]
        print(f"\n== {name} ==")

        repo_dir = clone_or_checkout(node, stack_root)
        new_sha = get_head_commit(repo_dir)
        prev_sha = read_prev_sha(name)
        code_changed = (new_sha != prev_sha)

        run_build(node, os.path.join(repo_dir, node.get("workdir", ".")), build_key)

        unit_text = render_systemd_unit(view, node)
        unit_path = f"/etc/systemd/system/{name}.service"
        unit_changed = write_if_changed(unit_path, unit_text)
        if unit_changed:
            any_unit_changed = True
            changed_units.append(name)

        systemctl("enable", f"{name}.service")

        if code_changed:
            restarted_nodes.append(name)
            write_sha(name, new_sha)

        if prev_sha is None:
            write_sha(name, new_sha)

    if any_unit_changed:
        systemctl("daemon-reload")

    for name in changed_units:
        systemctl("restart", f"{name}.service")

    for name in restarted_nodes:
        if name not in changed_units:
            systemctl("restart", f"{name}.service")

    print("\\nSummary:")
    print(f" - Units changed: {', '.join(changed_units) if changed_units else 'none'}")
    print(f" - Code restarts: {', '.join(restarted_nodes) if restarted_nodes else 'none'}")
    print("Apply complete.")

# ------------------------ compose generation ------------------------
def gen_compose(manifest: Dict[str, Any], profile_name: str, out_path: str):
    """
    Generate docker-compose.yml using safe YAML emission.
    Each node builds from a sibling repo (../<node>) and uses Dockerfile.docker.
    """
    view = apply_profile(manifest, profile_name)

    compose: Dict[str, Any] = {"services": {}}

    # Broker
    broker = (view.get("ipc") or {}).get("broker") or {}
    broker_type = broker.get("type", "mosquitto")
    if broker_type in ("docker", "mosquitto"):
        compose["services"]["mqtt"] = {
            "image": "eclipse-mosquitto:2",
            "restart": "unless-stopped",
            "ports": ["1883:1883"],
        }

    # Defaults
    defaults_env = (view.get("defaults") or {}).get("env") or {}

    # Nodes
    for n in view.get("nodes", []):
        env = dict(defaults_env)
        env.update(n.get("env") or {})
        # Always talk to the mqtt service in Compose
        env["MQTT_URL"] = "tcp://mqtt:1883"

        compose["services"][n["name"]] = {
            "build": {
                "context": f"../{n['name']}",
                "dockerfile": "Dockerfile.docker",  # <= key change
            },
            "environment": env,
            "depends_on": ["mqtt"],
            "restart": "unless-stopped",
        }

    ensure_dir(pathlib.Path(out_path).parent)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(compose, f, sort_keys=False)
    print(f"Wrote {out_path}")

# ------------------------ QoL ------------------------
def status():
    if which("systemctl"):
        run(sudo() + ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"])
    else:
        print("systemctl not found; status is minimal on this system.")

def doctor():
    problems = []
    if not which("git"): problems.append("git missing")
    if not which("python3"): problems.append("python3 missing")
    try:
        import yaml  # noqa
    except Exception:
        problems.append("python3-yaml missing")
    print("Doctor check:")
    if problems:
        for p in problems: print(" -", p)
        sys.exit(1)
    else:
        print(" - OK")

def main():
    ap = argparse.ArgumentParser(description="Robot Stack Controller")
    ap.add_argument("cmd", choices=["apply-native", "gen-compose", "status", "doctor"])
    ap.add_argument("--manifest", default=str(ROOT / "manifest.yaml"))
    ap.add_argument("--profile", default=None, help="Profile name from profiles/*.yaml")
    ap.add_argument("--out", default=str(ROOT / "docker-compose.yml"), help="Output path for gen-compose")
    ap.add_argument("--build-key", default="pi", help="Default build key (pi/amd64/jetson/docker)")
    args = ap.parse_args()

    manifest = read_yaml(args.manifest)
    if args.cmd == "apply-native":
        apply_native(manifest, args.profile, args.build_key)
    elif args.cmd == "gen-compose":
        gen_compose(manifest, args.profile, args.out)
    elif args.cmd == "status":
        status()
    elif args.cmd == "doctor":
        doctor()

if __name__ == "__main__":
    main()
