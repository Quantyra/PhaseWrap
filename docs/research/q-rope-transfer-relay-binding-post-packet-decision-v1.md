# Relay-Binding Post-Packet Decision v1

Decision: continue

Reason:
- The corrected relay-binding witness beat the bounded symbolic control on both declared packet metrics.
- Generator and audit diagnostics passed.
- The next bounded step is nuisance hardening, not scope expansion.

Next bounded step:
- `token_permutation=cdab`
- keep only the relay witness and bounded symbolic control
- stop immediately if the control matches or beats the witness on both `mae` and `rank_correlation`
