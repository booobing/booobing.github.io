---
name: clarification-gate
description: Trigger when the request is ambiguous, conflicting, under-specified, or likely to cause scope drift. Especially useful before implementation.
---

# Decision rule
- LOW: proceed with explicit assumptions.
- MEDIUM: present 2-3 bounded options, choose the safest default.
- HIGH: halt implementation and ask for or prepare clarification.

# Output
- ambiguity level
- why
- what can safely proceed now
- what must not proceed
- minimum clarification needed

# Do not
- ask broad open-ended questions
- proceed on hidden assumptions
