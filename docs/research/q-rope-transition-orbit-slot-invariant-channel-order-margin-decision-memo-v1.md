# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Margin Decision Memo v1

Date: 2026-03-10
Stories: S489

## Decision
- stop the slot-invariant channel-order margin execution branch

## Reason
- under the approved gate, both `mae` and `rank_correlation` are primary metrics
- the witness led on `mae`
- multiple bounded controls led on `rank_correlation`
- mixed leadership is not enough to keep the branch active under protocol

## Consequence
- return the line to memo-only posture
- preserve the next angle only if it changes the objective family rather than retrying the same margin target
