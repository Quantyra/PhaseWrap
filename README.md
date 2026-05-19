# QRoPE

[![CI](https://github.com/Quantyra/QRoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/QRoPE/actions/workflows/ci.yml)

QRoPE is Quantyra's public research repository for phase-wrap positional scoring and bounded hardware validation.

The repository's primary artifact is the paper in `docs/publication/qrope-paper-v1.md`. The code, evidence packets, and figures support that paper and should be read as evidence infrastructure rather than as the headline result.

## Primary publication

- [Repository paper v1](docs/publication/qrope-paper-v1.md)

If you only read one artifact, read the paper first.

## What the paper claims

QRoPE presents:

- phase-wrap residual features using mod-8 and mod-12 structure;
- the SQR score as the product of the mod-8 and mod-12 signed margins;
- deterministic validation packets with raw counts, backend metadata, and offline recomputation;
- a bounded Stage 4 real-hardware validation result;
- a completed hardware comparison report covering the product-state witness and the entangling CX witness family.

The paper does not claim broad quantum advantage, full transformer-scale superiority, or general cross-backend robustness.

## Publication and status

- `Current evidence posture`: Stage 4 real-noisy-hardware positive result for one frozen packet/backend/date/calibration context.
- `Hardware posture`: IBM Quantum is the only hardware lane currently available for QRoPE Stage 4; IonQ and Quandela remain simulator paths unless explicitly reconfigured.
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Patent/IP posture`: USPTO provisional submission received `2026-05-18`; the Electronic Acknowledgement Receipt lists application `64/068,121`; final Filing Receipt pending. See [Patent status note](docs/publication/patent-status-note-v1.md).

## Supporting references

- [Patent status note](docs/publication/patent-status-note-v1.md)
- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [QRoPE method schematic](docs/publication/figures/qrope-method-schematic-v1.svg)
- [Validation pipeline figure](docs/publication/figures/qrope-validation-pipeline-v1.svg)
- [Stage 4 comparison figure](docs/publication/figures/qrope-stage4-comparison-v1.svg)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Phase-wrap algorithm note](docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md)
- [Patent notice](PATENTS.md)
- [Automated terminal human-review packet](docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md)

## Quickstart

Recommended local environment: Python `3.11+`.

```bash
python -m pip install -e ".[dev]"
```

Run a simulator-free local method check with no IBM credentials:

```bash
python - <<'PY'
from qrope.automated_stage_gates import phase_margins, normalized_phase_label

margins = phase_margins(delta_a=1, delta_b=4)
print(margins)
print("label", normalized_phase_label(margins["score"]))
PY
```

Install IBM Runtime dependencies only when preparing a real hardware run:

```bash
python -m pip install -e ".[ibm]"
```

Verify the saved Stage 4 packet arithmetic from the published raw-count evidence:

```bash
python scripts/verify_stage4_hardware_packet.py
```

Expected verifier summary:

```json
{
  "pass": true,
  "provider": "ibm_runtime",
  "backend": "ibm_fez",
  "packet_id": "qrope-hardware-73c61893576297ff",
  "job_ids": ["d84jbq00bvlc73d4krr0"]
}
```

## Reviewer path in 10 minutes

- Read the paper.
- Skim the claim boundary in this README if you want the short version.
- Inspect the Stage 4 packet files under `logs/automated_stage_gates/stage4_hardware_packet/`.
- Run `python scripts/verify_stage4_hardware_packet.py`.

## Appendix: implementation and governance

- [Current evidence posture and claim boundary note](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)

## Appendix: licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP-status boundaries are documented in [PATENTS.md](PATENTS.md) and [Patent status note](docs/publication/patent-status-note-v1.md).
