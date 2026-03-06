# Q-RoPE Quandela Remap/Skip Note v1

## Chosen policy
- Chosen policy: explicit sample-level skip after bounded retries.
- Implementation point: `qrope.run.collect_quandela_scores(...)`
- Failure policy: if too few samples remain after skips, fail the run as non-meaningful rather than emit misleading metrics.

## Why this policy
- Provider behavior was too unstable for a trustworthy deterministic remap.
- A coarse remap would have changed the photonic scoring semantics without evidence that the new region is truly stable.
- Skip policy preserves honesty: blocked provider points reduce coverage instead of being silently rewritten.

## Outcome
- The skip policy is now explicit in code.
- It still does not rescue seed `123` for Quandela `V2` and `V3`; too few retained samples remain for a meaningful run.
- So the next decision is no longer “retry or not,” it is “change provider path, remap semantics, or stop claiming broad Quandela coverage.”

## Comparability impact
- Prior successful Quandela artifacts remain comparable to each other.
- Failed seed `123` / `V2` and `V3` remain missing by design, not by accident.
- This weakens any claim that the current Quandela adapter supports robust seed coverage under the present mapping.
