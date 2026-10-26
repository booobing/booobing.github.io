# Template Capabilities

이 문서는 현재 `codex_project_template`가 새 프로젝트에서 어떤 역할을 할 수 있는지 설명한다.
이 템플릿은 앱 구조나 기술 스택을 미리 정하는 시작점이 아니라, Codex agent가 일관된 절차로 계획, 구현, 검증, 회고를 수행하도록 돕는 운영 기반이다.

## Primary Role

이 템플릿의 핵심 역할은 프로젝트 초기에 비어 있는 코드베이스에도 작업 질서를 먼저 세우는 것이다.
새 프로젝트는 보통 목표, 범위, 검증 방법, 의사결정 기록이 흩어지기 쉽다.
이 템플릿은 그 부분을 `charter -> plan -> implementation -> checkpoint -> review -> lesson` 흐름으로 고정한다.

## What It Can Do

### 1. 작업 시작 범위를 고정한다

`docs/charter.template.md`는 새 작업을 시작하기 전에 목표, non-goals, 수정 대상, 체크포인트를 정리하게 만든다.
이를 통해 Codex가 요청 밖의 파일을 임의로 확장해서 수정하지 않도록 한다.

사용 방식:

1. `docs/charter.template.md`를 복사해 `docs/charter.md`를 만든다.
2. 이번 작업의 목표와 제외 범위를 적는다.
3. 필요한 체크포인트와 수정 예상 파일을 적는다.
4. Codex 작업은 이 문서를 기준으로 진행한다.

### 2. 역할별 agent 작업을 분리한다

`.codex/agents/`에는 작업 성격에 맞춘 역할 정의가 들어 있다.
각 역할은 같은 저장소를 보더라도 다른 관점으로 판단하도록 설계되어 있다.

- `planner`: 목표, non-goals, 모호성, 난이도, 체크포인트를 먼저 정리한다.
- `implementer`: 승인된 범위 안에서 코드나 문서를 수정한다.
- `reviewer`: 계약 위반, 회귀, 범위 확장, 테스트 누락을 찾는다.
- `qa`: 수용 시나리오, 경계 조건, 실패 모드, 산출물 위생을 점검한다.
- `security_reviewer`: 비밀값, 위험한 입출력, 의존성, 배포 위험을 확인한다.
- `rca_analyst`: 반복 실패나 범위 이탈의 원인과 예방 규칙을 정리한다.

### 3. 스택 중립 체크포인트를 제공한다

`.harness/checkpoints/default.yml`은 특정 언어나 프레임워크에 묶이지 않는 기본 게이트를 제공한다.
처음에는 템플릿 자체 검증에 맞춰져 있고, 실제 프로젝트가 생기면 명령만 교체하면 된다.

기본 게이트:

- `charter_exists`: charter가 존재하는지 확인한다.
- `repo_cleanliness_review`: 템플릿 잔재, 캐시, 생성물을 잘못 추적하지 않는지 확인한다.
- `lint_optional`: 현재 프로젝트의 정적 검사를 실행한다.
- `test_optional`: 현재 프로젝트의 테스트를 실행한다.
- `clarification_debt`: 모호성 누적 상태를 확인한다.

### 4. Clarification Debt를 추적한다

`.harness/scripts/record_event.py`와 `.harness/scripts/cd_status.py`는 작업 중 생기는 모호성, 수정 요청, 재작업, 범위 이탈을 점수화한다.
점수가 커지면 새 구현을 계속 밀어붙이기보다 RCA와 lesson 정리를 먼저 하도록 신호를 준다.

기록 대상 예시:

- 요구사항 확인이 필요한 경우
- 작업을 다시 해야 하는 경우
- 잘못된 가정으로 수정이 틀어진 경우
- charter 없이 구현을 시작한 경우
- 요청 범위를 넘어선 파일을 수정한 경우

### 5. RCA와 lesson 흐름을 제공한다

`docs/rca.template.md`, `LESSONS.active.md`, `.harness/memory/lessons-learned.md`는 반복되는 실패를 저장소의 운영 지식으로 남기기 위한 자리다.
이 템플릿은 단순히 문제를 고치는 데서 끝나지 않고, 다음 작업에서 같은 실수를 줄이도록 회고 문서를 남기는 흐름을 제공한다.

RCA가 제안한 예방 규칙을 지침, 스킬, 스크립트, 훅, 체크포인트에 반영할 때는 `harness-improve` 스킬로 같은 작업을 다시 실행해 전후를 비교하고, 근거가 있는 변경만 남긴다.
예방 규칙은 강제력이 높은 장치(hook > script > checkpoint > skill > 문장 규칙)부터 고른다. 이 흐름은 Harness²(Google Research, 2026)의 Propose -> Probe -> Compose를 가볍게 옮긴 것이다.

