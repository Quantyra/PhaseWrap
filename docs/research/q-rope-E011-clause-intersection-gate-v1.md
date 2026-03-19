# Q-RoPE E011 Clause-Intersection Gate v1

Date: 2026-03-19
Stories: S1610-S1611

## BLUF
- E011 passes only if it stays genuinely conjunctive and bounded.
- The task must require two explicit bounded clauses that are both decision-critical.
- Neither clause may determine the final target alone.

## Frozen Task
- synthetic_positional_clause_intersection_reference_selection_response

## Required Structure
- one bounded candidate memory
- exactly two explicit bounded query clauses
- one positional clause and one content-role clause
- each clause alone must leave multiple candidates viable
- exactly one final valid target may remain after both clauses are applied together
- the joint intersection must be decision-critical rather than recoverable from either clause alone or from a direct lookup shortcut

## Allowed Symbolic Family
- one frozen symbolic family only
- declared query summaries
- per-candidate bounded content summaries
- per-candidate bounded positional summaries
- bounded aggregate clause-ambiguity summaries
- bounded intersection-conflict summaries

## Blocked By Default
- token-id shortcuts
- slot-id shortcuts
- explicit clause-pattern lookup tables
- direct intersection labels as model inputs
- clause-order-specific symbolic families
- count-specific symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates

## Required Hard-Stop Diagnostics
- coarse_clause_intersection_state_null_pass
- within_clause_intersection_state_variation_pass
- clause_one_only_null_pass
- clause_two_only_null_pass
- joint_intersection_nontrivial_pass
- candidate_set_nontrivial_pass
- ounded_candidate_count_pass
- clause_intersection_noncollapse_pass
- 	oken_view_balance_pass
- inal_target_nontrivial_pass

## Hard Stop
- Stop E011 immediately if either clause becomes sufficient alone, if the task collapses into direct lookup behavior, or if the fairness contract requires multiple symbolic families.
