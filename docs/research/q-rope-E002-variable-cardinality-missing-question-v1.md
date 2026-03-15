# Q-RoPE E002 Variable-Cardinality Missing Question v1

## BLUF
- Next missing question:
  - can the witness survive bounded positional selection when candidate-set size and distractor composition vary, rather than only in fixed-size candidate sets?
- This is the next best question because it tests robustness beyond both preserved successor-class survivors.
- Execution remains closed.

## Why This Question Is Missing
Current preserved successor-class evidence covers:
- `key-query-offset-selection`
- `dual-anchor-offset-consensus`

Both preserve bounded model-like positional selection, but both use fixed candidate-set size.

The current package does not yet answer whether the witness survives when:
- the choice set grows within a bounded cap,
- distractors are inserted,
- and the correct choice must remain stable despite set-composition change.

## Decision Leverage
If this question succeeds:
- the successor layer becomes meaningfully stronger and less tied to fixed-cardinality framing.

If this question fails:
- the current successor package becomes a more defensible practical ceiling for bounded model-like positional selection.

## Candidate Direction
- `synthetic_positional_variable_cardinality_offset_selection_response`

## Why Not Another Existing Family
- not another transfer family
- not another abstract bridge
- not another realism-bridge retrieval variant
- not another fixed-cardinality successor clone

## Next Step
- write one candidate sketch and gate sketch only
- keep implementation and execution closed