### 6. 템플릿 무결성을 검증한다

`tests/test_template_integrity.py`는 이 저장소가 특정 프로젝트 잔재 없이 템플릿 상태를 유지하는지 확인한다.
필수 파일 존재, 제거되어야 할 경로, 추적되면 안 되는 캐시, 이전 프로젝트 키워드 유입을 검사한다.

실행 명령:

```bash
uv run --frozen python -m pytest -q
```

### 7. 프로젝트별 구조를 받아들일 준비를 한다

이 템플릿은 실제 소스 디렉터리를 미리 만들지 않는다.
대신 프로젝트 성격에 맞게 `src/`, `app/`, `packages/`, `services/`, `docs/`, `tests/` 같은 구조를 나중에 선택할 수 있게 비워 둔다.
새 구조가 결정되면 charter와 checkpoint에 그 규칙을 반영한다.

### 8. Spec Kit을 기능 단위 산출물 엔진으로 붙인다

`.harness/spec-kit/codex-template-preset/`은 Spec Kit을 이 템플릿의 운영 철학에 맞게 쓰기 위한 로컬 preset이다.
이 preset은 Spec Kit의 constitution, spec, plan, tasks 템플릿을 교체해서 다음 원칙을 고정한다.

- `AGENTS.md`가 운영 규칙의 최상위 문서다.
- `.specify/memory/constitution.md`는 운영 규칙의 원본이 아니라 요약 미러다.
- `spec.md`, `plan.md`, `tasks.md`는 기능 단위 계획 산출물이다.
- 완료 선언은 `.harness/checkpoints/default.yml`과 review/lesson 흐름을 기준으로 한다.

사용 방식:

```powershell
uvx --from git+https://github.com/github/spec-kit.git@v0.8.7 specify init --here --integration codex --integration-options="--skills" --no-git --ignore-agent-tools
specify preset add --dev .harness/spec-kit/codex-template-preset
```

`.harness/scripts/speckit_status.py`는 `.specify/`가 없으면 `STATUS=SKIPPED`를 반환하고, 있으면 기능 산출물의 누락과 `NEEDS CLARIFICATION` 잔여 여부를 검사한다.

## What It Does Not Do

이 템플릿은 다음을 제공하지 않는다.

- 샘플 애플리케이션 코드
- 특정 언어, 런타임, 프레임워크 강제
- 제품 기획서 자동 작성
- 테스트 전략 자동 완성
- 배포 환경 자동 구성
- Spec Kit 자체를 vendoring하거나 community extension/preset을 자동 설치
- 보안 검토를 대체하는 완전한 감사

이 템플릿은 프로젝트를 대신 설계하지 않는다.
대신 설계와 구현이 기록 가능한 순서로 진행되도록 작업 레일을 깔아 둔다.

## Recommended Use Cases

이 템플릿은 다음 상황에 특히 적합하다.

- 새 프로젝트를 시작하기 전에 Codex 작업 규칙을 먼저 정하고 싶을 때
- 여러 agent 역할을 나눠 계획, 구현, 검토를 운영하고 싶을 때
- 작업 범위 이탈과 반복 재작업을 줄이고 싶을 때
- 프로젝트별 체크포인트를 점진적으로 추가하고 싶을 때
- 실패 원인과 학습 내용을 저장소 안에 남기고 싶을 때

## First Customization Checklist

새 프로젝트로 복사한 뒤 최소한 다음 항목을 채운다.

1. `pyproject.toml`의 프로젝트 이름을 바꾼다.
2. `README.md`를 실제 프로젝트 소개로 바꾼다.
3. `docs/charter.md`를 만들고 첫 작업의 목표와 non-goals를 적는다.
4. `.harness/checkpoints/default.yml`의 lint와 test 명령을 실제 명령으로 교체한다.
5. 실제 소스와 테스트 디렉터리를 프로젝트 성격에 맞게 만든다.
6. `tests/test_template_integrity.py`에서 새 프로젝트에 맞지 않는 템플릿 전용 검사를 조정한다.
7. 첫 작업이 끝나면 체크포인트 결과와 필요한 lesson을 남긴다.

## Operating Principle

이 템플릿의 기준은 빠른 생성보다 신뢰 가능한 반복이다.
Codex가 새 프로젝트에서도 같은 방식으로 시작하고, 멈추고, 확인하고, 배울 수 있게 만드는 것이 이 저장소의 가장 중요한 역할이다.
