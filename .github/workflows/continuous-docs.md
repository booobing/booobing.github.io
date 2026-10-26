---
on:
  schedule:
    - cron: "0 2 * * *"
permissions:
  contents: read
  pull-requests: write
---

# Continuous Documentation

Compare:
- `README.md`
- `AGENTS.md`
- `docs/charter.md` or the active task charter
- `.harness/checkpoints/default.yml`
- public commands, APIs, and user workflows that changed recently

Rules:
- no runtime code changes
- conservative edits only
- if behavior is unclear, open an issue or propose a charter update instead of guessing
- keep generated docs and screenshots out of the repository unless the charter explicitly says otherwise
