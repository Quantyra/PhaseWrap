# Q-RoPE Relational Witness Implementation Approval Gate v1

## Decision
- `APPROVE`
- scope: `strictly bounded`

## Approved scope
One bounded implementation phase is approved for:
- task: `synthetic_sector_parity_binary`
- baseline: `V0`
- candidate: `V_future_relational_witness`
- backend: `sim_quantum_statevector`

## Hard limits
- local-only
- synthetic-only
- zero-credit
- no remote execution
- no benchmark expansion
- no second candidate branch
- no hyperparameter sweep

## Why approval is justified
This path now has:
- exact task
- exact feature schema
- exact head constraint
- exact packet
- exact diagnostics
- exact stop conditions

That is enough for one bounded falsification cycle.

## Why the approval remains narrow
This approach is materially new, but still unproven.

The repo has already shown that broad reopening before the first clean packet leads to wasted motion.

So the correct move is:
- one tightly bounded implementation
- then one tightly bounded packet

## Next step
Translate this approval into one strict implementation plan before any code is written.
