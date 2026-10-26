# CLAUDE.md

이 파일은 Claude Code 진입점이다. 운영 규칙의 최상위 진실의 원천은 `AGENTS.md`이며,
Claude도 codex와 **동일한** charter -> plan -> implementation -> checkpoint -> review -> lesson
루프로 움직인다. 아래 규칙 전체를 그대로 따른다.

@AGENTS.md

## Claude Runtime Mapping

codex의 `.codex/agents/*.toml`과 `.agents/skills/*`는 Claude용으로 아래에 미러링되어 있다.
동작은 동일하고, 파일 위치와 형식만 각 도구에 맞춘 것이다.

### Subagents (`.claude/agents/`)

Agent 도구로 아래 역할을 호출한다. 본문 지침은 `.codex/agents/*.toml`의 `developer_instructions`와 같다.
codex는 read-only를 sandbox로 강제하지만, Claude의 read-only 역할은 테스트 실행을 위해 Bash를 가지므로
파일을 수정하지 않는 것은 프롬프트로만 지켜진다.

- `planner`: 목표, non-goals, 모호성, 난이도, 체크포인트, 롤백을 먼저 정리한다. (read-only)
- `implementer`: 승인된 범위 안에서 최소 diff로 코드/문서를 수정한다. (write)
- `reviewer`: 계약 위반, 회귀, 범위 확장, 테스트 누락을 찾는다. (read-only)
- `qa`: 수용 시나리오, 경계 조건, 실패 모드, 산출물 위생을 점검한다. (read-only)
- `security_reviewer`: 비밀값, 위험한 입출력, 의존성, 배포 위험을 확인한다. (read-only)
- `rca_analyst`: Clarification Debt가 임계치를 넘거나 반복 실패 시 원인과 예방 규칙을 정리한다. (read-only)

Difficulty 판정에 따라 Simple은 단일 흐름, Medium은 planner/implementer/reviewer,
Complex는 qa/security_reviewer/rca_analyst 관점까지 분리한다.

### Skills (`.claude/skills/`)

Skill 도구로 아래를 사용한다. codex `.agents/skills/*`와 내용이 동일하다.

- `charter-first`, `clarification-gate`, `brainstorm-no-code` — 착수 전 범위/모호성 정리
- `lean-code-design` — 구현 전 최소 안전 설계
- `checkpoint-gate` — 완료 선언 전 게이트 실행
- `lesson-logger`, `root-cause-analysis`, `review-synthesizer` — 회고/리뷰 종합
- `harness-improve` — RCA나 교훈이 제안한 harness 변경을 같은 작업으로 다시 실행해 검증한 뒤에만 반영
- `python-security-supply-chain` — Python 의존성/배포/보안
- `research-pipeline` — 선택적 연구/실험 워크플로

### Checkpoints (Windows / PowerShell)

완료를 말하기 전에 `.harness/checkpoints/default.yml`의 필수 게이트를 실행한다.
Python 도구가 있으면 항상 Clarification Debt를 확인한다.

```powershell
uv run --frozen python -m pytest -q                          # test_optional + 무결성
uv run --frozen ruff check .                                 # lint_optional
uv run --frozen python .harness/scripts/cd_status.py         # clarification_debt
uv run --frozen python .harness/scripts/speckit_status.py    # speckit_optional
```

게이트가 실패하면 완료라고 말하지 않는다. 의도적으로 건너뛴 게이트는 이유와 잔여 위험을 남긴다.

### Review / Hooks

- 리뷰는 `REVIEW.md`를 따른다. PR은 `.github/pull_request_template.md`의 Testing / Risk / How to revert를 채운다.
- `.claude/settings.json`의 PostToolUse 훅이 `.py` 파일을 수정할 때마다 `.harness/scripts/ruff_hook.py`로 Ruff를 실행한다. 실패하면 출력이 돌아오므로 같은 턴에 고친다.
- 같은 Ruff 동작은 Codex의 `.codex/hooks.json`에도 등록되어 있다. Claude는 `file_path`, Codex는 `apply_patch`의 patch command를 보내므로 공통 훅이 두 형식을 처리한다.

### Event / Lesson Logging

correction, redo, scope drift, rollback, 반복 실패가 발생하면 기록한다.

```powershell
uv run --frozen python .harness/scripts/record_event.py <task_id> <event> <score> [note]
```

CD >= 50이면 RCA와 lesson 갱신, CD >= 80이면 새 구현을 중단한다.
