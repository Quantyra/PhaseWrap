# Continuous target decision memo

## Decision
- `STOP` the implemented `synthetic_dual_continuous_coupled_response` branch.
- Return the branch to memo-only posture.

## Basis
- The approved fixed packet failed cleanly.
- `V_future_relational_witness_continuous` underperformed all approved symbolic controls.
- The strongest bounded symbolic control (`V_control_symbolic_boolean_state_lookup`) dominated the task.

## Why this is decisive
- The branch was granted one bounded implementation phase only.
- The task was meant to test whether the witness path survived stronger symbolic regression baselines.
- It did not.

## What is disallowed next
- no tuning on this task
- no broader continuous packet
- no remote execution
- no publication use

## What remains valid
- preserve the broader continuous angle at memo level only
- any future restart must use a harder state-sensitive continuous task that cannot be solved by a bounded lookup over three agreement bits
