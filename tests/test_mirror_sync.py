from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILLS = ROOT / ".agents/skills"
CLAUDE_SKILLS = ROOT / ".claude/skills"
FRONTMATTER = re.compile(r"^---\n.*?\n---\n", re.S)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def without_description(text: str) -> str:
    # Descriptions may be reworded per tool (e.g. dropping "Codex"); bodies must match.
    return "\n".join(line for line in text.splitlines() if not line.startswith("description:"))


def skill_names(root: Path) -> set[str]:
    return {path.parent.name for path in root.glob("*/SKILL.md")}


def test_skill_sets_match() -> None:
    assert skill_names(CODEX_SKILLS) == skill_names(CLAUDE_SKILLS)


def test_skill_bodies_match() -> None:
    mismatched = [
        name
        for name in sorted(skill_names(CODEX_SKILLS) & skill_names(CLAUDE_SKILLS))
        if without_description(read(CODEX_SKILLS / name / "SKILL.md"))
        != without_description(read(CLAUDE_SKILLS / name / "SKILL.md"))
    ]
    assert mismatched == []


def test_agent_instructions_match() -> None:
    mismatched = []
    for toml_path in sorted((ROOT / ".codex/agents").glob("*.toml")):
        agent = tomllib.loads(read(toml_path))
        md_path = ROOT / ".claude/agents" / f"{agent['name']}.md"
        body = FRONTMATTER.sub("", read(md_path)).strip() if md_path.is_file() else None
        if body != agent["developer_instructions"].strip():
            mismatched.append(agent["name"])
    assert mismatched == []


def test_claude_and_codex_hooks_cover_shared_ruff_policy() -> None:
    claude = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    codex = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
    claude_group = claude["hooks"]["PostToolUse"][0]
    codex_group = codex["hooks"]["PostToolUse"][0]
    assert claude_group["matcher"] == "Edit|Write|MultiEdit"
    assert codex_group["matcher"] == "Edit|Write"
    assert "ruff_hook.py" in claude_group["hooks"][0]["command"]
    assert "ruff_hook.py" in codex_group["hooks"][0]["command"]
    assert "ruff_hook" in codex_group["hooks"][0]["commandWindows"]
