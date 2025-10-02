# Contributing Guide

We welcome contributions to extend the robot stack template.

---

## Development Workflow

1. Fork and clone.
2. Create a feature branch.
3. Update code/docs/tests.
4. Run lint + CI locally.
5. Submit a PR.

---

## Coding Standards

- Python: PEP8, lint with `flake8`.
- YAML: lint with `yamllint`.
- Shell: lint with `shellcheck`.
- Commit messages: Conventional Commits (feat:, fix:, docs:, chore:, etc.).

---

## Adding a New Profile

1. Create `profiles/<name>.yaml`.
2. Add overrides for nodes, env, broker mode.
3. Update docs with profile description.

---

## Adding a New Example Node

- Place in `examples/node-<lang>`.
- Include Makefile + Dockerfile.docker + minimal app.
- Update `manifest.yaml` if you want it wired in.
```
