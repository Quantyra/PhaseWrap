# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Consistency Task Specification v1

Date: 2026-03-11
Stories: S590

## Task ID
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary`

## Objective
- predict whether the latent signed top-k pair-order relation flips across two slot-invariant paired contexts
- positive label means the signed pair-order flips across the paired contexts
- negative label means the signed pair-order is preserved across the paired contexts

## Construction Rule
- start from the same slot-invariant latent state family used by the stopped signed-consistency line
- preserve latent slot invariance by construction under paired rendered views
- for each retained coarse slot-invariant state, construct paired contexts `A` and `B` that keep the same coarse state but change within-state pair-order realization
- derive one latent signed top-k pair-order quantity per context
- emit a binary flip label from `sign(pair_order_A) != sign(pair_order_B)` only
- enforce class balance inside each coarse slot state so coarse signed-flip lookup should be near-null by construction
- keep token identity and slot identity as nuisance variables rather than label carriers

## Required Generator Diagnostics
- `latent_slot_invariance_pass`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass`
- `coarse_slot_topk_pair_signed_flip_lookup_near_null_pass`
- `within_state_topk_pair_signed_flip_variation_pass`
- `paired_context_diversity_pass`
- `signed_flip_label_balance_pass`

## Why This Is Materially Different
- the stopped signed-consistency branch supervised directional agreement across paired contexts
- this line makes directional flip-versus-hold the primary supervised object
- it tests whether the witness preserves useful signal specifically in controlled directional reversals rather than generic consistency

## Rejection Rule
- reject the task if coarse slot state alone predicts flip imbalance away from the centered global rate
- reject the task if paired contexts collapse to one effective view
- reject the task if within-state signed-flip variation collapses
