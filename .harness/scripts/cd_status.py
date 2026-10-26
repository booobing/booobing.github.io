from __future__ import annotations

import json
import re
from pathlib import Path

EVENTS = Path(".harness/memory/session-events.jsonl")
RCA_DOCS = [path for path in Path("docs").glob("rca.*.md") if path.name != "rca.template.md"]
LESSONS = Path(".harness/memory/lessons-learned.md")
RCA_AT = 50
HALT_AT = 80
ENTRY_DATE = re.compile(r"^- Date: (\d{4}-\d{2}-\d{2})\s*$", re.M)
LESSON_FIELD = re.compile(r"^- (Date|Task|Symptom):\s*(.+?)\s*$", re.M)


def has_lesson_since(day: str) -> bool:
    """True if lessons-learned.md has a real entry (below "## Entries") dated on or after day."""
    if not LESSONS.exists():
        return False
    _, _, entries = LESSONS.read_text(encoding="utf-8").partition("## Entries")
    for block in re.split(r"(?=^- Date: )", entries, flags=re.M):
        fields = dict(LESSON_FIELD.findall(block))
        if fields.get("Date", "") >= day and all(fields.get(name) for name in ("Task", "Symptom")):
            return True
    return False

def main() -> int:
    total = 0.0
    latest_day = ""
    if EVENTS.exists():
        for line in EVENTS.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            total += float(event.get("score", 0))
            latest_day = max(latest_day, str(event.get("ts", ""))[:10])
    print(f"Clarification Debt: {total}")
    if total >= HALT_AT:
        print("STATUS=HALT")
        return 80
    if total >= RCA_AT:
        has_rca = any(path.exists() for path in RCA_DOCS)
        if has_rca and has_lesson_since(latest_day):
            print("STATUS=RCA_COMPLETE")
            return 0
        print("STATUS=RCA_REQUIRED")
        return 50
    print("STATUS=OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
