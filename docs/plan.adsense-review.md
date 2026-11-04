# AdSense review diagnosis (2026-11-05)

## Charter

- Objective: 사용자가 전달한 ‘게시자 콘텐츠가 없는 화면’ 거절 알림을 공개 배포본·코드·공식 정책과 대조하고 최소 수정안을 작성한다.
- Non-goals: 이 진단 단계에서 제품 코드 수정, 광고 계정 설정 변경, 재검토 신청, 커밋·푸시·배포, 승인 보장, 운영 규칙 변경 없음.
- Touched files: `docs/plan.adsense-review.md`, `.harness/memory/lessons-learned.md`, 무시되는 `.harness/memory/session-events.jsonl`과 `.harness/tmp/adsense-live-20261105.html`.
- Ambiguity: 진단 LOW. Google이 지적한 정확한 URL·화면과 자동 광고 설정은 알림에서 확인할 수 없어 심사 내부 원인은 단정하지 않는다.
- Difficulty: Simple for diagnosis. Product implementation would be Medium, with sequential planning, implementation, and review perspectives in one agent.
- Required checkpoints: 실제 공개 HTML/JS 읽기, 정책 원문 대조, 진단 문서 범위·공백 확인, CD 상태 확인. 코드·운영 설정 변경이 없는 단계에서는 제품 테스트를 생략한다.
- Authorization boundary: CD 245 / HALT. 기존 사용자 예외 ‘이번 효과 수정은 계속 진행’은 책 시각 효과에 한정되므로 광고 심사 대응 구현에 확대하지 않는다. 이번 correction +25 기록 후 CD 270 / HALT. 구현은 이번 수정에 대한 예외 승인 후 진행한다.
- Rollback plan: 이번 진단 문서와 실패 lesson 추가분만 되돌릴 수 있다. 사용자 변경·기존 문서와 이벤트 이력은 보존한다.

## Evidence

- 공개 주소 `https://booobing.github.io/?policy-check=20261105`는 HTTP 200을 반환했다. HTML 7,729 bytes. 스냅샷은 위 임시 파일에 보관했다.
- 공개 `game.js?v=dd2731548dd8`도 HTTP 200이며 로컬 `web/game.js`와 내용이 일치한다. 따라서 로컬 코드의 아래 동작은 현재 배포본에도 해당한다.
- `web/index.html:28`의 소개는 한 문장이다. `web/index.html:47`의 결과 사진은 처음에 hidden이며 사진 URL은 사용자 조작 후 JavaScript에서 선택한다. 이용 안내는 `web/index.html:99`의 닫힌 dialog에 있다. 이는 초기 상태에 게임의 사진·설명이 충분히 노출되지 않는 근거이며, Google이 JavaScript를 전혀 읽지 못한다는 증거는 아니다.
- `web/index.html:68`, `web/index.html:86`, `web/index.html:87`에는 배너 자리·테스트 모드·테스트 광고 보기 UI가 있다. 공개 HTML에 ‘테스트’가 9회 나온다. 단어 자체가 위반이라는 뜻은 아니며 실제 테스트 흐름이 공개된 상태다.
- `web/index.html:12`에 AdSense 외부 스크립트가 있지만 `data-ad-slot`은 없다. 계정의 자동 광고 설정은 읽지 않았으므로 광고가 실제 어디에 표시되었는지는 확정하지 않는다.
- `web/index.html:108`의 ‘추적 광고를 사용하지 않아요’ 안내는 Google 광고 스크립트를 넣은 현재 구현에 맞춰 재검토해야 한다. 별도의 개인정보처리방침 HTML 또는 링크는 현재 없다. 이 부분은 이번 알림에서 직접 지적된 원인이라고 단정하지 않는 별도 발견이다.
- `web/game.js:237`과 `web/game.js:241`은 테스트 완료 버튼으로 재시도 권리를 지급한다. 실제 광고 시청 확인 API는 없다.
- `tests/web-game.mjs:375`는 외부 요청 0개를 기대하지만 현재 HTML은 Google 스크립트를 요청한다. 기존 66개 통과 결과는 해당 스크립트를 추가하기 전의 결과다. 이번에 다시 통과했다고 보고하지 않는다.

## Official policy comparison

