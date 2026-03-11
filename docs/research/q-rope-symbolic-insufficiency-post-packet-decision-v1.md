# Q-RoPE Symbolic Insufficiency Post-Packet Decision v1

Date: 2026-03-10
Stories: S669

## Decision
- keep the symbolic-insufficiency branch active
- do not widen the task or symbolic family yet
- next bounded step: token-renaming hardening

## Reason
- the witness cleared the frozen-basis symbolic control on the fixed first packet
- the branch now has a positive result under the declared symbolic-insufficiency contract
- the next useful question is robustness to a fixed label-preserving token renaming, not task expansion

## Next Step
- rerun the same bounded witness/control packet under a fixed token permutation
- keep the symbolic basis frozen
- stop the branch if the witness loses either declared packet metric under that nuisance perturbation
