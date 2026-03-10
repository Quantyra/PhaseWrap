# Q-RoPE Transition Orbit Channel-Advantage Decision Memo v1

Date: 2026-03-10
Stories: S453

## Decision
- stop the transition-orbit channel-advantage execution branch

## Why
- the generator hard-stop diagnostics passed on all fixed packet runs
- the witness lost decisively on the primary metric to every approved bounded control
- the failure mode was stronger than a simple near-tie: the witness became numerically unstable on multiple seeds while the controls stayed finite and well behaved
- mean rank correlation stayed weak and did not justify reopening the branch after a catastrophic MAE failure

## Consequence
- return the line to memo-only posture
- do not widen the task or control family on this branch
- preserve one next angle that tests relative channel ordering rather than raw signed channel-effect magnitude
