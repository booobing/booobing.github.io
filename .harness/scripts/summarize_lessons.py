from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

EVENTS = Path(".harness/memory/session-events.jsonl")
OUT = Path("LESSONS.active.md")

RULES = {
    "started_without_charter": (
        "구현 전에는 `docs/charter.md` 또는 작업별 charter로 objective, non-goals, touched files를 먼저 적는다."
    ),
    "out_of_bounds_edit": (
        "허용 범위를 벗어나는 파일 수정은 금지하고, 임시 출력은 `.harness/tmp/`로 격리한다."
    ),
    "correct": "요구사항이나 계약을 다시 해석하게 되면 즉시 테스트와 checkpoint를 갱신한다.",
    "redo": "같은 실패를 반복하지 말고 RCA와 active lesson을 먼저 갱신한다.",
}

def main() -> int:
    counts = Counter()
    if EVENTS.exists():
        for line in EVENTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                counts[json.loads(line)["event"]] += 1

    bullets = []
    for event, _ in counts.most_common(8):
        if event in RULES:
            bullets.append(f"- {RULES[event]}")
    if not bullets:
        bullets.append("- 최근 반복 오류가 없으므로 기본 하네스 규칙만 유지한다.")

    text = (
        "# LESSONS.active.md\n\n"
        "최근 반복 오류를 줄이기 위해 즉시 적용할 짧은 규칙만 유지한다.\n\n"
        + "\n".join(bullets)
        + "\n"
    )
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
