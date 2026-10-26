from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".harness/scripts/cd_status.py"
HEADER = "# lessons-learned.md\n\n## Format\n- Date:\n- Task:\n- Symptom:\n\n## Entries\n"


def run_status(tmp_path: Path, events: list[tuple[str, float]], lessons: str, rca: bool = True) -> str:
    memory = tmp_path / ".harness/memory"
    memory.mkdir(parents=True)
    (memory / "session-events.jsonl").write_text(
        "".join(json.dumps({"ts": f"{day}T00:00:00+00:00", "score": score}) + "\n" for day, score in events),
        encoding="utf-8",
    )
    (memory / "lessons-learned.md").write_text(lessons, encoding="utf-8")
    (tmp_path / "docs").mkdir()
    if rca:
        (tmp_path / "docs/rca.demo.md").write_text("# RCA\n", encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True)
    return result.stdout


def entry(day: str) -> str:
    return f"\n- Date: {day}\n- Task: demo\n- Symptom: x\n"


def test_format_header_alone_does_not_complete_rca(tmp_path: Path) -> None:
    assert "STATUS=RCA_REQUIRED" in run_status(tmp_path, [("2026-10-01", 60)], HEADER)


def test_lesson_older_than_latest_event_does_not_complete_rca(tmp_path: Path) -> None:
    events = [("2026-09-01", 30), ("2026-10-01", 30)]
    assert "STATUS=RCA_REQUIRED" in run_status(tmp_path, events, HEADER + entry("2026-09-01"))


def test_date_only_lesson_does_not_complete_rca(tmp_path: Path) -> None:
    lessons = HEADER + "\n- Date: 2026-10-01\n"
    assert "STATUS=RCA_REQUIRED" in run_status(tmp_path, [("2026-10-01", 60)], lessons)


def test_lesson_on_or_after_latest_event_completes_rca(tmp_path: Path) -> None:
    events = [("2026-09-01", 30), ("2026-10-01", 30)]
    assert "STATUS=RCA_COMPLETE" in run_status(tmp_path, events, HEADER + entry("2026-10-01"))


def test_missing_rca_doc_still_requires_rca(tmp_path: Path) -> None:
    out = run_status(tmp_path, [("2026-10-01", 60)], HEADER + entry("2026-10-01"), rca=False)
    assert "STATUS=RCA_REQUIRED" in out


def test_below_threshold_is_ok(tmp_path: Path) -> None:
    assert "STATUS=OK" in run_status(tmp_path, [("2026-10-01", 10)], HEADER)
