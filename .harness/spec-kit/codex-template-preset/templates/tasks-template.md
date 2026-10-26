---
description: "Codex project template task list for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: `spec.md` and `plan.md`
**Gate**: `.harness/checkpoints/default.yml`

Tasks are grouped so each user story can be implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency
- **[Story]**: User story label such as US1 or US2
- Include exact file paths in every implementation or test task

## Phase 1: Setup

**Purpose**: Prepare only the structure and tooling required by the charter.

- [ ] T001 Confirm charter objective, non-goals, touched files, checkpoints, and rollback plan
- [ ] T002 Create or adjust only the directories needed for this feature
- [ ] T003 [P] Update project-specific checkpoint commands if the feature introduces a new stack

## Phase 2: Foundational

**Purpose**: Shared behavior required before user-story work begins.

- [ ] T004 Implement shared contracts, configuration, or helpers required by all user stories
- [ ] T005 [P] Add contract or invariant tests for shared behavior if requested or risk-reducing

**Checkpoint**: Foundation is ready for independently testable user-story work.

## Phase 3: User Story 1 - [Title] (Priority: P1)

**Goal**: [What this story delivers]
**Independent Test**: [How to verify this story on its own]

### Tests For User Story 1

- [ ] T006 [P] [US1] Add acceptance or integration test in [path]
- [ ] T007 [P] [US1] Add boundary or failure-mode test in [path]

### Implementation For User Story 1

- [ ] T008 [US1] Implement required behavior in [path]
- [ ] T009 [US1] Update user-facing docs or examples if behavior changes in [path]

**Checkpoint**: User Story 1 works independently and does not expand beyond the charter.

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [What this story delivers]
**Independent Test**: [How to verify this story on its own]

### Tests For User Story 2

- [ ] T010 [P] [US2] Add acceptance or integration test in [path]

### Implementation For User Story 2

- [ ] T011 [US2] Implement required behavior in [path]

**Checkpoint**: User Stories 1 and 2 both remain independently testable.

## Phase N: Harness Checkpoint, Review, And Lesson

**Purpose**: Keep completion under the repository's existing operating model.

- [ ] T900 Run required gates from `.harness/checkpoints/default.yml`
- [ ] T901 Run `uv run --frozen python .harness/scripts/speckit_status.py` when `.specify/` exists
- [ ] T902 Review for charter mismatch, scope drift, missing tests, and rollback risk
- [ ] T903 Update `LESSONS.active.md`, `.harness/memory/lessons-learned.md`, or RCA only if the run produced a correction, redo, rollback, repeated failure, or high Clarification Debt

## Dependencies

- Setup must finish before foundational work.
- Foundational work must finish before user-story implementation.
- User stories should stay independently testable unless the plan explicitly justifies a dependency.
- Harness checkpoint and review must finish before claiming completion.

## Notes

- Avoid vague tasks that do not name paths.
- Avoid tasks that silently expand touched files beyond the charter.
- Do not install community Spec Kit extensions or presets unless explicitly approved.
