from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".harness/scripts/research_pipeline.py"


def run_pipeline(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_init_creates_manifest_and_parses_survey_topic(tmp_path: Path) -> None:
    workspace = tmp_path / "research-workspace"

    result = run_pipeline(
        "run",
        "--topic",
        "survey:short: Adaptive Sparse Attention",
        "--workspace",
        str(workspace),
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["topic"] == "Adaptive Sparse Attention"
    assert manifest["paper_mode"] == "survey"
    assert manifest["survey_depth"] == "short"
    assert manifest["current_stage"] == "ideation"
    assert list(manifest["stages"]) == manifest["stage_order"]


def test_complete_blocks_until_required_artifacts_exist(tmp_path: Path) -> None:
    workspace = tmp_path / "research-workspace"
    assert run_pipeline("init", "--topic", "original: Test Topic", "--workspace", str(workspace)).returncode == 0
    assert run_pipeline("start", "--workspace", str(workspace)).returncode == 0

    blocked = run_pipeline("complete", "--workspace", str(workspace))

    assert blocked.returncode == 3
    assert "MISSING=ideation/research_brief.md" in blocked.stdout
    assert "STATUS=BLOCKED" in blocked.stdout


def test_complete_advances_after_required_artifacts_exist(tmp_path: Path) -> None:
    workspace = tmp_path / "research-workspace"
    assert run_pipeline("init", "--topic", "Test Topic", "--workspace", str(workspace)).returncode == 0
    assert run_pipeline("start", "--workspace", str(workspace)).returncode == 0
    (workspace / "ideation/research_brief.md").write_text("brief\n", encoding="utf-8")
    (workspace / "ideation/literature_map.json").write_text("[]\n", encoding="utf-8")

    completed = run_pipeline("complete", "--workspace", str(workspace))

    assert completed.returncode == 0, completed.stderr
    assert "COMPLETED_STAGE=ideation" in completed.stdout
    assert "CURRENT_STAGE=planning" in completed.stdout
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["stages"]["ideation"]["status"] == "completed"
    assert manifest["current_stage"] == "planning"


def test_resume_reports_failed_stage(tmp_path: Path) -> None:
    workspace = tmp_path / "research-workspace"
    assert run_pipeline("init", "--topic", "Test Topic", "--workspace", str(workspace)).returncode == 0
    assert run_pipeline("start", "--workspace", str(workspace)).returncode == 0
    assert (
        run_pipeline(
            "fail",
            "--workspace",
            str(workspace),
            "--reason",
            "missing dataset",
        ).returncode
        == 0
    )

    result = run_pipeline("resume", "--workspace", str(workspace))

    assert result.returncode == 0, result.stderr
    assert "STATUS=failed" in result.stdout
    assert "RESUME_STAGE=ideation" in result.stdout
