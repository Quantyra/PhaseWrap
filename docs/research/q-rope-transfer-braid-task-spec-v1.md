# Q-RoPE Transfer Braid Task Spec v1

Date: 2026-03-12
Stories: S933

## Task
`synthetic_symbolic_insufficiency_braid_crossing_response`

## Structure
Each sample contains:
- two relational channels with ordered crossing points
- declared summaries for each channel before and after crossing
- one target that depends on the consistency of the ordered crossing pattern rather than any single local channel summary

## Target Intent
The regression target should vary with:
- ordered crossing residual structure
- cross-channel reconciliation after crossing
- direction-sensitive interaction between pre-crossing and post-crossing summaries

The target should not be reconstructable from:
- coarse braid-state ids alone
- single-channel declared summaries alone
- a bounded additive/quadratic symbolic family over declared braid summaries only

## Required Generator Diagnostics
- `coarse_braid_state_null_pass`
- `within_braid_state_variation_pass`
- `latent_braid_diversity_pass`
- `crossing_target_nontrivial_pass`
- `token_view_balance_pass`
- `channel_balance_pass`

## Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- metrics:
  - `mae`
  - `rank_correlation`
