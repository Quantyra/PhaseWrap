# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Rank-Only Task Spec v1

Date: 2026-03-10
Status: memo-only
Story: S518

## Task
- task id: `synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only`
- supervision type: listwise ranking reduced to top-k rank structure only

## Design Goal
- make top-k rank structure primary
- remove top-k separation magnitude from the supervised target
- preserve latent slot invariance by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_rank_lookup_near_null_pass = true`
- `within_state_topk_rank_variation_pass = true`

## Intended Primary Metrics
- `accuracy`
- `order_f1`

## Scope Constraint
- memo-only until a dedicated approval gate exists
