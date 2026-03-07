# Q-RoPE Local Screening Branch Reassessment v1

## Decision
Decision: `PAUSE` further local simulator redesign iteration on the current screening branch.

Meaning:
- keep the existing local screening infrastructure
- do not open another immediate local tail candidate
- do not spend remote budget based on the current local redesign line

## Why this is the correct decision
The local screening branch has now produced two consecutive negative mechanism outcomes:

1. fixed post-`RZ` mixing presets
   - no robust promotion candidate

2. broader interference-tail redesign (`mix_it1`)
   - clear `NO-GO`

At the same time, the original branch questions have already been answered:
- parity is a better local screening readout than weighted for default use
- downstream conversion plus readout is the bottleneck
- small local redesigns can move the signal
- but they have not produced a robust branch-worthy improvement

That means the branch is no longer failing because of lack of exploration.
It is failing because the explored local simulator interventions are not producing reliable gains.

## Why this is a pause, not a permanent stop
The branch is still useful as infrastructure:
- deterministic local statevector path
- parity-default screening path
- focused tests
- clear screening gates

What is paused is:
- more immediate mechanism redesign attempts inside this same local loop

What remains valid:
- use the local simulator as a sanity-check path
- use current local evidence in publication framing

## What should not happen next
Do not:
- open another tail preset branch immediately
- reopen `V4`
- reopen threshold tuning
- spend remote credits trying to rescue the local redesign line

## Recommended next program move
The next best move is outside this local redesign loop:

- synthesize the current evidence into a program-level status and decision memo

Reason:
- the repo now contains enough evidence to state clearly what is viable, what is exploratory, and what has failed
- that decision is more valuable right now than one more local tweak

## Program posture after this decision
Primary defensible elements:
- `V3` remains the primary reference path
- remote execution feasibility is established
- remote results are unstable and require constrained claims
- local redesign attempts beyond the parity upgrade have not yielded robust gains

Exploratory elements:
- `V4`
- broader local redesign candidates

Closed local redesign items:
- fixed post-`RZ` preset branch
- `mix_it1` interference-tail candidate

## Bottom line
The local screening branch has reached diminishing returns for now.
Pause it.
Use the accumulated evidence to update the project-level decision posture before opening any new technical branch.
