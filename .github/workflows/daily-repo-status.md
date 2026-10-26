---
on:
  schedule:
    - cron: "0 0 * * *"
permissions:
  contents: read
  issues: write
---

# Daily Repo Status

Produce a daily issue with:
- latest CI health
- whether setup, lint, tests, and Clarification Debt checks are green
- top 3 repository risks grounded in current files
- whether docs or tests drift from the active charter
- whether generated artifacts or caches appear tracked

Rules:
- do not guess missing context
- link to evidence
- if risk is architectural, recommend a charter or RCA before code changes
