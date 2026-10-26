"""Shared Claude Code and Codex PostToolUse hook for edited Python files.

Claude sends the edited path in ``tool_input.file_path``. Codex sends an apply_patch
command in ``tool_input.command``, so this hook extracts paths from both formats.
Exit 2 sends Ruff's output back to the agent so it can fix the issue in the same turn.
Only Ruff exit code 1 (lint violations) is reported; a missing tool or any other failure
exits 0 and never blocks the edit.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return Path.cwd().resolve()


def file_paths(payload: dict[str, object]) -> list[str]:
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return []

    paths: list[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            paths.append(value)

    command = tool_input.get("command")
    if isinstance(command, str):
        for line in command.splitlines():
            for marker in ("*** Update File: ", "*** Add File: ", "*** Move to: "):
                if line.startswith(marker):
                    paths.append(line[len(marker) :].strip())
                    break
    return list(dict.fromkeys(paths))


def resolve_python_paths(paths: list[str], root: Path) -> list[Path]:
    resolved: list[Path] = []
    for value in paths:
        path = Path(value)
        candidates = [path] if path.is_absolute() else [Path.cwd() / path, root / path]
        match = next((candidate.resolve() for candidate in candidates if candidate.is_file()), None)
        if match is not None and match.suffix == ".py":
            resolved.append(match)
    return list(dict.fromkeys(resolved))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    root = repo_root()
    paths = resolve_python_paths(file_paths(payload), root)
    if not paths:
        return 0
    if importlib.util.find_spec("ruff") is None:
        return 0
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--no-cache",
            "--force-exclude",
            *[str(path) for path in paths],
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 1:
        return 0
    sys.stderr.write(result.stdout + result.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
