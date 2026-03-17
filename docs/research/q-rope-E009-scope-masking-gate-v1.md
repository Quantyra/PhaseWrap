# Q-RoPE E009 Scope-Masking Gate v1

Date: 2026-03-16

## BLUF
- `E009` passes only to bounded implementation planning review.
- Code and execution remain closed.
- The candidate fails immediately if local-scope eligibility becomes explicit scope lookup, slot heuristics, or a loose fairness contract.

## Frozen Task
- task:
  - `synthetic_positional_scope_masked_reference_selection_response`

## What Must Be True
- the task must contain:
  - one bounded candidate memory
  - one active local scope and one inactive outer region
  - at least one out-of-scope distractor with stronger apparent base positional-content fit than the final in-scope target
  - exactly one final valid in-scope target after scope masking is applied
- local scope membership must be decision-critical rather than decorative
- one frozen symbolic family only across all allowed candidate patterns
- the task must not collapse to simple content-only or position-only solvability by construction

## Blocked By Default
- token-id shortcuts
- slot-id shortcuts
- explicit scope-id lookup tables
- direct in-scope/out-of-scope label lookup features
- count-specific symbolic families
- scope-pattern-specific symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates

## Required Hard-Stop Diagnostics
- `coarse_scope_masking_state_null_pass`
- `within_scope_masking_state_variation_pass`
- `in_scope_target_nontrivial_pass`
- `out_of_scope_distractor_nontrivial_pass`
- `scope_only_null_pass`
- `content_only_null_pass`
- `position_only_null_pass`
- `final_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `scope_noncollapse_pass`

## Decision Rule
- Pass only to bounded implementation planning review.
- Stop immediately if the candidate cannot stay genuinely scope-conditioned under a single frozen symbolic family.
