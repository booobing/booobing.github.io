---
name: checkpoint-gate
description: Trigger after code changes, before claiming completion, or when a subagent needs to decide if work can advance to the next stage.
---

# Required checks
- Confirm a charter exists, or confirm the task is still bounded by an explicit user request.
- Read `.harness/checkpoints/default.yml`.
- Run the required commands that apply to the current project.
- Always run `uv run --frozen python .harness/scripts/cd_status.py` when Python tooling is available.
- If a command is intentionally skipped, record the reason and the residual risk.

# Output
- PASS / FAIL
- failed checkpoint names
- skipped checkpoint names and why
- smallest next action

# Rule
게이트가 실패하면 완료라고 말하지 않는다.
