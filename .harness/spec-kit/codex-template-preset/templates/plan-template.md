# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Summary

[Primary requirement and selected technical approach.]

## Technical Context

**Language/Version**: [e.g., Python 3.12 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., none, FastAPI, React or NEEDS CLARIFICATION]
**Storage**: [if applicable, otherwise N/A]
**Testing**: [e.g., pytest, npm test, cargo test or NEEDS CLARIFICATION]
**Target Platform**: [runtime or deployment target]
**Project Type**: [library/cli/web-service/desktop-tool/etc.]
**Performance Goals**: [domain-specific or N/A]
**Constraints**: [security, compatibility, offline, memory, latency, or N/A]

## Constitution Check

Spec Kit constitution is advisory unless it mirrors `AGENTS.md`.
If `.specify/memory/constitution.md` conflicts with `AGENTS.md`, follow `AGENTS.md`.

| Gate | Status | Notes |
|------|--------|-------|
| Charter exists | [PASS/FAIL] | [link or note] |
| Non-goals honored | [PASS/FAIL] | [scope note] |
| Touched files bounded | [PASS/FAIL] | [expected files] |
| Checkpoints identified | [PASS/FAIL] | [required commands] |
| Rollback path clear | [PASS/FAIL] | [rollback note] |

## Project Structure

### Documentation

```text
specs/[###-feature]/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code

```text
[Replace with the real project layout for this feature.]
```

**Structure Decision**: [Document the selected structure and why it matches the charter.]

## Implementation Notes

- **Touched files**: [Concrete paths or directories]
- **Dependencies to add**: [Package names or none]
- **Migration/data impact**: [Impact or none]
- **Security considerations**: [Concrete checks or none]
- **Compatibility considerations**: [Concrete checks or none]

## Required Checkpoints

Use `.harness/checkpoints/default.yml` as the completion gate.

```text
[List exact commands or named gates required for this feature.]
```

## Rollback Plan

[How to revert, disable, or isolate the change if a checkpoint or review fails.]

## Complexity Tracking

Fill only when the plan exceeds the charter or introduces meaningful complexity.

| Complexity | Why Needed | Simpler Alternative Rejected Because |
|------------|------------|--------------------------------------|
| [item] | [reason] | [reason] |
