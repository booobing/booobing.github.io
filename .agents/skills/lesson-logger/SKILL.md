---
name: lesson-logger
description: Trigger when a run had a correction, redo, out-of-bounds edit, started without charter, or repeated error. Converts incidents into reusable lessons.
---

# Steps
1. classify event: clarify / correct / redo / started_without_charter / out_of_bounds_edit
2. append JSONL event via script if available
3. update or propose a lesson only when evidence supports it: a reproduced failure, a before/after contrast, or a checkpoint result. Otherwise log the event only.
4. tag the lesson scope (invariant / domain) and the harness component it changes
5. if the lesson proposes a harness change, route it to `harness-improve`
6. if CD >= 50, require RCA

# Output
- event type
- score impact
- lesson wording, scope, component, evidence (or "no lesson: insufficient evidence")
- whether RCA is required
