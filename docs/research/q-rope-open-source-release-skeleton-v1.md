# Q-RoPE Open-Source Release Skeleton v1

## Objective
Define the minimum repository structure and governance files for Phase A open-source release.

## Phase A publish set
1. Algorithm code (Q-RoPE + baselines V0-V2 comparators)
2. Configs and seeds
3. Reproduction runbook
4. Aggregate reporting scripts

## Required repo layout
```text
src/
  qrope/
    run.py
    aggregate.py
    report.py
configs/
  ablation/
docs/
  research/
logs/
tests/
```

## Required public files
1. `README.md` with quickstart and experiment matrix
2. `LICENSE` (Apache-2.0 recommended)
3. `CONTRIBUTING.md` with coding and reproducibility rules
4. `CITATION.cff`
5. `SECURITY.md` (minimal disclosure policy)
6. `CODE_OF_CONDUCT.md`

## Secrets and safety exclusions
- Do not publish cloud tokens, account IDs, or billing artifacts.
- Keep private datasets or contract-restricted assets out of release.
- Publish only sanitized logs.

## Reproducibility checklist
1. Pin dependency versions.
2. Include fixed seed list and split definitions.
3. Include expected output schema and sample output files.
4. Include command-line examples for `V0-V3`.

## Release gate
Before opening repository:
1. Run secret scan.
2. Verify runbook commands on clean environment.
3. Verify all links in `README.md`.
4. Confirm claim language matches S005 allowed claims.
