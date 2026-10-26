---
name: root-cause-analysis
description: Trigger when Clarification Debt is high, a rollback occurred, or the same mistake class repeated. Do not use for ordinary code review.
---

# Produce exactly
1. Symptom
2. Root cause
3. First missed signal
4. Prevention rule, scoped as invariant (any task) or domain (this stack/area)
5. Which component should change: hook, script, checkpoint, skill, subagent, memory, or AGENTS rule
6. One-line lesson for LESSONS.active.md

# Rule
- blame process, not the user
- prefer prevention rules over longer prompts
- choose the most enforcing component that works: hook > script > checkpoint > skill > prose rule
- always write the RCA and the failure lesson (symptom, root cause, reproduced-failure evidence); only adopting the prevention rule as a harness change goes through `harness-improve` first
