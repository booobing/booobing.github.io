# [PROJECT_NAME] Constitution

This constitution is a Spec Kit mirror for stable project principles.
`AGENTS.md` remains the operational source of truth for agent behavior, checkpoint discipline, scope control, and history safety.

## Core Principles

### I. Charter Before Implementation

Every task MUST start from either `docs/charter.md` or an explicit task charter.
The charter MUST state objective, non-goals, touched files, ambiguity level, difficulty, required checkpoints, and rollback plan.

### II. Bounded, Conservative Changes

Implementation MUST stay inside the user request and the charter.
Agents SHOULD prefer the smallest diff that satisfies the feature specification and required checkpoints.

### III. Specification As Planning Input

Spec Kit artifacts (`spec.md`, `plan.md`, `tasks.md`) are feature-level planning artifacts.
They do not replace `AGENTS.md`, `LESSONS.active.md`, or `.harness/checkpoints/default.yml`.

### IV. Checkpoint Completion

Completion MUST be gated by the repository checkpoint file.
If a checkpoint cannot run, the final report MUST state exactly why and what risk remains.

### V. Lessons And RCA

Corrections, repeated failures, scope drift, rollbacks, and high Clarification Debt MUST be converted into a lesson or RCA candidate.

## Development Workflow

Use this order when Spec Kit is enabled:

```text
charter -> specify/clarify -> plan -> tasks -> implementation -> checkpoint -> review -> lesson/RCA
```

## Governance

Amendments to this file SHOULD mirror durable changes already accepted in `AGENTS.md` or `LESSONS.active.md`.
If this file conflicts with `AGENTS.md`, `AGENTS.md` wins.
Community extensions or presets MUST NOT be installed unless explicitly approved for the project.

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
