# Codex Project Template Bridge Preset

This local Spec Kit preset keeps `codex_project_template` as the operational authority while using Spec Kit to create feature-level `spec.md`, `plan.md`, and `tasks.md` artifacts.

## Intended Authority

- `AGENTS.md` remains the operational source of truth.
- `.specify/memory/constitution.md` mirrors stable principles from `AGENTS.md` and `LESSONS.active.md`.
- Spec Kit artifacts are planning inputs for a feature, not final completion gates.
- `.harness/checkpoints/default.yml` remains the completion gate.

## Install In A Project

```powershell
uvx --from git+https://github.com/github/spec-kit.git@v0.8.7 specify init --here --integration codex --integration-options="--skills" --no-git --ignore-agent-tools
specify preset add --dev .harness/spec-kit/codex-template-preset
```

Use `--no-git` for the first pilot so Spec Kit does not install branch or commit automation into the template flow.

## Expected Flow

```text
charter
-> speckit specify/clarify
-> speckit plan
-> speckit tasks
-> implementation
-> .harness checkpoint
-> review
-> lesson/RCA
```
