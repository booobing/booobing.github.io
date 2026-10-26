## Summary
<!-- 무엇을, 왜 바꿨는지. 관련 charter: docs/charter.md -->

## Testing
<!-- 실행한 명령과 결과를 그대로 적는다. 실행하지 못한 체크포인트는 이유와 남은 위험을 적는다. -->
- [ ] `uv run --frozen ruff check .`
- [ ] `uv run --frozen python -m pytest -q`
- [ ] `uv run --frozen python .harness/scripts/speckit_status.py`
- [ ] `uv run --frozen python .harness/scripts/cd_status.py`

## Risk
<!-- 낮음 / 중간 / 높음 과 그 이유. 무엇이 잘못될 수 있고, 어떤 검사가 그걸 잡는가? -->

## How to revert
<!-- 되돌리는 방법. 예: 이 PR revert, 설정 플래그 끄기, 마이그레이션 롤백 순서 -->

<!-- Claude가 작성했더라도 변경을 요청한 사람이 위 내용을 확인한다. 리뷰 규칙은 REVIEW.md를 따른다. -->
