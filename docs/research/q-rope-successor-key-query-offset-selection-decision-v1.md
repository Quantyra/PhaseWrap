# Q-RoPE Successor Key-Query Offset Selection Decision v1

Date: 2026-03-14
Stories: S1263-S1265

## BLUF
- The candidate is acceptable for one more memo-level step.
- The next valid move is to write the candidate-level gate, not an implementation plan.
- If the candidate-level gate cannot keep the symbolic control bounded and the task genuinely one-of-many, the class should stop there.

## Decision
- `CONTINUE TO CANDIDATE-LEVEL GATE ONLY`

## Why
- The candidate appears more model-like than `offset-retrieval`.
- It still has a plausible bounded fairness contract.
- The remaining uncertainty is now concentrated enough to justify one stricter gate.
