# Q-RoPE E002 Variable-Cardinality Successor Candidate v1

## BLUF
- Candidate:
  - `synthetic_positional_variable_cardinality_offset_selection_response`
- This candidate is admissible for memo-level review only.
- It is intended to test bounded robustness to candidate-set growth and distractor insertion.

## Candidate Outline
- one query anchor
- bounded candidate-count range, for example `3` to `5`
- one correct positional choice under a relative-offset rule
- inserted distractors that preserve local ambiguity while changing set composition
- fixed upper cap to prevent fairness blow-up

## Admissibility Conditions
- candidate-count variability must be part of the task, not cosmetic
- symbolic control must use only bounded aggregate summaries over the set
- no per-cardinality lookup tables
- no hidden slot-identity shortcuts
- success or failure must change the decision outlook for the successor layer

## Immediate Rejection Conditions
- fixed-cardinality behavior disguised as variable-cardinality
- uncontrolled higher-order set interactions
- candidate-count growth beyond a small frozen cap
- symbolic control that needs cardinality-specific memorization

## Next Step
- write the explicit gate sketch for this candidate
- do not open implementation or execution yet
