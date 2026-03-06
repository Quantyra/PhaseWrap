# Q-RoPE Three-Seed Remote Synthesis v1

## Scope
- Dataset: `yelp`
- Slice policy: balanced 12-sample remote slice
- Seeds: `42`, `123`, `777`
- Variants: `V0`, `V2`, `V3`
- Backends: direct Quandela photonic remote and IBM Runtime remote

## Supported claims
- We have real remote execution evidence on both providers for the matched 3-seed packet.
- The remote packet is sufficient to show strong seed sensitivity on both providers.
- The remote packet is sufficient to reject a simple, stable cross-provider claim such as:
  - “`V3` consistently beats `V0` on both providers”
  - “`V2` behaves similarly across providers”
  - “provider ranking differences are minor noise”

## Unsupported claims
- We cannot claim stable remote superiority of `V3` over baselines.
- We cannot claim stable provider agreement on rank ordering.
- We cannot claim this slice predicts broader task-level or production-level behavior.
- We cannot claim a clean hardware bake-off because the provider circuit families are not identical.

## Contradicted candidate narratives
- `V3` as a robustly dominant remote variant:
  - contradicted by seed `123` on IBM and seed `777` on Quandela
- `V2` as a stable midpoint:
  - contradicted by provider- and seed-dependent rank changes
- direct provider consistency:
  - contradicted by the observed rank inversions across seeds

## Operational readout
- Direct Quandela is viable again after credits were added.
- IBM remains operational as a secondary comparator.
- Latency is not stable enough to use as a decisive comparative signal from the current packet.

## Decision
- Another paid Quandela wave is **not justified now**.
- The current packet already answers the most immediate remote question:
  - the remote story is unstable and claim-bounded
- The highest-value next step is zero-credit synthesis, framing, and publication-risk tightening, not more paid execution.

## Conditions that would justify another paid wave
- A specific question that the current packet cannot answer, such as:
  - whether the instability is unique to `yelp`
  - whether the instability survives on a second dataset with the same slice policy
- A minimal run list tied directly to that question
- A clear statement of how the result would change the program decision

## Bottom line
- The 3-seed matched remote packet was worth running.
- It did not validate a strong positive hardware-style narrative.
- It did give us a defensible, decision-grade conclusion: remote behavior is real, but unstable and highly claim-bounded on the current evidence.
