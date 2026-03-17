# Q-RoPE E010 Nested-Scope Shadow Gate v1

Date: 2026-03-17
Stories: S1578-S1579

## BLUF
- `E010` passes only if it stays genuinely hierarchical and bounded.
- The task must require two locally eligible candidates inside nested active scopes.
- Exactly one final valid target may remain after nearer-scope shadow precedence is applied.

## Frozen Task
- `synthetic_positional_nested_scope_shadow_selection_response`

## Required Structure
- one bounded candidate memory
- exactly two nested active scopes
- at least two candidates that satisfy the same base positional-content rule while remaining locally eligible in different active scopes
- exactly one final valid target after nearer-scope shadow precedence is applied
- the nearer-scope candidate must be decision-critical rather than recoverable from a flat scope mask alone

## Allowed Symbolic Family
- one frozen symbolic family only
- declared query summaries
- per-candidate bounded content summaries
- per-candidate bounded positional summaries
- bounded aggregate nested-scope ambiguity summaries
- bounded precedence-conflict summaries

## Blocked By Default
- token-id shortcuts
- slot-id shortcuts
- explicit scope-id lookup tables
- direct precedence labels as model inputs
- flat in-scope/out-of-scope shortcut families
- per-shadow-pattern symbolic families
- count-specific symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates

## Required Hard-Stop Diagnostics
- `coarse_nested_scope_shadow_state_null_pass`
- `within_nested_scope_shadow_state_variation_pass`
- `two_local_candidates_nontrivial_pass`
- `near_scope_precedence_nontrivial_pass`
- `flat_scope_mask_null_pass`
- `content_only_null_pass`
- `position_only_null_pass`
- `final_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `nested_scope_noncollapse_pass`

## Hard Stop
- Stop `E010` immediately if the task collapses into flat scope masking, explicit scope lookup, slot heuristics, or fairness blow-up.
