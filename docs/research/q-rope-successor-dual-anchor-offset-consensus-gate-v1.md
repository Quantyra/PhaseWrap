# Q-RoPE Successor Dual-Anchor Offset Consensus Gate v1

Date: 2026-03-14
Stories: S1298-S1299

## BLUF
- The dual-anchor consensus candidate passes the memo bar only if correctness genuinely depends on two anchors at once and the symbolic control stays bounded.
- This gate does not approve implementation yet.
- It passes only to bounded implementation planning if the candidate-level fairness contract is frozen cleanly.

## Task
- `synthetic_positional_dual_anchor_offset_consensus_response`

## Candidate Intent
- one bounded candidate set
- two anchors
- exactly one candidate that satisfies both anchor-relative positional rules simultaneously
- one or more candidates that satisfy only one anchor rule or match local token statistics while failing the consensus rule

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared dual-anchor summaries, per-candidate summaries, and bounded aggregate consensus summaries only

## Frozen Declared Summary Scope
Allowed declared summaries may include only:
- anchor-a identity summary
- anchor-b identity summary
- per-candidate relative-offset summaries to each anchor
- per-candidate token-identity summaries
- per-candidate single-anchor agreement summaries
- per-candidate dual-anchor consensus summary
- bounded aggregate confusability summaries across the small candidate set

Not allowed:
- latent ids
- candidate lookup tables keyed by microstate identity
- unrestricted higher-order anchor x candidate interactions
- learned attention modules or transformer surrogates

## Required Candidate-Level Admissibility Conditions
The candidate passes only if all are true:
- at least two anchors are genuinely active in defining correctness
- exactly one candidate is correct because it satisfies both declared anchor-relative rules
- at least three candidates are genuinely active in the selection problem
- the task does not collapse into single-anchor scoring only
- the symbolic control can be written as a frozen bounded family with explicit feature audit
- success or failure would still change whether post-successor validation should exist

## Candidate-Level Stop Rule
Stop the candidate immediately if any of the following are true:
- correctness collapses to one anchor only
- the candidate becomes a renamed single-query selection task
- the symbolic control requires lookup blow-up or uncontrolled higher-order interactions
- the task needs larger candidate sets or longer sequences just to stay nontrivial
- the candidate no longer provides decision leverage beyond `key-query-offset-selection`

## Gate Decision Rule
- Pass to bounded implementation planning only if the candidate specification remains clean under this gate.
- Otherwise stop the post-successor class and treat the current package as the practical ceiling.
