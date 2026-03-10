# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Rank-Only Approval Candidate v1

Date: 2026-03-10
Status: approval-candidate
Story: S520

## Decision
- elevate the line to approval-candidate posture
- keep it memo-only in this step

## Why This Line Exists
- the stopped slot-invariant top-k margin branch preserved the strongest `mae` signal but failed the declared rank gate
- this line makes top-k rank structure primary instead of top-k margin magnitude
- this is materially different from the stopped branch, not a relabel of the same objective

## Why It Is Not Yet Implementation-Approved
- the task still needs a dedicated implementation-approval gate
- the hard-stop diagnostics must be bound directly into that gate before code reopens
