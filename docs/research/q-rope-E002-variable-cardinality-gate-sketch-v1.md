# Q-RoPE E002 Variable-Cardinality Gate Sketch v1

## BLUF
- The variable-cardinality successor candidate should open only if fairness remains bounded under set-size variability.
- The main threat is control-family blow-up.
- If that threat cannot be contained at memo level, `E002` should stop before implementation.

## Gate Questions
- Is the task genuinely variable-cardinality rather than fixed-cardinality with padding?
- Is the candidate-count cap explicit and small?
- Can the symbolic control remain bounded to aggregate set summaries only?
- Is there a clean stop rule if the design collapses into slot-identity or cardinality lookup?
- Would success or failure change the program decision?

## Pass Condition
- all five questions can be answered yes with a clear bounded contract

## Fail Condition
- any required fairness bound is vague, missing, or cardinality-specific
