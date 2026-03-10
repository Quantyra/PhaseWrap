# Q-RoPE Transition Orbit Sign-Only Approval-Candidate v1

Date: 2026-03-11
Stories: S412

## Decision
- place the sign-only line at approval-candidate posture
- keep implementation closed in this step

## Why
- the line is materially different from the stopped signed-margin branch
- it targets the exact unresolved survival signal from that branch:
  - directional sign prediction, not signed magnitude calibration
- the control family is explicit and bounded

## Remaining Blocker
- the generator has not yet proven that coarse sign lookup is near-null tightly enough that a bounded symbolic sign baseline cannot win trivially

## Next Legitimate Move
- write the dedicated implementation-approval gate only if the sign-only generator contract remains unchanged
