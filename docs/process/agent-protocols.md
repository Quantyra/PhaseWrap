# Agent protocols

## Purpose
Standardize how worker agents are launched and how they report results for QRoPE research.

## Critical path and parallelization
- Each epic must identify its critical path in the epic file.
- All stories not on the critical path and not blocked should be executed in parallel by default.

## Reporting
- Workers should update the story file with a completion note and list files changed.
- Workers should create or update docs when required by story outputs.
- Orchestrator must update `logs/checkpoint.json` before each major action and after each story status change.

## Cycle-time logging
- Record cycle start timestamp when work begins.
- Record cycle end timestamp when completion notes are written.
- Include Start, End, and Total in story notes.

## Research quality gates
- Epics must include an evidence log section.
- Stories must cite sources or datasets used.
- Findings should be reproducible or explicitly note limitations.
- A novelty review gate must occur before publication drafting or formal claim hardening.
- Publication work must stop if the current result is null-to-inconclusive without a credible positive thesis; in that state, convert the repo to internal archive/positioning mode until a materially different positive hypothesis appears.

## Planning loop protocol
Use a plan-and-refine loop for non-trivial stories:
- `L0`: execute directly.
- `L1`: 1 draft + up to 1 revision.
- `L2`: 1 draft + up to 2 revisions.
- `L3`: 1 draft + up to 3 revisions.

Validator feedback for `L2/L3` must include correctness gaps, missing dependencies, risk gaps, and concrete fixes.

## Git protocol
- The repository must remain under git version control.
- Each completed story or materially distinct protocol step should end with a non-interactive git commit.
- Commit messages should reference the story ID when one exists, for example: `S040 define V4b redesign`.
- Never commit secrets, tokens, or local `.env` files.
- If a step changes only transient logs or caches without a meaningful protocol artifact, do not force a commit just to create noise.
