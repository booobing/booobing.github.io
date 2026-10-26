# lessons-learned.md

## Format
- Date:
- Task:
- Symptom:
- Root cause:
- Scope: invariant / domain
- Component: hook / script / checkpoint / skill / subagent / memory / AGENTS rule
- Evidence: before/after contrast, reproduced failure, or checkpoint result
- Earlier signal we missed:
- Prevention rule:
- Skill or AGENTS update:
- Whether it should become an active lesson:

harness 변경을 교훈으로 남길 때는 Evidence가 있어야 한다. 근거가 없는 변경은 `candidate`로만 적는다. RCA가 필요한 실패 기록은 재현된 실패를 Evidence로 항상 남긴다. 2026-10-21 이전 항목에는 Scope / Component / Evidence가 없다.

## Entries

- Date: 2026-06-26
- Task: lean-code-design
- Symptom: Generated skill UI metadata dropped the `$lean` prefix from `$lean-code-design`.
- Root cause: PowerShell expanded `$lean` inside a double-quoted argument before the generator received it.
- Earlier signal we missed: The default prompt was passed through shell quoting instead of single quotes or an escaped dollar.
- Prevention rule: Use single quotes or escape `$` for literal skill names in PowerShell command arguments.
- Skill or AGENTS update: Added the prevention rule to `LESSONS.active.md`.
- Whether it should become an active lesson: Yes.

- Date: 2026-10-17
- Task: claude-mirror
- Symptom: Codex-to-Claude mirroring touched 17 files without a charter; the new Ruff hook used a cwd-relative path that blocked every edit outside the repo root, and CLAUDE.md documented the wrong `record_event.py` usage.
- Root cause: A "set up tooling" request was treated as configuration rather than a task that needs a charter, and the hook was tested only by calling the script directly from the repo root.
- Earlier signal we missed: The touched-file count passed 3 (Medium difficulty), and the hook test never ran the actual settings.json command.
- Prevention rule: Agent/tooling setup still needs a charter first; test hooks by running the exact configured command from a non-root cwd; copy documented commands from the script's own usage text.
- Skill or AGENTS update: Added the hook-testing and charter rules to `LESSONS.active.md`.
- Whether it should become an active lesson: Yes.
