# Q-RoPE Photonic Provider Fallback Decision v1

## Decision
- Do not assume a paid direct-Quandela option fixes the current issue.
- Treat the current direct-Quandela problem as a provider/API execution-path issue, not a clearly documented account-tier limitation.
- Preferred fallback path: Perceval via `ScalewaySession`.

## Rationale
- Perceval provider docs expose Quandela and Scaleway as separate provider paths.
- The Quandela docs document token/session usage, but do not document a paid tier switch that changes remote submission semantics for `sim:slos`.
- Scaleway QaaS explicitly offers Quandela access, including emulated and real photonic platforms, through a built-in Perceval provider path.

## Operational interpretation
- Paying for direct Quandela may improve quotas or access in some cases, but we do not currently have source-backed evidence that it resolves the provider-side `400` submission failures we are seeing.
- Therefore, “upgrade direct Quandela” is not the primary next move.
- The primary next move is to evaluate the alternative photonic provider path while preserving photonic-first strategy.

## Recommended next step
- Add a Scaleway provider onboarding/integration story.
- Keep IBM as the non-photonic secondary comparator.
- Keep direct Quandela artifacts as valid supplemental evidence, but stop treating direct Quandela as the only photonic cloud path.

## Sources
- Perceval providers docs: direct Quandela and Scaleway sessions are both first-class provider paths.
- Scaleway QaaS docs/marketing: Quandela QPUs and emulated photonic access are available through Scaleway.
