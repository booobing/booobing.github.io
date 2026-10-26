---
name: research-pipeline
description: Use when the agent should automate an optional research or experiment workflow through manifest-backed stages, status, resume, and artifact contracts.
---

# Goal
Drive research, paper, benchmark, or repeated experiment work through `.harness/scripts/research_pipeline.py` instead of ad hoc notes.
For ordinary development tasks, keep using the repository's normal charter/checkpoint loop unless the work needs staged evidence tracking.

# Workflow
1. Create or reuse a workspace with `python .harness/scripts/research_pipeline.py run --topic "<topic>"`.
2. Before doing stage work, run `start --workspace <workspace>`.
3. Produce the required real artifact for the current stage inside the workspace.
4. Mark the stage with `complete --workspace <workspace>` only after required artifacts exist.
5. Use `status`, `resume`, and `inspect` to report progress or recover after interruption.

# Stage Order
`ideation -> planning -> setup -> coding -> execution -> analysis -> figure_gen -> writing -> review`

# Evidence Rule
Do not invent experiment results, metrics, tables, or figures. If a required artifact is missing, keep the stage pending or failed and write the limitation in the next planning/review artifact.

# Boundaries
- This is an optional template mode, not the default flow for every development project.
- LaTeX compilation can use the Codex LaTeX plugin; this skill only manages pipeline state.
- GPU, SLURM, model routing, and external services are outside this MVP unless a later charter adds them.
