# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Consistency Task Spec v1

Date: 2026-03-10
Stories: S500

## Task
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary`

## Objective
- supervise whether the top-k ordering pattern remains consistent under slot-invariant ordered transition structure
- preserve slot identity as a nuisance variable by construction
- remove the full-list target from the stopped rank-only branch

## Generator Contract
- latent slot invariance must hold exactly
- coarse top-k consistency lookup must be near-null
- within-state top-k consistency variation must be present
- slot-view balance must hold

## Primary Metrics
- `accuracy`
- `f1`

## Rejection Rule
- reject any continuation that reintroduces full-list order quality as the primary supervised target
