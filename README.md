# PhaseWrap-RoPE

[![CI](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml)

PhaseWrap-RoPE is Quantyra's public research repository for phase-wrap positional scoring and bounded hardware validation.

The primary artifact is the paper: [PhaseWrap-RoPE repository paper v1](docs/publication/qrope-paper-v1.md). The code, figures, and evidence packets support that paper.

## Paper

- [PhaseWrap-RoPE repository paper v1](docs/publication/qrope-paper-v1.md)

The paper is the intended review entry point. It defines the method, claim boundary, validation protocol, and hardware evidence record.

## Scope

PhaseWrap-RoPE presents:

- phase-wrap residual features using mod-8 and mod-12 structure;
- a cross-band score computed from the product of the mod-8 and mod-12 signed margins;
- deterministic validation packets with raw counts, backend metadata, and offline recomputation;
- a bounded Stage 4 real-hardware validation result;
- a completed hardware comparison report covering the product-state witness and entangling CX witness family.

The paper does not claim broad quantum advantage, full transformer-scale superiority, or general cross-backend robustness.

## Status

- `Evidence`: bounded Stage 4 hardware-positive result for the recorded packet/backend/date/calibration context.
- `Hardware`: IBM Quantum is the primary Stage 4 hardware lane; IonQ and Quandela paths require explicit provider configuration.
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Patent/IP`: patent pending; USPTO provisional application `64/068,121`. Additional receipt identifiers are retained in internal IP records.

## Quickstart

Recommended local environment: Python `3.11+`.

```bash
python -m pip install -e ".[dev]"
```

Run a local method check with no provider credentials:

```bash
python - <<'PY'
from qrope.automated_stage_gates import phase_margins, normalized_phase_label

margins = phase_margins(delta_a=1, delta_b=4)
print(margins)
print("label", normalized_phase_label(margins["score"]))
PY
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

Install provider dependencies only when preparing a hardware rerun:

```bash
python -m pip install -e ".[ibm]"
```

## Reviewer Path

- Read the paper.
- Inspect the Stage 4 packet files under `logs/automated_stage_gates/stage4_hardware_packet/`.
- Run `python scripts/verify_stage4_hardware_packet.py`.
- Compare the verifier output with `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`.

## Appendix: Figures

- [Method schematic](docs/publication/figures/qrope-method-schematic-v1.svg)
- [Validation pipeline](docs/publication/figures/qrope-validation-pipeline-v1.svg)
- [Stage 4 hardware comparison](docs/publication/figures/qrope-stage4-comparison-v1.svg)

## Appendix: Supporting Documents

- [Patent status note](docs/publication/patent-status-note-v1.md)
- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Phase-wrap algorithm note](docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md)

## Appendix: Licensing and Patent Notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP boundaries are documented in [PATENTS.md](PATENTS.md).
