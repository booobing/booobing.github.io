from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "LESSONS.active.md",
    "pyproject.toml",
    ".codex/agents/planner.toml",
    ".codex/agents/implementer.toml",
    ".codex/agents/reviewer.toml",
    ".codex/agents/qa.toml",
    ".codex/agents/security_reviewer.toml",
    ".codex/agents/rca_analyst.toml",
    ".codex/hooks.json",
    ".harness/checkpoints/default.yml",
    ".harness/scripts/record_event.py",
    ".harness/scripts/cd_status.py",
    ".harness/scripts/speckit_status.py",
    ".harness/scripts/summarize_lessons.py",
    ".harness/spec-kit/codex-template-preset/preset.yml",
    ".harness/spec-kit/codex-template-preset/README.md",
    ".harness/spec-kit/codex-template-preset/templates/constitution-template.md",
    ".harness/spec-kit/codex-template-preset/templates/spec-template.md",
    ".harness/spec-kit/codex-template-preset/templates/plan-template.md",
    ".harness/spec-kit/codex-template-preset/templates/tasks-template.md",
    "docs/charter.template.md",
    "docs/rca.template.md",
    "docs/template-capabilities.md",
]

FORBIDDEN_PATHS = [
    "android",
    "backend",
    "firmware",
    "instruction",
    "papers",
    "src",
    "WHITEPAPER.html",
    "MANUAL.backend.md",
    "MANUAL.frontend.md",
    "MANUAL.ops-test.md",
    "docs/node-firebase-backend-update.md",
    "docs/project-status.md",
    "docs/rca.backend_android_bootstrap.md",
]

FORBIDDEN_TRACKED_PREFIXES = [
    ".harness/gradle-home/",
    ".harness/pip-audit-cache/",
    ".harness/tmp/",
    ".hypothesis/",
    ".ruff_cache/",
    ".venv/",
]

FORBIDDEN_KEYWORDS = [
    "U" + "HF",
    "R" + "FID",
    "Firebase",
    "Android",
    "Tetris",
    "khuround",
]

TEXT_SUFFIXES = {".md", ".toml", ".yml", ".yaml", ".py", ".txt"}


def test_required_template_files_exist() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_project_specific_paths_are_removed() -> None:
    present = [path for path in FORBIDDEN_PATHS if (ROOT / path).exists()]
    assert present == []


def test_cache_and_generated_outputs_are_not_tracked() -> None:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = [path for path in result.stdout.splitlines() if (ROOT / path).exists()]
    offenders = [
        path
        for path in tracked
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in FORBIDDEN_TRACKED_PREFIXES)
    ]
    assert offenders == []


def test_template_text_has_no_legacy_project_keywords() -> None:
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        parts = path.relative_to(ROOT).parts
        if not parts:
            continue
        if parts[0] in {".git", ".venv", ".ruff_cache", ".pytest_cache"}:
            continue
        if len(parts) >= 2 and parts[0] == ".harness" and parts[1] in {"tmp", "uv-cache"}:
            continue
        if path.name == "test_template_integrity.py":
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in text:
                offenders.append(f"{rel}: {keyword}")
    assert offenders == []


def test_speckit_status_skips_when_not_initialized(tmp_path: Path) -> None:
    script = ROOT / ".harness/scripts/speckit_status.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "STATUS=SKIPPED" in result.stdout


def test_speckit_status_detects_unresolved_clarification(tmp_path: Path) -> None:
    script = ROOT / ".harness/scripts/speckit_status.py"
    feature_dir = tmp_path / "specs" / "001-demo"
    feature_dir.mkdir(parents=True)
    (tmp_path / ".specify" / "memory").mkdir(parents=True)
    (tmp_path / ".specify" / "memory" / "constitution.md").write_text(
        "AGENTS.md is the operational source of truth.\n",
        encoding="utf-8",
    )
    (feature_dir / "spec.md").write_text(
        "Feature\n\n[NEEDS CLARIFICATION: choose behavior]\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 20
    assert "STATUS=NEEDS_ATTENTION" in result.stdout
