---
name: lean-code-design
description: Use when Codex is designing code, implementation plans, refactors, or bug fixes and should apply Ponytail-style minimal safe design inside this repository's charter, checkpoint, and review loop. Trigger before implementation when a request could invite over-engineering, new abstractions, new dependencies, duplicated helpers, broad rewrites, or speculative future-proofing.
---

# Lean Code Design

## Goal

Design the smallest safe change after understanding the touched flow. Use the
Ponytail ladder as a design filter, while keeping this repository's charter,
checkpoint, review, and lesson rules as the stronger contract.

## Workflow

1. Read the charter, task, relevant code, and tests before choosing a design.
2. State the smallest touched-file set and explicit non-goals.
3. Climb the ladder and stop at the first rung that satisfies the request:
   - Skip work that does not need to exist.
   - Reuse an existing helper, type, pattern, or module.
   - Use the standard library.
   - Use a native platform feature.
   - Use an already-installed dependency.
   - Use a one-line or local change.
   - Write the minimum new code that works.
4. For bug fixes, grep callers and fix the shared root cause rather than only
   the reported symptom.
5. Add the smallest meaningful check for non-trivial logic, then run the
   checkpoint gate.

## Design Rules

- Prefer deletion, reuse, and boring local edits over new structure.
- Do not add abstractions, configuration, dependencies, files, or scaffolding
  for hypothetical future needs.
- Keep implementation plans short: chosen rung, files touched, check to run,
  and what was intentionally skipped.
- Mark deliberate simplifications with a `ponytail:` comment only when the
  shortcut has a known ceiling and future upgrade path.

## Never Simplify Away

- Charter scope, non-goals, and checkpoint discipline.
- Input validation at trust boundaries.
- Error handling that prevents data loss.
- Security, privacy, accessibility, and rollback safety.
- Calibration or environment realities that the code must expose.
- Anything the user explicitly insists on after the tradeoff is named.

## Output Shape

When planning, produce a compact design note:

- selected rung
- files to touch
- skipped complexity
- validation command

When implementing, keep the final response focused on what changed, what was
skipped, and which checks ran.
