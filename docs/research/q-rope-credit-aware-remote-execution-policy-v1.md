# Q-RoPE Credit-Aware Remote Execution Policy v1

## Purpose
Prevent limited provider credits from being consumed implicitly during routine research work.

## Provider budget posture
- Quandela credits are limited and should be treated as a constrained experimental budget.
- IBM usage does not consume Quandela credits.
- Local simulators and documentation/process work do not consume Quandela credits.

## Zero-credit activities
- Story writing, checkpoint updates, evidence logging, and literature/planning work
- Local code changes and local unit tests
- `sim_local`, `sim_quantum_statevector`, and `sim_qiskit_aer` runs
- Scaleway onboarding documentation and local script preparation without remote submission

## Credit-consuming activities
- Any `sim_quandela_remote` execution
- Any direct replay of Quandela remote job payloads against the live API
- Any future real photonic hardware submission through Quandela-backed paths

## Execution rules
1. Do not launch Quandela remote runs silently.
2. Before any new Quandela execution wave, state:
- intended run IDs
- whether the run is exploratory or protocol-critical
- why local/IBM evidence is insufficient
3. Prefer the smallest useful evidence packet:
- single rerun before wave rerun
- matched slice before wider slice
- one seed before multi-seed expansion
4. If a story can be completed with zero-credit work, do that first.
5. If direct Quandela becomes credit-constrained again, pause further direct execution and re-evaluate fallback/provider options before continuing.

## Current implication
- We can continue protocol/documentation/onboarding work without spending Quandela credits.
- We should spend Quandela credits only on high-value empirical steps that materially change the evidence state.

## Current evidence-based estimate
- We do not have a verified source-backed credit-per-run formula for direct Quandela usage.
- Therefore we cannot responsibly promise an exact number of remaining experimental runs from the current 100-credit balance.
- Budget decisions must be made conservatively and announced before execution.