- 콘텐츠가 없거나 가치가 낮은 화면, 미완성 화면, 알림·탐색·행동 목적 화면에는 Google 광고를 게재할 수 없다. 직접 검토·선별하지 않은 자동 생성 콘텐츠도 해당한다. 현재 사진 목록에는 사람이 인원수를 확인한 기록이 있으므로 AI 생성 자체만으로 거절 원인을 단정하지 않는다. [게시자 콘텐츠가 없는 화면](https://support.google.com/publisherpolicies/answer/11112688?hl=ko)
- 비보상형 광고의 클릭·조회 대가로 보상을 제공해서는 안 된다. 일반 AdSense 배너를 일정 시간 보여주거나 클릭했다는 이유로 재시도 권리를 주는 방식은 계획하지 않는다. 정식 보상형 광고는 별도 제품·계정 자격·공식 완료 이벤트가 필요하다. [애드센스 프로그램 정책](https://support.google.com/adsense/answer/48182?hl=ko), [Ad Placement API 가입](https://developers.google.com/ad-placement/docs/signup)
- Google 광고 사용 시 개인정보처리방침에는 Google·제3자 광고 제공자의 쿠키 사용과 맞춤 광고 거부 방법 등을 안내해야 한다. [필수 콘텐츠](https://support.google.com/adsense/answer/1348695?hl=ko)
- AdSense는 소유권 연결에 광고 스크립트 외에 계정 메타 태그도 지원한다. 광고를 아직 송출하지 않는 단계에서는 현재 게시자 ID를 유지한 메타 태그를 사용하는 방안을 검토한다. 실제 송출을 시작하면 필요한 SDK·개인정보 및 동의 설정을 별도로 적용한다. [사이트 연결](https://support.google.com/adsense/answer/7584263?hl=ko)

## Root cause analysis

1. Symptom: 사이트가 ‘게시자 콘텐츠가 없는 화면에 Google 게재 광고’ 사유로 거절되었다.
2. Root cause: 확인 가능한 준비상 결함은 테스트판의 숨겨진 사진·간단한 초기 설명·데모 광고 흐름을 유지한 채 소유권 확인 스크립트를 게시한 것이다. 기능·배포 성공을 광고 심사 준비 완료와 별도로 판단하지 못했다. Google 내부의 특정 판정 원인은 미확인이다.
3. First missed signal: 공개 HTML에 테스트 광고와 ‘추적 광고 없음’ 안내가 남아 있었으며 별도 개인정보 안내가 없었다.
4. Prevention rule (domain): 광고 스크립트 게시 전 실제 공개 초기 화면의 콘텐츠·사용 가능한 기능·개인정보 설명·보상형 광고 제품 적합성을 점검하고 소유권 확인과 심사 준비를 구분한다.
5. Component: memory. 운영 스킬·훅·체크포인트·AGENTS 변경은 제안하거나 적용하지 않는다.
6. One-line lesson: 소유권 확인 코드 배포 성공은 콘텐츠와 광고 운영이 심사 가능한 상태라는 증거가 아니다.

## Proposed implementation after a scoped exception

- Selected rung: 기존 정적 HTML/CSS/JS와 검수된 사진 자산을 재사용한다. 서버·프레임워크·외부 의존성은 추가하지 않는다.
- 첫 화면의 책 연출은 유지한다. 그 아래에 실제 게임 설명, 이용 방법, 사진 제작·인원수 확인 방법과 검수된 사진 예시를 정적 HTML로 제공한다. 제목·설명만 반복하여 분량을 채우지 않는다. 예시 사진은 지연 로딩하고 기존 첫 전송 용량을 확인한다.
- 공개판의 테스트 배너·가짜 시청 완료 흐름을 정리한다. 광고 연동 전 임시 재시도 방식은 사용자와 확정한다. 초기 요구의 첫 무료·이후 보상형 광고 규칙을 허락 없이 바꾸지 않는다. 일반 배너를 재시도 보상에 사용하지 않는다.
- 개인정보 안내는 실제 동작과 일치하도록 별도 문서와 상시 링크를 둔다. 운영자 문의 경로는 기존 공개 연락처를 확인하거나 사용자에게 받아 작성하며 임의로 만들지 않는다.
- 실제 광고가 준비되지 않은 기간에는 광고 스크립트 대신 계정 확인 메타 태그를 사용하는 방안을 적용 범위에 포함한다. 메타 태그는 콘텐츠 보강을 대체하지 않는다. 운영 광고는 콘텐츠 화면에서만 표시하고 로딩·오류·전환·단순 확인 화면과 게임 버튼을 피하도록 별도 검증한다.
- Expected product files: `web/index.html`, `web/styles.css`, `web/game.js`, `web/privacy.html`, `tests/web-game.mjs`, 관련 제품 안내 문서. 실제 구현 전 최종 범위와 임시 재시도 동작을 고정한다. `web/photos.js`와 100개 원본 자산·책 영상은 유지한다.
- Validation: 초기 콘텐츠가 조작 없이 보이는지, 모바일 배치와 링크, 무료/재시도·오류 복구와 기존 영상, 광고 요청/문구의 실제 일치, 외부 요청 검사 계약, 용량과 적용 가능한 기본 체크포인트. 승인 전후에 크롤러와 일반 사용자에게 다른 콘텐츠를 제공하지 않는다.
- 재검토 신청은 구현·검증·공개 반영 후에만 진행한다. 이 변경안은 승인 확률이나 승인을 보장하지 않는다.

## Checkpoint and review

- Public HTML/JS read: PASS. HTTP 200과 로컬 JS 일치 확인.
- Policy comparison: PASS for accessible official policy, site connection, and privacy pages. 사용자가 링크한 `11036238` 문서는 웹 도구에서 접근 실패하여 그 문서의 상세 내용을 근거로 사용하지 않았다.
- Charter and changed-file scope: PASS. 진단 문서·실패 기록에 한정하며 제품 코드는 변경하지 않았다.
- `git diff --check` and diagnosis text checks: PASS. Charter·필수 진단 절·공백 검사를 통과했다. `git diff --exit-code -- web .github`도 PASS로 제품·배포 코드를 변경하지 않았음을 확인했다.
- Clarification debt: FAIL / HALT, actual CD 270.0, exit 1. 이 진단은 완료해도 제품 수정·정책 문제 해결 완료로 표시하지 않는다. 가용 `.venv/Scripts/python.exe`로 저장소의 `cd_status.py`를 실행했으며 uv 환경 동기화는 필요하지 않았다.
- Skipped: Ruff/Python test suite/Spec Kit/JS syntax/browser game suite. 진단 문서만 변경했으므로 실행하지 않았다. 기존 외부 요청 테스트와 새 AdSense 스크립트의 계약 불일치는 제품 수정 시 해결해야 한다.
- Review findings on new diagnostic changes: 수정할 것 없음. 실제 심사 내부 원인과 자동 광고 상태를 사실로 단정하지 않았고 새 제품 구현·배포를 하지 않았다. 기존 제품 결함은 Evidence 절의 파일·행 근거로 분리했다.
- Smallest next action: 이번 광고 심사 대응에 한정한 구현 중단 예외를 사용자에게 요청한다. 승인 후 광고 미연동 기간의 재시도 방식과 실제 문의 경로를 확정하고 위 최소 수정안을 구현한다.

## Authorized implementation charter (2026-11-05)

- User authorization: ‘뭐하느라 그렇게 쌓였냐 초기화 하는 대신에 다시 반복 안하도록 반영하고 진행해’. 이번 광고 심사 대응과 그 재발 방지 반영을 진행한다. 추가 확인 없이 구현·검증 후 기존 `pages` 원격으로 공개 반영한다. 재검토 신청과 광고 계정 설정은 이번 범위 밖이다.
- Confirmed interim replay: ‘광고 연결 전까지 무료로 반복 이용’. 보상형 광고 미연동 기간의 데모 광고·광고 게이트를 제거하고 모든 펼치기를 무료로 제공한다.
- Objective: 공개 초기 콘텐츠와 사진 예시를 제공하고, 실제로 작동하는 무료 재시도·정확한 개인정보 안내·광고 없는 계정 확인을 구현한다. 기록을 초기화하지 않고 승인·교정·검증을 연결해 동일 실패를 방지한다.
- Touched files: `AGENTS.md`, `CLAUDE.md`, `LESSONS.active.md`, `.harness/memory/lessons-learned.md`, `docs/plan.adsense-review.md`, `docs/game.md`, `progress.md`, `web/index.html`, `web/styles.css`, `web/game.js`, `web/privacy.html`, `web/assets/preview-*.webp`, `tests/web-game.mjs`; 무시되는 세션 이벤트와 `.harness/tmp/` 검증 산출물.
- Non-goals: CD 점수·이력·임계치·상태 판정 코드 변경, 기본 체크포인트 약화, 실제 광고 송출·계정 설정·재검토 신청, 새 의존성, 사진 카탈로그·검수 인원수·책 영상 변경, 기존 미커밋 작업 일괄 커밋 없음.
- Validation publishing dependency: 변경한 `tests/web-game.mjs`는 기존 `docs/photos.manifest.json`의 검수 기록을 읽는다. 재현 가능한 검증을 위해 이 기존 기록을 선택적으로 함께 커밋한다. 카탈로그나 기록 내용은 변경하지 않는다. 다른 이전 미커밋 계획·운영 변경은 포함하지 않는다.
- Additional touched file: `.harness/checkpoints/default.yml`의 기존 미커밋 게임 게이트 4줄도 선택적으로 포함한다. 실제 검증한 JS 구문·게임 브라우저 검사가 이후 기본 게이트에서 빠지지 않게 연결하며 기존 필수 검사를 제거하지 않는다.
- Design rung: 기존 DOM·CSS·사진 재사용. 예시용 작은 WebP만 파생하고 별도 프레임워크·서버를 추가하지 않는다. 사용하지 않는 데모 광고 코드는 삭제한다. 기존 세션의 직전 사진 기록은 유지하고 사용하지 않는 광고 권리는 더 이상 읽거나 지급하지 않는다.
- Visual thesis: 고딕 회랑·떠 있는 책·금빛을 유지하고 책 아래에 차분한 사진 기록과 설명을 배치한다.
- Content plan: 기존 게임 → 이용 방법 → 사진 예시 3개 → 제작·검수 설명 → 개인정보·문의 링크. 초기 HTML에 콘텐츠를 직접 넣고 예시 사진은 작은 파일·지연 로딩을 사용한다.
- Interaction thesis: 기존 부유·hover 입자·영상 1.45초 사진 공개를 유지한다. 추가 설명과 개인정보 링크는 JavaScript 없이도 탐색할 수 있다.
- Required checkpoints: 새 정책 준비 검사에서 기존 배포 HTML 실패 재현 → 동일 검사 통과, 기존 영상·로비·모바일·오류·세션·무작위 동작 브라우저 회귀, 기본 게임 클라이언트와 스크린샷 직접 확인, JS 구문·해시·용량·Ruff·pytest·Spec Kit·CD·diff 검사, 독립적인 최종 리뷰 관점, 공개 반영 후 실제 HTML/JS/개인정보 확인.
- Rollback: 이번 제품/지침 변경만 새 커밋으로 되돌릴 수 있다. 이벤트를 삭제하거나 Git 이력을 재작성하지 않는다.

### Harness improvement proposal and probe

- Reference failure: CD 270 / HALT가 과거 승인·교정 내역과 별개로 반복 제시됐고 현재 작업에서도 추가 승인 요구로 이어졌다. 기존 스크립트는 모든 이력을 합산하며 해결한 건을 차감하지 않는다. 초기에 사용자 요구를 명확히 한 두 질문도 각각 +10으로 기록되어 있어 합계가 전부 제품 버그 수를 뜻하지 않는다.
- Candidate kept for probe: `AGENTS.md`와 그 진입점 `CLAUDE.md`에 명시적인 계속 진행 지시를 작업 charter의 정확한 범위·RCA·재발 방지 검증에 연결하도록 명시한다. 원래 CD 결과를 유지하고 이미 승인된 범위에는 재승인을 반복 요구하지 않는다. 활성 lesson에는 광고 도입 시 실제 외부 요청·문구·초기 콘텐츠를 함께 검증하는 원칙을 추가한다.
- Candidate dropped: 누적 점수 초기화, 음수 이벤트로 상쇄, 임계치 상향 또는 기본 게이트 제거. 사용자의 기록 보존 지시와 일치하지 않으며 재발 방지의 근거가 아니다.
- Probe: 같은 `cd_status.py` 실행 결과가 여전히 원래 누적 점수와 HALT인지 확인한다. 같은 광고 심사 준비 검사로 수정 전 실패와 수정 후 통과를 비교한다. 승인된 이 작업에서 추가 중단 질문 없이 구현·검증을 끝내는지 기록한다. 제품 품질은 별도 브라우저/기본 체크포인트로 판정한다.
- Compose: 최종 검증 후 결과를 아래에 기록한다. 스킬·스크립트·훅·임계치는 변경하지 않는다.

### Implementation and checkpoint results

- Public release: 데모 광고와 배너 자리·가짜 완료 처리를 삭제하고 모든 펼치기를 무료로 제공한다. 기존 세션의 직전 사진은 유지하며 예전 광고 credit은 무시하고 다음 저장 때 제거한다.
- Content: 이용 방법, 원본 링크가 있는 사진 예시 3장, AI 제작·사람 수 검수·추첨 구성 설명을 정적 HTML에 제공한다. 원본 사진·검수 숫자·책 영상은 변경하지 않았다. 작은 예시 WebP 3개만 추가했다.
- Privacy: `web/privacy.html`과 상시 링크를 추가했다. 현재의 로컬 세션 저장·광고 없음·GitHub 호스팅·공개 GitHub 이슈 문의를 설명한다. 공개 저장소 API에서 `has_issues: true`를 확인했다. 광고 송출 코드는 계정 확인 메타 태그로 대체했다.
- Red/green: 새 광고 요청 검사는 수정 전 `public game does not load advertising SDKs before real ad integration`에서 exit 1로 실패했다. 동일 검사와 계정 메타 태그·가짜 광고 부재·정적 콘텐츠·개인정보 링크·실제 외부 요청 검사까지 수정 후 통과했다.
- Browser: 76 checks PASS. 실제 3초 알파 영상, 1.45초 사진 공개, 광량/후광, 부유·hover 입자, 무료 반복·중복 조작 방지, 구 세션·저장 차단·오류/지연 복구, 100장 원본/검수·320px 모바일·JavaScript 없는 콘텐츠/링크를 확인했다.
- Basic game client: 기존 기본 클라이언트로 3회 상태/스크린샷을 만들었다. 산출물 `.harness/tmp/adsense-client/`. 테스트 서버와 기본 클라이언트는 HTTP 200의 최신 코드에서 실행됐다. IAB의 로컬 탭은 연결 거부 오류를 반환하여 그 탭의 로컬 재생을 검증했다고 주장하지 않는다.
- Required checks: Charter PASS, Ruff PASS, pytest 28 passed / 1 skipped (기존 bash+uv 훅 실행 환경), JS 구문 PASS, diff 공백 PASS. Spec Kit not initialized / SKIPPED.
- CD probe: `uv run --frozen python .harness/scripts/cd_status.py`는 CD 280 / HALT를 그대로 출력했다. 원래 270에 무료 반복 이용 확인 clarify +10만 추가됐으며 이력을 초기화·차감하지 않았다. HALT는 PASS로 바꾸지 않고 이번 사용자 지시에 따른 명시적인 범위 예외로 기록한다.
- Harness compose: 작업별 승인과 RCA·검증을 연결하는 AGENTS/CLAUDE 규칙과 활성 lesson을 채택했다. 같은 작업에서 원래 HALT를 유지하며 추가 승인 질문 없이 구현·품질 검증을 진행했다. 스킬/스크립트/체크포인트/임계치 변경은 없다.
- Visual review: 데스크톱·320px 정적 콘텐츠/개인정보 스크린샷을 직접 확인했다. 예시 사진에 원본 링크와 인원수·장면 설명이 있고 콘텐츠 겹침·가로 넘침이 없다. 모바일에서 줄바꿈을 숨길 때 붙는 ‘숫자를만드는’ 표기는 HTML 공백으로 교정했다.
- Payload: 초기 자산 상한 510,228 bytes (예시 3장 모두 포함), 전체 배포 11,875,837 bytes. 검증용 버전 해시는 LF로 정규화해 Windows 체크아웃의 줄바꿈에 영향을 받지 않도록 검사한다.
- Final review: 수정할 것 없음. 승인된 무료 반복 요구·고딕/영상/100장 계약·정적 콘텐츠·개인정보·계정 확인을 대조했다. 스크립트/임계치/이력은 보존됐고 새 테스트는 실제 브라우저 동작과 공개 요청을 확인한다. 이번 제품 변경과 직접 필요한 테스트·검수 기록·게임 게이트·운영 교훈만 선택해 커밋하며 다른 이전 미커밋 작업은 남긴다.
- Public deploy: pending.
