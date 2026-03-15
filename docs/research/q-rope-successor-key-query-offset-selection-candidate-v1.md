# Q-RoPE Successor Key-Query Offset Selection Candidate v1

Date: 2026-03-14
Stories: S1263-S1265

## BLUF
- Candidate: `synthetic_positional_key_query_offset_selection_response`
- This candidate is admissible at memo level because it adds query-conditioned selection among bounded competing candidates, not just one anchor-to-target retrieval relation.
- It is still not approved for implementation.

## Decision
- `ADMISSIBLE FOR CANDIDATE-LEVEL GATE REVIEW ONLY`

## Why This Candidate Exists
The current realism-bridge survivor `offset-retrieval` already tested one correct relative-offset relation under distractor pressure.
What it did not test is:
- a bounded candidate-selection setting where the system must choose one candidate from a small set relative to a query anchor.

That difference is the whole point of this candidate.

## Core Structure
- one query anchor
- one small bounded key set, for example 3 or 4 candidates
- exactly one target key identified by a relative-offset rule from the query anchor
- one or more distractor keys sharing token identity or local statistics with the target
- final response depends on selecting the correct key rather than only scoring a single relation

## Why This Is More Model-Like Than `offset-retrieval`
`offset-retrieval` asked:
- does the correct target relation survive against a distractor?

This candidate asks:
- can the correct key be selected from a bounded competing set under a query-relative positional rule?

That adds:
- query-conditioned competition
- one-of-many positional choice
- a small selection problem closer to how attention-like retrieval behaves

## Why This Is Not Just Another Realism-Bridge Variant
It is not enough to rename fields from `offset-retrieval`.
The candidate is only valid if:
- multiple candidates are genuinely active in the scoring problem
- the label depends on selecting the right key from the set
- the symbolic control must reason over bounded candidate summaries rather than one target-plus-one-distractor relation only

If those are not true, reject the candidate.

## Bounded Symbolic Control Sketch
The control should be limited to declared summaries such as:
- query-anchor identity summary
- per-candidate relative-offset summary
- per-candidate token-identity summary
- per-candidate target-agreement summary
- candidate-set confusability summary
- bounded additive and bounded-quadratic interactions only

The control must not receive:
- latent ids
- arbitrary candidate-set lookup tables
- uncontrolled higher-order basis growth
- learned attention modules or transformer surrogates

## Decision Leverage
If this candidate later succeeds under bounded execution:
- a stronger case exists that the witness signal reaches a more model-like positional selection regime.

If it fails cleanly at gate or execution:
- the current package should likely be treated as the practical ceiling for the positional-relevance line.

## Main Risks
- the candidate may collapse back into a dressed-up two-relation retrieval task
- the fairness contract may become too loose once multi-candidate summaries are introduced
- the positive result may still be too synthetic to justify any escalation beyond internal interpretation

## Candidate-Level Gate Questions
Before any implementation plan is allowed, answer all of the following:
- is the candidate genuinely one-of-many selection, not just target-vs-distractor scoring?
- can the symbolic control be written as a frozen bounded family without lookup blow-up?
- does the candidate still work with a very small candidate set?
- would success or failure materially change whether successor-class validation should exist?

## VP-of-Research Judgment
- This candidate is good enough to justify one more memo-level gate review.
- It is not yet good enough to justify code.
