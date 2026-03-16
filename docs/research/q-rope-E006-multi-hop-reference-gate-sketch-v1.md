# Q-RoPE E006 Multi-Hop Reference Gate Sketch v1

Date: 2026-03-15
Stories: S1447-S1449

## BLUF
- `E006` is admissible only if it stays genuinely multi-hop.
- The candidate fails immediately if the final target can be derived directly from the query without the intermediate candidate.
- Execution remains closed until a stricter gate is written.

## Required Gate Conditions
- exactly one intermediate candidate per example under the first-hop rule
- exactly one final target per example under the second-hop rule
- the final target must not be directly derivable from the query-conditioned rule alone
- one frozen symbolic family across all allowed candidate counts
- bounded first-hop and second-hop declared summaries only
- active distractors at both hop levels
- no token-id or slot-id shortcuts

## Immediate Reject Conditions
- task collapses into direct one-shot selection
- intermediate hop is ornamental rather than decision-critical
- symbolic control requires latent pointer tables or per-pattern lookup families
- candidate count or hop depth expands beyond a small bounded cap
