# Charter

- Objective: Adapt Harness² (Google Research, 2026) ideas to this template's improvement loop: (1) lesson entries with scope, component, and evidence, where harness changes become lessons only with evidence and RCA failure records stay mandatory; (2) a `harness-improve` skill that proposes invariant/domain harness edits, probes them by re-running the same task or checkpoint, and keeps only edits supported by a before/after contrast; (3) RCA prevention rules that prefer enforcing components (hook > script > checkpoint > skill > prose rule). (4) Fix pre-existing gaps found in review: `cd_status.py` must count only real lesson entries dated on or after the latest event, and `README.md` must list the actual skills and Claude files.
- Non-goals: Do not install or vendor `google-research/harness2`, add dependencies, add automated multi-candidate runs, change checkpoint commands, or rewrite existing lesson entries.
- Touched files: `docs/charter.md`, `AGENTS.md`, `CLAUDE.md`, `.harness/memory/lessons-learned.md`, `.agents/skills/lesson-logger/SKILL.md`, `.claude/skills/lesson-logger/SKILL.md`, `.agents/skills/root-cause-analysis/SKILL.md`, `.claude/skills/root-cause-analysis/SKILL.md`, `.agents/skills/harness-improve/SKILL.md`, `.agents/skills/harness-improve/agents/openai.yaml`, `.claude/skills/harness-improve/SKILL.md`, `.codex/agents/rca_analyst.toml`, `.claude/agents/rca_analyst.md`, `docs/rca.template.md`, `docs/template-capabilities.md`, `tests/test_mirror_sync.py`, `.harness/scripts/cd_status.py`, `tests/test_cd_status.py`, `README.md`.
- Ambiguity: LOW.
- Difficulty: Medium.
- Required checkpoints: `uv run --frozen ruff check .`, `uv run --frozen python -m pytest -q`, `uv run --frozen python .harness/scripts/speckit_status.py`, `uv run --frozen python .harness/scripts/cd_status.py`, `tests/test_mirror_sync.py`, fresh-context `reviewer` pass.
- Rollback plan: Delete `.agents/skills/harness-improve/`, `.claude/skills/harness-improve/`, `tests/test_mirror_sync.py`, and `tests/test_cd_status.py`; revert the lesson-logger, root-cause-analysis, rca_analyst, lessons-learned format, RCA template, template-capabilities, cd_status, README, AGENTS, CLAUDE, and charter edits.

## Follow-up Charter: Claude-to-Codex parity

- Objective: Make the Claude Code setup usable from Codex with the same shared skills, agent instructions, and Ruff-after-edit behavior.
- Non-goals: Do not copy `.claude/settings.local.json` permission grants, change model choices, install plugins, or alter the existing workflow rules.
- Touched files: `.codex/hooks.json`, `.codex/agents/*.toml`, `.harness/scripts/ruff_hook.py`, `tests/test_ruff_hook.py`, `tests/test_mirror_sync.py`, `tests/test_template_integrity.py`, `AGENTS.md`, `CLAUDE.md`, `README.md`.
- Ambiguity: LOW.
- Difficulty: Medium.
- Required checkpoints: mirror tests, hook tests from a repository subdirectory, `uv run --frozen ruff check .`, `uv run --frozen python -m pytest -q`, `uv run --frozen python .harness/scripts/speckit_status.py`, `uv run --frozen python .harness/scripts/cd_status.py`.
- Rollback plan: Remove `.codex/hooks.json` and revert only the shared hook, documentation, and test changes listed above; preserve all earlier uncommitted Harness² work.
