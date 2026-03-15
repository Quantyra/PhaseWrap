# Q-RoPE E002 Variable-Cardinality Implementation v1

Date: 2026-03-14
Stories: S1334-S1337

## BLUF
- Implemented `synthetic_positional_variable_cardinality_offset_selection_response` inside the frozen `E002` scope.
- The task stays genuinely variable-cardinality across active candidate counts `3`, `4`, and `5`.
- The witness and control both use one frozen family across counts; the implementation did not require count-specific symbolic families.

## Implemented Task
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`

## Construction
- one query anchor
- active candidate counts `3`, `4`, `5`
- exactly one correct candidate under the declared relative-offset rule
- distractor insertion changes set composition while keeping the count cap fixed

## Fairness Notes
- one frozen symbolic family spans all allowed candidate counts
- only aggregate set summaries plus per-candidate declared summaries are used
- no per-count lookup tables, no slot-identity shortcuts, no basis drift by count

## Outcome
- The bounded implementation held.
- `E002` remains admissible for one fixed three-seed packet only.
