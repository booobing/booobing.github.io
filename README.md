# Codex Project Template

이 저장소는 새 프로젝트를 시작할 때 Codex agent가 바로 일할 수 있도록 준비한 운영형 템플릿입니다.
특정 앱, 백엔드, 모바일, 데이터, 펌웨어 스택을 강제하지 않고, 작업을 시작하고 검증하고 학습하는 공통 루프만 제공합니다.

## What This Template Provides

- `AGENTS.md`: Codex가 따라야 할 저장소 운영 규칙
- `docs/template-capabilities.md`: 이 템플릿이 새 프로젝트에서 수행할 수 있는 역할 설명
- `.codex/agents/`: planner, implementer, reviewer, qa, security reviewer, RCA analyst 역할 정의
- `.agents/skills/`: 로컬 스킬 — `charter-first`, `clarification-gate`, `brainstorm-no-code`, `lean-code-design`, `checkpoint-gate`, `review-synthesizer`, `lesson-logger`, `root-cause-analysis`, `harness-improve`, `python-security-supply-chain`, `research-pipeline`
- `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`: 같은 규칙, 역할, 스킬을 Claude Code에서 쓰기 위한 미러 (`tests/test_mirror_sync.py`가 일치 여부를 검사)
- `.claude/settings.json`, `.codex/hooks.json`: Claude Code와 Codex가 `.py` 파일을 수정할 때마다 같은 Ruff 훅을 실행하는 도구별 등록
- `REVIEW.md`, `.github/pull_request_template.md`: 리뷰 출력 규칙과 PR의 Testing / Risk / How to revert 양식
- `.harness/checkpoints/default.yml`: 프로젝트별 체크포인트를 채워 넣는 기본 게이트
- `.harness/scripts/`: Clarification Debt 기록과 상태 확인 스크립트
- `.harness/spec-kit/codex-template-preset/`: Spec Kit을 템플릿 운영 규칙에 맞게 쓰기 위한 로컬 preset
- `docs/charter.template.md`: 새 작업의 목표, 범위, 체크포인트를 고정하는 템플릿
- `docs/rca.template.md`: 반복 실패나 범위 이탈이 생겼을 때 쓰는 RCA 템플릿
- `tests/test_template_integrity.py`: 템플릿이 특정 프로젝트 잔재 없이 유지되는지 확인하는 테스트

## Start A New Project

1. 이 폴더를 새 프로젝트 이름으로 복사합니다.
2. `pyproject.toml`의 `project.name`을 새 프로젝트 이름으로 바꿉니다.
3. `README.md`를 실제 프로젝트 설명으로 교체하되, Codex 운영 문서는 유지합니다.
4. `docs/charter.template.md`를 복사해 `docs/charter.md`를 만들고 첫 작업의 목표와 non-goals를 채웁니다.
5. 실제 소스 코드는 프로젝트 성격에 맞게 `src/`, `app/`, `packages/`, `backend/`, `frontend/` 등으로 추가합니다.
6. `.harness/checkpoints/default.yml`의 `lint_optional`과 `test_optional` 명령을 실제 스택 명령으로 바꿉니다.
7. 첫 구현 전 `uv run --frozen python .harness/scripts/cd_status.py`로 Clarification Debt 상태를 확인합니다.

## Optional Spec Kit Bridge

Spec Kit을 쓰고 싶다면 이 템플릿을 대체하지 말고 기능 단위 `spec.md`, `plan.md`, `tasks.md` 생성기로 붙입니다.
`AGENTS.md`는 계속 운영 규칙의 최상위 문서이고, `.harness/checkpoints/default.yml`이 완료 게이트입니다.

초기 파일럿은 릴리스 태그에 고정하고 git 자동화 없이 시작하는 방식을 권장합니다.

```powershell
uvx --from git+https://github.com/github/spec-kit.git@v0.8.7 specify init --here --integration codex --integration-options="--skills" --no-git --ignore-agent-tools
specify preset add --dev .harness/spec-kit/codex-template-preset
```

Spec Kit이 초기화된 프로젝트에서는 다음 흐름을 사용합니다.

```text
charter -> speckit specify/clarify -> speckit plan -> speckit tasks -> implementation -> checkpoint -> review -> lesson
```

`.harness/scripts/speckit_status.py`는 `.specify/`가 없으면 건너뛰고, 있으면 기능 산출물의 누락과 `NEEDS CLARIFICATION` 잔여 여부를 점검합니다.

## Optional Research / Experiment Pipeline Automation

