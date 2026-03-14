# Q-RoPE Realism-Bridge Offset-Retrieval Task Family Design v1

Date: 2026-03-14
Stories: S1223-S1225

## Missing Question
- Does the current selective bridge signal survive on a task that looks more like relative-position retrieval than the current synthetic bridge set?

## Candidate
- Task family: `synthetic_positional_offset_retrieval_response`
- Proposed witness: `V_future_relational_witness_positional_offset_retrieval`
- Proposed bounded control: additive and bounded-quadratic regressor over declared offset-retrieval summaries only

## Core Structure
- sequence frame with a designated query anchor
- a retrieval target defined by a relative offset from the anchor
- distractor candidates that share token identity or local statistics but differ in relative position
- final resolution depends on whether the model preserves the correct relative-offset retrieval relation rather than only local order, local distance, or simple span membership

## Why This Is Realism-Bridge
- It is closer to actual positional encoding behavior because it pressures an anchor-to-target retrieval relation, not only a static positional relation.
- It is more model-like than the current bridge set because relative retrieval under distractors is closer to the kind of positional dependence that attention mechanisms must preserve.

## Material Difference From Existing Bridge Set
- not just order around an anchor
- not just nearer/farther distance
- not just interval containment
- not just signed offset class
- not just ordered betweenness
- instead: relative-position retrieval under distractor competition
