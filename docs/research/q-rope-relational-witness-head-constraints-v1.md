# Q-RoPE Relational Witness Head Constraints v1

## Decision
- preserve one tiny-head constraint set

## Allowed head family
Only one of these is allowed in a future bounded restart:
- logistic regression over the fixed feature schema
- or a single linear layer plus sigmoid with no hidden layer

These are equivalent for protocol purposes.

## Explicitly forbidden head variants
- hidden layers
- nonlinear MLP stacks
- tree models
- token-level feature fusion
- attention over sector features
- ensembling

## Training constraints
- one fixed train/validation/test split policy
- one fixed regularization setting declared in advance
- no hyperparameter sweep
- no seed sweep beyond the approved packet seeds

## Anti-slack rule
If the head needs substantial tuning to work, the approach fails its intended test.

The whole point is to determine whether:
- sector-first quantum responses already contain enough structured signal
- for a tiny constrained head to read out usefully

## Required audit outputs
Any future restart must emit:
- learned coefficients
- intercept
- feature ordering
- feature scaling rule, if any

That keeps the witness readable and falsifiable.

## Bottom line
The witness head is only valid as a research angle if it stays tiny, explicit, and auditable.