이 템플릿의 기본값은 일반 개발 프로젝트용 `charter -> plan -> implementation -> checkpoint -> review -> lesson` 루프입니다.
논문, 실험, 벤치마크, 반복 검증처럼 산출물이 여러 단계에 걸쳐 누적되는 작업을 할 때만 선택적으로 research pipeline을 켭니다.

Research pipeline은 임기응변 메모 대신 재개 가능한 workspace와 `manifest.json`으로 진행 상태를 관리하는 얇은 자동화 레이어입니다.
LaTeX 컴파일, GPU 실행, 외부 모델 호출은 이 MVP의 책임이 아니며, Codex가 각 stage의 실제 산출물을 만든 뒤 manifest를 갱신하는 방식입니다.
일반 개발 프로젝트도 성능 실험, 마이그레이션 검증, 모델 평가처럼 evidence가 쌓이는 작업이라면 이 pipeline을 사용할 수 있습니다.

```powershell
# 새 연구 workspace 생성
uv run --frozen python .harness/scripts/research_pipeline.py run --topic "original: Adaptive Sparse Attention"

# 명시한 workspace에서 stage 시작
uv run --frozen python .harness/scripts/research_pipeline.py start --workspace .harness/tmp/research/{session_id}

# 현재 상태 확인
uv run --frozen python .harness/scripts/research_pipeline.py status --workspace .harness/tmp/research/{session_id}

# 필수 artifact가 생긴 뒤 stage 완료
uv run --frozen python .harness/scripts/research_pipeline.py complete --workspace .harness/tmp/research/{session_id}

# 실패 또는 중단 후 재개 지점 확인
uv run --frozen python .harness/scripts/research_pipeline.py resume --workspace .harness/tmp/research/{session_id}
```

기본 stage 순서는 다음과 같습니다.

```text
ideation -> planning -> setup -> coding -> execution -> analysis -> figure_gen -> writing -> review
```

`original: Topic`, `survey:short: Topic`, `survey:standard: Topic`, `survey:long: Topic` 접두사는 manifest의 paper mode로 기록됩니다.
각 stage는 필수 artifact가 workspace 안에 존재해야 완료할 수 있으므로, 실제 실행 결과가 없는 숫자, 표, 그림을 완료 산출물처럼 통과시키지 않습니다.

## Recommended Codex Flow

1. Charter first: 작업 목표, non-goals, touched files, required checkpoints를 먼저 고정합니다.
2. Specify/Plan: Spec Kit을 쓰는 프로젝트라면 기능 spec, plan, tasks를 생성하고, 쓰지 않는 프로젝트라면 기존 implementation plan을 작성합니다.
3. Implement: 승인된 범위 안에서 최소 diff로 수정합니다.
4. Checkpoint: `.harness/checkpoints/default.yml`에 적힌 게이트를 실행합니다.
5. Review: reviewer와 qa 관점으로 계약 위반, 회귀, 테스트 누락을 확인합니다.
6. Learn: correction, redo, out-of-bounds edit가 있으면 lesson 또는 RCA로 남깁니다.

## Checkpoints

템플릿 기본 체크포인트는 스택 중립입니다.

```bash
uv sync --frozen
uv run --frozen ruff check .
uv run --frozen python -m pytest -q
uv run --frozen python .harness/scripts/speckit_status.py
uv run --frozen python .harness/scripts/cd_status.py
```

프로젝트가 생기면 다음 명령을 실제 명령으로 교체하세요.

- `lint_optional`: 예를 들어 `npm run lint`, `ruff check .`, `cargo clippy`
- `test_optional`: 예를 들어 `npm test`, `pytest`, `cargo test`
- `speckit_optional`: `.specify/`가 있는 프로젝트에서 Spec Kit 산출물 상태 검사
- `repo_cleanliness_review`: 프로젝트 고유 산출물, 캐시, 샘플 데이터 추적 여부 검사

## Where Project Files Belong

- Product specs: `docs/` 또는 프로젝트가 정한 `specs/`
- Source code: 프로젝트 스택에 맞는 루트 디렉터리
- Tests: `tests/` 또는 스택 표준 테스트 디렉터리
- Temporary output: `.harness/tmp/`
- Tool caches: `.harness/*-cache/`, `.cache/`, `.ruff_cache/`
- Long-lived lessons: `.harness/memory/lessons-learned.md`

템플릿 자체에는 샘플 앱 코드를 넣지 않습니다. 새 프로젝트의 첫 charter가 실제 구조를 결정합니다.
