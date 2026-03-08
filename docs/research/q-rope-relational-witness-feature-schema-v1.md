# Q-RoPE Relational Witness Feature Schema v1

## Decision
- preserve one fixed feature schema for any future witness-head restart

## Allowed feature groups
The witness head may only consume sector-first quantum outputs and their direct derived contrasts.

### Group A: sector means
- `mu_P_small`
- `mu_P_large`
- `mu_N_small`
- `mu_N_large`

### Group B: sign contrasts
- `delta_sign_small = mu_P_small - mu_N_small`
- `delta_sign_large = mu_P_large - mu_N_large`

### Group C: magnitude contrasts
- `delta_mag_pos = mu_P_small - mu_P_large`
- `delta_mag_neg = mu_N_small - mu_N_large`

### Group D: crossed task contrasts
- `delta_task = (mu_P_small + mu_N_large) / 2 - (mu_N_small + mu_P_large) / 2`

## Explicitly forbidden inputs
The witness head may not consume:
- raw token identities
- absolute positions
- direct offset sign
- direct offset magnitude
- pooled scalar score as the only feature
- any feature computed after sector pooling that hides sector-level structure

## Why this matters
The point of the witness head is not to let a classical model solve the task freely.

The point is to test whether:
- sector-first quantum responses contain usable relational evidence

So the feature schema must remain:
- small
- explicit
- shortcut-resistant

## Diagnostic requirement
Any future restart using this schema must emit the full feature vector per sample or per run summary so the head’s inputs are auditable.

## Bottom line
The witness-head path is only legitimate if the head sees:
- sector-resolved quantum evidence
- and nothing richer than the declared relational contrasts
