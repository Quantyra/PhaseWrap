# Q-RoPE Sector-Parity Restart Brief Draft v1

## Status
- `draft only`
- `not approved`
- `memo-level only`

## Candidate
- `V_future_sector_relational`

## Motivation
The pair-state branch showed that explicit relational sector structure can create strong synthetic separation, but the sign-labeled task was too vulnerable to direct label alignment.

The next restart must preserve:
- explicit relational structure
- sector-first diagnostics

And remove:
- direct sign-to-label equivalence

## Target task
- `synthetic_sector_parity_binary`

### Label rule
- label `1`: `P_small`, `N_large`
- label `0`: `N_small`, `P_large`

This forces any future mechanism to do more than recover offset sign.

## Required mechanism declaration
Any future implementation brief based on this draft must specify:
- exact representation family
- exact sector-resolution rule
- exact aggregation rule
- exact anti-collapse diagnostic

No open-ended mechanism families are allowed at approval time.

## Required packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- baseline: `V0`
- candidate: one future branch only

## Required success criteria
The future candidate must satisfy all of:
- better mean accuracy than `V0`
- better mean F1 than `V0`
- positive task-relevant sector separation across all three seeds
- no pooled-score-only explanation
- explicit sector resolution before aggregation

## Required failure criteria
Stop immediately if any of the following occur:
- only one-seed improvement
- pooled score drift explains the gain
- sector resolution is bypassed or aggregated too early
- the task can be solved by recovering a simpler shortcut than the declared relational rule

## Budget and scope guardrails
- local-only
- synthetic-only
- zero-credit
- no benchmark expansion
- no remote execution
- no parallel variant branching

## Decision posture
This draft is preserved so the next restart, if pursued, begins at a higher bar than the archived pair-state implementation branch.

## Bottom line
The archive now contains a concrete future restart brief for an alignment-safe synthetic family.
It is specific enough to review later, but not approved for execution now.
