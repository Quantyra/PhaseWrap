# Q-RoPE Credit-Gated Remote Wave Selection v1

## Decision
- Do not spend additional Quandela credits immediately.

## Why
- We already have the smallest high-value packet that materially changes the evidence state:
  - matched `yelp`
  - seeds `42`, `123`, `777`
  - variants `V0`, `V2`, `V3`
  - both providers (`sim_quandela_remote`, `ibm_runtime_remote`)
- That packet is sufficient to show strong seed sensitivity and unstable provider-specific rank ordering.
- A new wave would broaden cost before we have extracted the full value from the packet already paid for.

## What should happen next
- Zero-credit analysis and synthesis of the full 3-seed matched remote packet.
- Only after that, decide whether broader dataset expansion is worth more Quandela spend.

## Spend gate
- Current recommendation: `WAIT`
- Trigger for next paid wave:
  - a concrete analysis question that current 3-seed evidence cannot answer
  - and a minimal proposed run list tied to that question
