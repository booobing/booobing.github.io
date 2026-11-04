# AGENTS.md

## Mission
Codex는 이 저장소에서 즉흥적으로 구현하지 않고, **charter -> plan -> implementation -> checkpoint -> review -> lesson** 루프로 움직인다.
정답을 추측하지 말고, 현재 저장소의 문서, 테스트, 코드, 체크포인트를 진실의 원천으로 삼아라.

## Hard Rules
1. **Conservative edits**: 요청을 만족하는 최소 diff를 선호한다.
2. **Charter first**: 구현 전 목표, non-goals, touched files, required checkpoints를 확인한다.
3. **No guessing**: 중요한 ambiguity는 명시하고, 필요하면 clarification protocol을 따른다.
4. **Stay in bounds**: charter 또는 사용자 요청 밖의 파일을 임의로 수정하지 않는다.
5. **Checkpoint discipline**: 완료를 말하기 전에 해당 작업의 게이트를 실행하거나, 실행하지 못한 이유를 남긴다.
6. **Log corrections**: correction, redo, scope drift, rollback, 반복 실패는 lesson 또는 RCA 후보로 남긴다.
7. **No history rewriting**: 명시 요청 없이 rebase, amend, force-push, hard reset을 하지 않는다.

## Session Start Checklist
- `docs/charter.md` 또는 작업별 charter가 있는지 확인한다.
- 없으면 `docs/charter.template.md` 기준으로 목표와 범위를 먼저 정한다.
- `LESSONS.active.md`와 관련 하위 `AGENTS.override.md`가 있는지 확인한다.
- ambiguity와 difficulty를 판정한다.
- touched files와 non-goals를 작업 전에 적는다.

## Clarification Protocol
- **LOW ambiguity**: 진행하되 가정을 명시한다.
- **MEDIUM ambiguity**: 2-3개의 선택지를 제시하고 가장 보수적인 옵션을 추천한다.
- **HIGH ambiguity**: 구현을 멈추고 charter 보강, 설계, RCA 중 필요한 작업부터 수행한다.

## Difficulty Guide
- **Simple**: 파일 1-3개, 기존 패턴 복사, 단순 로직. 단일 agent와 기본 checkpoint로 충분하다.
- **Medium**: 한 개 이상의 모듈 경계, 테스트 추가, 리팩터 포함. planner, implementer, reviewer 관점이 필요하다.
- **Complex**: 여러 시스템 경계, 데이터/보안/성능/배포 영향. explorer, qa, security, RCA 관점을 분리한다.

## Clarification Debt
다음 이벤트가 발생하면 `.harness/scripts/record_event.py`로 기록한다.

- `clarify`: +10
- `correct`: +25
- `redo`: +40
- `started_without_charter`: +15
- `out_of_bounds_edit`: +20
- repeated error multiplier: x1.5

규칙:
- CD >= 50: RCA를 수행하고 lesson을 갱신한다.
- CD >= 80: 새 구현을 중단하고 진단과 정리만 수행한다.

사용자가 원인 조치·재발 방지 반영과 계속 진행을 명시하면, 해당 작업 charter에 승인 문구·정확한 범위·RCA·재발 방지 검증을 연결해 그 범위만 예외로 진행한다. 원래 점수·이력·임계치와 `cd_status.py`의 결과는 보존하고, 승인된 동일 범위의 재승인을 반복 요구하지 않는다. 예외는 다른 작업으로 자동 확장하지 않으며 나머지 체크포인트를 생략하거나 실패를 통과로 표시하지 않는다.

## Required Artifacts Per Task
- charter 또는 charter 업데이트
- implementation plan
- checkpoint result
- session event log, 필요한 경우
- RCA, 필요한 경우
- lesson update, 필요한 경우

## Spec Kit Bridge
- `AGENTS.md`가 운영 규칙의 최상위 진실의 원천이다.
- `.specify/memory/constitution.md`는 `AGENTS.md`와 `LESSONS.active.md`의 안정된 원칙을 요약하는 미러로만 운용한다.
- Spec Kit 산출물(`spec.md`, `plan.md`, `tasks.md`)은 기능 단위 계획 산출물이며 완료 게이트가 아니다.
- 완료 선언은 `.harness/checkpoints/default.yml`을 기준으로 한다.
- community extension 또는 preset은 프로젝트에서 명시 승인하기 전까지 설치하지 않는다.

## Review Priorities
1. 계약, 스펙, charter 불일치
2. 사용자 요청 밖의 범위 확장
3. 데이터 손상, 보안, 롤백 위험
4. 테스트 누락 또는 자기충족적 테스트
5. 유지보수성을 낮추는 구조 변화

출력 형식, 이 저장소의 실패 유형, 리뷰 반복 제한은 `REVIEW.md`를 따른다.

## Skill Routing
긴 절차를 이 파일에 늘리지 않는다.
반복되는 작업은 `.agents/skills/*`로 라우팅하고, 실행 가능한 부분은 `.harness/scripts/`에 둔다.
코드 설계, 구현 계획, 리팩터링, 버그 수정의 범위를 잡을 때는 `.agents/skills/lean-code-design`을 참고해 과잉 설계를 먼저 제거하되, charter와 checkpoint 규칙을 우선한다.
RCA, 반복 교훈, 반복 리뷰 지적이 이 파일이나 스킬, 스크립트, 훅, 체크포인트의 변경을 제안하면 `.agents/skills/harness-improve`로 같은 작업을 다시 실행해 전후를 비교하고, 근거가 있는 변경만 남긴다.
Claude Code와 Codex가 모두 쓰는 저장소 훅은 `.claude/settings.json`과 `.codex/hooks.json`에 각각 등록하고, 공통 로직은 `.harness/scripts/`에 둔다.
