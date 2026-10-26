# Root Cause Analysis

1. Symptom: Generated `agents/openai.yaml` contained `Use -code-design...` instead of `Use $lean-code-design...`.
2. Root cause: PowerShell expanded `$lean` inside a double-quoted command argument before `init_skill.py` received the metadata.
3. First missed signal: The generator command included a literal skill invocation token with `$` but did not use single quotes or escaping.
4. Prevention rule: Use single quotes or escape `$` when passing literal skill names through PowerShell arguments.
5. Whether AGENTS, skill description, or checkpoint should change: Update active lessons only; AGENTS and checkpoints already require correction logging and CD review.
6. One-line lesson for LESSONS.active.md: PowerShell 명령 인자에 `$skill-name` 같은 리터럴을 넣을 때는 변수 확장을 피하도록 작은따옴표 또는 이스케이프를 쓴다.
