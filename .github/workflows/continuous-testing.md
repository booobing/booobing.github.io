---
on:
  schedule:
    - cron: "0 4 * * *"
permissions:
  contents: read
  pull-requests: write
---

# Continuous Testing

Target the real repository surface:
- current source directories
- current test directories
- `docs/charter.md` or the active task charter
- `.harness/checkpoints/default.yml`

Strengthen or propose:
- acceptance tests for user-visible behavior
- contract and boundary checks for public interfaces
- smoke checks that keep temp outputs under `.harness/tmp/`
- regression tests for recently changed workflows

Rules:
- prefer doc/test PRs over broad production refactors
- flag self-fulfilling tests and missing invariants
- if behavior is unclear, propose a charter update instead of guessing
- reference checkpoint names directly in the PR body when suggesting changes
