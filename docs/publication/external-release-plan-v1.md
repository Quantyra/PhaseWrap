# PhaseWrap-RoPE external release plan v1

Status: `OPTIONAL_ARCHIVAL_RELEASE`

## Scope

The repository is already the primary public review artifact. The paper, figures, code, and hardware evidence can be reviewed directly from the GitHub repository.

Additional archival channels are optional. They should be used only if Quantyra wants an external DOI, archive snapshot, or venue-specific citation artifact.

## Optional Release Paths

- GitHub release tag for a fixed repository snapshot.
- Zenodo DOI if a citable archive is desired.
- OSF project if a supplemental evidence archive is desired.
- arXiv or another preprint server only if Quantyra later decides a formal preprint is useful.

## Current Recommendation

Use the GitHub repository as the review target for now. Keep the paper and figures in `docs/publication/`, preserve hardware evidence under `logs/automated_stage_gates/stage4_hardware_packet/`, and defer external archive work until there is a concrete publication or citation need.

## Release Tag Option

If a repository snapshot is needed, use a conservative review tag:

```text
v0.1.0-review
```
