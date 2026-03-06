# Q-RoPE Quandela Credit Recovery Note v1

## Finding
- After adding Quandela credits, the previously blocked direct-Quandela runs completed successfully:
  - `v2-yelp-quandela-s123`
  - `v3-yelp-quandela-s123`
- Both completed with `data_mode` suffix `skip0`, which means the current skip policy was not needed for these reruns.

## Interpretation
- This materially strengthens the earlier root-cause diagnosis that the direct-Quandela failures were primarily driven by account/provider credit state.
- Local hardening work remains useful because it improves diagnostics and bounded failure handling.
- However, the funded account state removes the immediate execution block for the current supplemental packet.

## Program impact
- Direct Quandela can remain the photonic-primary cloud path.
- Scaleway remains a fallback option, not the immediate critical path.
- The next sensible protocol move is to continue empirical expansion rather than fallback onboarding.
