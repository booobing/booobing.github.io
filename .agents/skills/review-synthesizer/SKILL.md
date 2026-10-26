---
name: review-synthesizer
description: Trigger when multiple review agents or workflows have produced findings that need a single decision and priority order.
---

# Output format
- first line: finding count, or "수정할 것 없음" when nothing needs fixing
- BLOCKERS
- HIGH
- MEDIUM
- LOW
- next action in priority order

# Rules
- deduplicate overlapping findings
- cite the strongest evidence as `file:line`
- prefer behavior/regression/security over style
- tag each finding Important / Nit / Pre-existing per `REVIEW.md`; keep at most 3 Nits
- group findings by bug class, not by single line
- after 3 review-fix rounds on the same change, stop and recommend rethinking the approach
- from round 2, review only changes since the previous round and do not repeat earlier findings
