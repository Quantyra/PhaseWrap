# Reviewer Start

This is the shortest no-credentials path through PhaseWrap.

## What This Repo Claims

PhaseWrap is a negative-results and methodology package. It shows, with reproducible artifacts, that the fixed-period PhaseWrap scoring line did not support a RoPE-replacement claim and that assistance pipelines can repair retrieval benchmarks without isolating the positional mechanism under test.

The most transferable result is the Stage 67-96 methodology arc, especially Stage 80/81: support-routed repairs solve phase-cued retrieval for every tested method, including `no_position`.

## What This Repo Does Not Claim

- No RoPE replacement.
- No production-transformer improvement.
- No quantum advantage.
- No entanglement-based advantage.
- No broad cross-backend hardware robustness.
- No claim that the general shortcut/control-task warning is novel.

## Verify Without Credentials

Recommended single command:

```bash
python -m qrope.verify_publication --profile public
```

Equivalent installed console command:

```bash
phasewrap-verify --profile public
```

Expected output:

```text
PHASEWRAP_PUBLIC_VERIFY_PASS
```

Equivalent legacy script:

```bash
python scripts/verify_publication_package.py
```

Expected output:

```text
PUBLICATION_PACKAGE_VERIFY_PASS
```

## Read In This Order

1. [Stage-to-claim map](docs/stage-to-claim-map.md)
2. [Methodology paper draft](docs/publication/phasewrap-methodology-paper-v1.md)
3. [Novelty and prior-work supplement](docs/publication/post-publication-novelty-and-prior-work-supplement-v1.md)
4. [Scoring API reference](docs/api/scoring.md)
5. [Reproducible review environment](docs/reproducible-environment.md)

## How To Cite Or Review

Use the Zenodo DOI and `CITATION.cff` for citation metadata. For review, start with the public verifier above and open issues against the specific stage, claim row, or artifact path being challenged.

## Hardware-Positive Means Bounded Readout Audit

`Hardware-positive` in this repository means a bounded two-qubit readout-audit result on archived packets. It does not imply RoPE replacement, transformer-scale improvement, quantum advantage, or general hardware robustness.

## Full Audit Tree

The full stage history is preserved for provenance. Reviewers do not need to read every stage first. Use the [stage-to-claim map](docs/stage-to-claim-map.md) to identify the headline evidence and the full audit pointers.
