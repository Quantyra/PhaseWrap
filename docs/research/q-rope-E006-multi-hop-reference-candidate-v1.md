# Q-RoPE E006 Multi-Hop Reference Candidate v1

Date: 2026-03-15
Stories: S1447-S1449

## BLUF
- Proposed candidate:
  - `synthetic_positional_intermediate_pointer_selection_response`
- The task uses one bounded candidate memory and one query prompt.
- Correctness depends on identifying an intermediate candidate first, then resolving the final target relative to that intermediate under a second bounded rule.

## Candidate Sketch
- one bounded query prompt
- one bounded candidate set
- query specifies a first-hop rule that identifies exactly one intermediate candidate
- the final target is not defined directly from the query
- the final target is defined by a second bounded positional/content rule relative to the intermediate candidate
- distractors remain active at both the intermediate and final stages
- at least one direct-looking distractor should remain active so the task cannot collapse into direct one-shot selection

## Why It Is Materially Different
- It is not another direct one-shot selection task.
- It is not repeated multi-query reuse over shared memory.
- It introduces bounded reference depth: query -> intermediate -> target.
- It tests whether the witness signal survives compositional relational indirection rather than only direct retrieval.

## Bounded Fairness Direction
- small fixed candidate-count cap
- one frozen symbolic family across all allowed candidate counts
- declared first-hop summaries and second-hop summaries only
- no latent pointer tables
- no token-id or slot-id shortcuts
- no direct-target summaries that bypass the intermediate hop
