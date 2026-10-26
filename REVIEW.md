# REVIEW.md

리뷰어(사람, `reviewer` 에이전트, `/code-review`, codex review)가 따르는 규칙이다.
우선순위는 `AGENTS.md`의 Review Priorities를 따르고, 이 문서는 출력 방식과 이 저장소의 실패 유형만 정한다.

## Output
- 요약 첫 줄은 발견 건수다. 고칠 것이 없으면 "수정할 것 없음"이라고 명확히 쓴다.
- 모든 발견은 `file:line` 근거를 단다. 이름만 보고 추측하지 않는다.
- 각 발견에 등급을 붙인다.
  - `Important`: 병합 전에 고쳐야 하는 문제
  - `Nit`: 고치면 좋은 사소한 문제. 최대 3개까지만 쓴다.
  - `Pre-existing`: 이번 변경 전부터 있던 문제. 이번 변경 작성자의 잘못처럼 쓰지 않는다.
- 한 줄이 아니라 버그 유형을 지적하고, 같은 유형의 다른 사례를 함께 나열한다.
- 스타일, 진단 메시지, 정리에만 관련된 지적은 버그를 숨기는 경우가 아니면 쓰지 않는다.

## Failure Types In This Repository
- 범위 이탈: charter의 touched files 밖을 수정한다.
- 문서가 잘못된 정보를 전달한다: `README.md`, `CLAUDE.md`, `docs/`의 명령과 경로가 실제 파일이나 `.harness/checkpoints/default.yml`과 다르다.
- 설정이 잘못된 경로로 보낸다: 체크포인트, CI, 훅이 존재하지 않는 명령이나 경로를 실행한다.
- codex/Claude 미러 불일치: `.agents/skills/*`와 `.claude/skills/*`, `.codex/agents/*.toml`과 `.claude/agents/*.md`의 지침 내용이 다르다.
- 자기충족적 테스트: 구현을 그대로 따라 쓴 assertion만 있다.
- 템플릿 오염: 캐시, 생성물, 이전 프로젝트 잔재가 추적된다.
- 비밀값 노출이나 workflow 권한 확대.

## Excluded Paths
`.venv/`, `.ruff_cache/`, `.harness/uv-cache/`, `.harness/tmp/`, `.harness/memory/session-events.jsonl`

## Review Loop Limit
- 같은 변경에 리뷰와 수정이 3회를 넘으면 리뷰를 멈추고 접근 방식 자체를 재검토하도록 요청한다.
- 2회차부터는 직전 리뷰 이후의 새 변경분만 리뷰한다.
- 이미 낸 지적은 반복하지 않는다.
