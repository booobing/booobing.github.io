---
name: harness-improve
description: Trigger when an RCA, a repeated lesson, or a recurring review finding proposes changing AGENTS.md, a skill, a subagent, a script, a hook, or a checkpoint. Tests the change on the same task before keeping it. Not for ordinary feature work.
---

# Goal
모델이 아니라 이 저장소의 harness(지침, 메모리, 스킬, 서브에이전트, 스크립트, 훅, 체크포인트)를 고친다.
고친 것이 실제로 행동을 바꿨는지 같은 작업으로 확인한 뒤에만 남긴다. (Harness²의 Propose -> Probe -> Compose)

# Steps
0. Charter: 고칠 harness 파일(미러 포함)을 charter의 touched files에 먼저 넣는다. 진행 중인 작업 charter 밖이면 charter를 확장하거나 별도 charter를 만든다.
1. Reference: 실패한 실행의 증거를 모은다. 실행 명령과 출력, 체크포인트 결과, `session-events.jsonl`, RCA 문서.
2. Propose: 후보를 최대 2개 만든다.
   - invariant: 어느 작업에서나 반복될 결함 (범위 고정, 계획, 검증, 도구 사용)
   - domain: 이 스택이나 영역에만 해당하는 지식과 절차
   - 각 후보에 고칠 component와 diff 요약을 적는다. 강제력이 높은 장치부터 고른다: hook > script > checkpoint > skill > 문장 규칙.
3. Probe: 같은 작업이나 재현 명령을 같은 조건으로 다시 실행해 전후를 비교한다.
   - 결함이 사라졌는가 / 그대로인가 / 다른 회귀가 생겼는가
   - CD >= 80(HALT)이면 재실행은 진단 목적으로만 하고, harness 편집은 새 charter에서 한다.
   - 행동 차이는 품질의 증거가 아니다. 결과는 `checkpoint-gate`로 따로 확인한다.
4. Compose: 근거가 있는 변경만 남긴다. 합치기, 하나만 채택, 아무것도 남기지 않기 모두 가능하다. 각 결정에 관찰한 근거를 단다.
5. Record: `.harness/memory/lessons-learned.md`에 Scope / Component / Evidence를 포함해 기록한다.
   - invariant는 `LESSONS.active.md` 후보, domain은 해당 스킬에 반영한다.
   - 근거가 없는 harness 변경은 교훈으로 기록하지 않는다. 이 규칙은 harness 변경에만 적용되며, CD >= 50일 때 필수인 RCA와 실패 기록(Symptom, Root cause, Evidence = 재현된 실패)은 그대로 남긴다.

# Rules
- 한 번에 고치는 component는 최소로 한다. codex/Claude 미러(`.agents`/`.claude`, `.codex/agents`/`.claude/agents`)는 함께 고친다.
- 비용이나 외부 의존 때문에 다시 실행할 수 없으면 변경을 적용하지 않는다. 건너뛴 이유와 함께 `candidate`로만 기록하고, 다음에 재현할 수 있을 때 다시 Probe한다.
- 권한 확대, 체크포인트 약화, 검증 생략으로 결함을 "해결"하지 않는다.
- 변경은 charter의 touched files 안에서만 한다.

# Output
- reference failure
- candidates: scope, component, diff summary
- probe result per candidate
- kept / dropped / candidate, with evidence
- lesson entry, or "no entry: insufficient evidence"
