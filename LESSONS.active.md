# LESSONS.active.md

최근 세션에서 바로 적용해야 하는 짧은 규칙만 유지한다.

- 작업 시작 전 `docs/charter.md` 또는 작업별 charter를 확인한다.
- charter가 없으면 구현보다 `docs/charter.template.md` 기반 범위 고정이 먼저다.
- scratch 출력과 임시 산출물은 `.harness/tmp/` 아래에 둔다.
- 새 스택을 도입할 때는 toolchain 확인과 최소 checkpoint를 먼저 추가한다.
- 테스트는 구현 세부를 따라 쓰지 말고, 사용자 관찰 동작과 계약을 검증한다.
- PowerShell 명령 인자에 `$skill-name` 같은 리터럴을 넣을 때는 변수 확장을 피하도록 작은따옴표 또는 이스케이프를 쓴다.
- 에이전트/도구 설정 변경도 작업이다. 파일 3개를 넘으면 charter부터 쓴다.
- 훅과 CI 명령은 설정 파일에 적힌 그대로, 저장소 루트가 아닌 cwd에서도 실행해 검증한다.
