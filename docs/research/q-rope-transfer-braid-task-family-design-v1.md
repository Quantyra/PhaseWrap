# Q-RoPE Transfer Braid Task Family Design v1

Date: 2026-03-12
Stories: S932

## Goal
Open a fourth materially different transfer family that tests whether the standing witness advantage survives an interleaved crossing topology rather than a path, loop, or fork-join topology.

## Why Braid
The current bounded transfer evidence covers:
- path-local composition
- loop-closure composition
- fork-join branch and rejoin composition

The next materially different topology should require:
- two relational channels that cross in ordered fashion
- target dependence on the interaction between crossings, not only local channel summaries
- resistance to a bounded symbolic family over declared braid summaries only

That is stricter than a path, different from a loop, and not reducible to a simple fork-join reconciliation.

## Design Principle
The target should depend on ordered crossing structure across two interleaved relational channels while remaining resistant to a bounded symbolic family over declared braid summaries.

## Planned Line
- task family:
  - `braid_crossing`
- first exact task:
  - `synthetic_symbolic_insufficiency_braid_crossing_response`
- witness candidate:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
- bounded control family:
  - braid-local additive and bounded-quadratic regressor over declared braid summaries only
