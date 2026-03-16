# Q-RoPE E006 Multi-Hop Reference Missing Question v1

Date: 2026-03-15
Stories: S1447-S1449

## BLUF
- The next missing question is whether the witness can survive bounded multi-hop positional reference resolution through an intermediate candidate.
- The current package does not answer that question because every preserved survivor still resolves the target directly from the query-conditioned rule.
- Success or failure here would change the interpretation of whether the line has any bounded compositional reference depth beyond direct selection.

## Missing Question
- Can the witness survive a bounded task where the correct target is defined only after first identifying an intermediate candidate and then applying a second bounded positional rule relative to that intermediate, without collapsing to direct slot heuristics, token identity, or symbolic pointer lookup?

## Why The Current Package Does Not Answer It
- `key-query-offset-selection` is direct one-shot selection.
- `dual-anchor-offset-consensus` composes two constraints, but still chooses the target directly rather than through an intermediate reference.
- `variable-cardinality-offset-selection` stresses set growth, not compositional reference depth.
- `content-gated-offset-selection` and `content-alias-disambiguation` strengthen direct position-content disambiguation, not two-stage reference resolution.
- `E005` tested repeated shared-memory query reuse, not chained reference resolution through an intermediate.

## Decision Leverage
- If `yes`, the line moves closer to bounded compositional reference behavior rather than only direct selection.
- If `no`, the current package likely marks the practical ceiling for direct bounded selection and should not imply any multi-hop strength.
