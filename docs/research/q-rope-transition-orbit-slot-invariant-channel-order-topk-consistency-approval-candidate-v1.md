# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Consistency Approval Candidate v1

Date: 2026-03-10
Stories: S502

## Status
- approval-candidate

## Rationale
- the stopped slot-invariant rank-only branch preserved the strongest order-F1 signal but failed the declared top-level accuracy gate
- the next legitimate continuation is top-k consistency under the same slot-invariance contract
- this is materially different from the failed rank-only branch because consistency of the top subset is primary and full-list ordering is not

## Approval Conditions
- keep the fixed control stack bounded
- do not widen the task family
- do not reopen implementation until the dedicated approval gate is written
