from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

OUT = Path(".harness/memory/session-events.jsonl")

def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python .harness/scripts/record_event.py <task_id> <event> <score> [note]")
        return 2
    task_id, event, score = sys.argv[1], sys.argv[2], float(sys.argv[3])
    note = sys.argv[4] if len(sys.argv) > 4 else ""
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "task_id": task_id,
        "event": event,
        "score": score,
        "note": note,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(f"recorded: {payload}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
