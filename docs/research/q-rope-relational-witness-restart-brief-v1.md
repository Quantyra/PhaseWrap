# Q-RoPE Relational Witness Restart Brief v1

## Status
- `memo-only`
- `not approved`

## Candidate
- `V_future_relational_witness`

## Task
- `synthetic_sector_parity_binary`

## Mechanism split
### Quantum side
- generate sector-first relational responses
- expose only the fixed schema:
  - sector means
  - sign contrasts
  - magnitude contrasts
  - task contrast

### Classical side
- one tiny witness head only
- logistic-regression-equivalent
- no hidden layer
- no token or position shortcut inputs

## Fixed packet
- baseline: `V0`
- candidate: `V_future_relational_witness`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- synthetic-only
- zero-credit

## Required diagnostics
- full feature ordering
- learned coefficients
- intercept
- per-sector response summary
- task contrast summary
- anti-collapse proof

## Success criteria
The candidate must satisfy all of:
- better mean accuracy than `V0`
- better mean F1 than `V0`
- positive task-relevant separation across all three seeds
- no pooled-score-only explanation
- no shortcut inputs outside the fixed schema

## Failure criteria
Stop immediately if:
- gains appear in only one seed
- witness utility disappears once shortcuts are removed
- coefficient pattern implies dependence on a hidden proxy outside the declared schema
- sector-first diagnostics are bypassed

## Guardrails
- no hyperparameter sweeps
- no second candidate branch
- no remote execution
- no benchmark expansion

## Bottom line
This brief defines the smallest valid restart for the relational witness angle.
It is specific enough for approval review, but it does not authorize implementation.
