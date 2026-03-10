# Q-RoPE Transition Orbit Listwise Post Pair-Reindex Decision v1

Date: 2026-03-11
Stories: S387

## Decision
- keep the branch active
- do not broaden the task or control family yet

## Why
- the first non-inert robustness perturbation did not erase the witness advantage
- the witness stayed ahead of the strongest retained controls on both top-1 accuracy and order-F1

## Bound Next Step
- next bounded step: `pair_reindex = 7` hardening on the same listwise task
- keep the witness fixed
- keep the strongest current symbolic baselines fixed
- keep the scope local-only and zero-credit
