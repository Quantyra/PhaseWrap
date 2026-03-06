# Q-RoPE Phase 2: Rigor and Hardware Plan v1

## Objective
Convert the completed local real-mode matrix into publishable evidence with stronger statistical validity and hardware-relevant results.

## Current baseline state
- Matrix coverage: `real=42`, `dry=0` in `summary_v1.csv`.
- Datasets currently used: local handcrafted slices (`yelp`, `imdb`, `amazon`).
- Limitation: sample sizes and data realism are not yet publication-grade.

## Statistical rigor plan
1. Increase seed count from 3 to at least 10 per variant/dataset.
2. Expand dataset size per domain (target >= 1,000 examples per dataset for phase-2 local studies).
3. Report, at minimum:
- mean and standard deviation
- 95% confidence intervals
- pairwise effect sizes (`V3` vs `V2`, `V1`, `V0`)
- nonparametric and/or bootstrap significance checks
4. Add per-variant run-failure and variance diagnostics.

## Experimental integrity checks
1. Fixed split protocol with checksum-tracked manifests.
2. Equal compute budget and hyperparameter budget across variants.
3. Pre-registered acceptance criteria for progression decisions.

## Hardware expansion plan (Quantyra-aligned)
### Primary: photonic track
- Stage P1: photonic simulator parity runs for selected slices.
- Stage P2: limited photonic hardware runs (Quandela/Xanadu path) for top-priority slices.

### Secondary: IBM comparator track
- Stage I1: run matched subset on IBM-compatible path for cross-platform robustness.
- Keep IBM results as comparator evidence, not primary identity.

## Minimum progression gates
Gate R1 (statistical readiness):
- >= 10 seeds completed for one dataset across `V0-V3`.
- CI/effect-size package generated.

Gate R2 (multi-dataset readiness):
- same package for at least two datasets.

Gate H1 (hardware readiness):
- one photonic simulator slice + one photonic hardware slice completed.

Gate H2 (cross-platform robustness):
- one IBM comparator slice completed with documented limitations.

## Deliverables for phase 2
1. `summary_v2.csv` + `report_v2.md` with CI/effect sizes.
2. Dataset manifest and split checksums.
3. Hardware run ledger (backend, queue, shots, cost/time).
4. Updated novelty/publishability memo with empirical claims only.
