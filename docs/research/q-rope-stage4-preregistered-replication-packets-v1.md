# PhaseWrap Stage 4 Preregistered Replication Packets v1

Date: `2026-05-20`

## Purpose

This artifact preregisters future Stage 4 replication row sets before any additional hardware execution. It is a no-hardware evidence-control artifact: it fixes seeds, row counts, shot counts, witness families, and row-set hashes so future reruns can be checked against a pre-existing packet plan.

Artifacts:

- Manifest: `logs/automated_stage_gates/stage4_preregistered_replication_packets/manifest.json`
- Script: `scripts/preregister_stage4_replication_packets.py`
- Packet files:
  - `logs/automated_stage_gates/stage4_preregistered_replication_packets/ibm_product_seed314_rows16_shots4096.json`
  - `logs/automated_stage_gates/stage4_preregistered_replication_packets/ibm_cx_seed314_rows16_shots4096.json`
  - `logs/automated_stage_gates/stage4_preregistered_replication_packets/braket_product_seed2718_rows8_shots1000.json`
  - `logs/automated_stage_gates/stage4_preregistered_replication_packets/braket_cx_seed2718_rows8_shots1000.json`

Reproduce:

```bash
python scripts/preregister_stage4_replication_packets.py
```

## Preregistered Lanes

| Lane | Provider placeholder | Family | Rows | Shots | Status |
| --- | --- | --- | ---: | ---: | --- |
| `ibm_product_seed314_rows16_shots4096` | IBM backend to be selected | `two_qubit_zz_expectation_phase_wrap_v1` | 16 | 4096 | not submitted |
| `ibm_cx_seed314_rows16_shots4096` | IBM backend to be selected | `two_qubit_cx_parity_phase_wrap_v2` | 16 | 4096 | not submitted |
| `braket_product_seed2718_rows8_shots1000` | Amazon Braket device to be selected | `two_qubit_zz_expectation_phase_wrap_v1` | 8 | 1000 | not submitted |
| `braket_cx_seed2718_rows8_shots1000` | Amazon Braket device to be selected | `two_qubit_cx_parity_phase_wrap_v2` | 8 | 1000 | not submitted |

## Claim Boundary

This artifact does not add hardware evidence. It supports only the process claim that future replication rows and witness families were frozen before future execution. A future run should preserve the row-set hash, family, row count, and shot count, then add real backend metadata, job or task IDs, raw counts, timestamps, and verifier output before being promoted as evidence.
