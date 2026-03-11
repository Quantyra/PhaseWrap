# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Recurrence Task Specification v1

Date: 2026-03-11
Stories: S617

## Task ID
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary`

## Objective
- predict whether the latent signed top-k pair-order flip disposition recurs across a retained set of slot-invariant paired contexts under bounded perturbations
- positive label means the same signed-flip pattern reappears after at least one intervening perturbation
- negative label means recurrence fails across the retained paired contexts

## Construction Rule
- start from the same slot-invariant latent state family used by the stopped signed-flip persistence line
- preserve latent slot invariance by construction under paired rendered views
- for each retained coarse slot-invariant state, construct a bounded chain of paired contexts with nontrivial within-state pair-order variation
- derive one latent signed top-k pair-order flip indicator per retained context in the chain
- emit a binary recurrence label from whether the initial signed-flip disposition reappears after the intervening perturbation sequence
- enforce class balance inside each coarse slot state so coarse signed-flip recurrence lookup should be near-null by construction
- keep token identity and slot identity as nuisance variables rather than label carriers

## Required Generator Diagnostics
- `latent_slot_invariance_pass`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass`
- `coarse_slot_topk_pair_signed_flip_recurrence_lookup_near_null_pass`
- `within_state_topk_pair_signed_flip_recurrence_variation_pass`
- `paired_context_diversity_pass`
- `signed_flip_recurrence_label_balance_pass`

## Rejection Rule
- reject the task if coarse slot state alone predicts recurrence imbalance away from the centered global rate
- reject the task if the retained chain collapses to one effective comparison
- reject the task if within-state signed-flip recurrence variation collapses
