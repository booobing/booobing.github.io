from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".harness/scripts/ruff_hook.py"


def hook_input(file_path: Path | str) -> str:
    return json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(file_path)}})


def codex_hook_input(file_path: Path | str) -> str:
    patch = "\n".join(
        [
            "*** Begin Patch",
            f"*** Update File: {Path(file_path).as_posix()}",
            "@@",
            "+import os",
            "*** End Patch",
        ]
    )
    return json.dumps({"tool_name": "apply_patch", "tool_input": {"command": patch}})


def run_hook(file_path: Path | str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=hook_input(file_path),
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_non_python_file_is_ignored() -> None:
    assert run_hook(ROOT / "README.md").returncode == 0


def test_clean_python_file_passes(tmp_path: Path) -> None:
    path = tmp_path / "clean.py"
    path.write_text("VALUE = 1\n", encoding="utf-8")
    assert run_hook(path).returncode == 0


def test_lint_error_is_reported_back(tmp_path: Path) -> None:
    path = tmp_path / "dirty.py"
    path.write_text("import os\n", encoding="utf-8")
    result = run_hook(path)
    assert result.returncode == 2
    assert "F401" in result.stderr


def test_codex_apply_patch_payload_is_checked(tmp_path: Path) -> None:
    path = tmp_path / "dirty.py"
    path.write_text("import os\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=codex_hook_input(path),
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "F401" in result.stderr


def test_codex_move_payload_checks_the_destination(tmp_path: Path) -> None:
    path = tmp_path / "moved.py"
    path.write_text("import os\n", encoding="utf-8")
    payload = json.dumps(
        {
            "tool_name": "apply_patch",
            "tool_input": {
                "command": "\n".join(
                    [
                        "*** Begin Patch",
                        "*** Update File: old.py",
                        f"*** Move to: {path.as_posix()}",
                        "@@",
                        "+import os",
                        "*** End Patch",
                    ]
                )
            },
        }
    )
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "F401" in result.stderr


def test_missing_ruff_is_fail_open(tmp_path: Path) -> None:
    path = tmp_path / "dirty.py"
    path.write_text("import os\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-S", str(HOOK)],
        input=hook_input(path),
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_ruff_excluded_path_is_not_blocked() -> None:
    path = ROOT / ".harness/tmp/ruff_hook_excluded.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("import os\n", encoding="utf-8")
    try:
        assert run_hook(path).returncode == 0
    finally:
        path.unlink()


def bash_with_uv() -> bool:
    if shutil.which("bash") is None:
        return False
    probe = subprocess.run(["bash", "-c", "command -v uv"], capture_output=True)
    return probe.returncode == 0


@pytest.mark.skipif(not bash_with_uv(), reason="hook commands run through a bash that has uv")
def test_settings_command_works_outside_repo_root(tmp_path: Path) -> None:
    settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    command = settings["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    path = tmp_path / "dirty.py"
    path.write_text("import os\n", encoding="utf-8")
    result = subprocess.run(
        ["bash", "-c", command],
        input=hook_input(path),
        cwd=ROOT / "tests",
        env={**os.environ, "CLAUDE_PROJECT_DIR": ROOT.as_posix()},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2, result.stderr
    assert "F401" in result.stderr


@pytest.mark.skipif(shutil.which("cmd") is None, reason="Codex Windows hook uses cmd.exe")
def test_codex_command_works_outside_repo_root(tmp_path: Path) -> None:
    hooks = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
    command = hooks["hooks"]["PostToolUse"][0]["hooks"][0]["commandWindows"]
    path = tmp_path / "dirty.py"
    path.write_text("import os\n", encoding="utf-8")
    result = subprocess.run(
        command,
        input=codex_hook_input(path),
        cwd=ROOT / "tests",
        capture_output=True,
        text=True,
        shell=True,
    )
    assert result.returncode == 2, result.stderr
    assert "F401" in result.stderr
