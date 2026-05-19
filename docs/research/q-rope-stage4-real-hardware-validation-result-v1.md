# Q-RoPE Stage 4 Real-Hardware Validation Result v1

Date: 2026-05-19

## Result

Stage 4 real-hardware validation has completed on IBM Runtime and Amazon Braket/Rigetti. The Braket replication artifact is the preferred current cross-provider evidence item because it was run after the Braket preparation adapter was added and verified with a 1000-shot-per-row hardware gate.

### Amazon Braket / Rigetti Result

- status: `PASS`
- outcome: `hardware-positive`
- provider: `amazon_braket`
- backend: `arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q`
- packet id: `qrope-hardware-5244f90bce2f93b8`
- frozen rows: `8`
- shots per row: `1000`
- hardware tasks: `8`
- task status: all `COMPLETED`
- output bucket: `amazon-braket-us-west-1-485386182336`
- offline verifier result: `pass`

| Variant | MAE | Rank Corr |
| --- | ---: | ---: |
| witness | 0.069901 | 0.786644 |
| control | 0.149995 | 0.121232 |

Gates:

- metadata complete: `true`
- comparability pass: `true`
- hardware direction positive: `true`
- noisy-simulator direction positive: `true`
- direction agreement: `true`
- fail reasons: none

Evidence:

- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/summary.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/preflight.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/execution.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/offline_verification.json`
- `docs/evidence/E002-braket-hardware-runbook.md`

### IBM Runtime Result

Stage 4 real-hardware validation also completed on IBM Runtime and passed the declared deterministic hardware gates.

- status: `PASS`
- outcome: `hardware-positive`
- provider: `ibm_runtime`
- backend: `ibm_fez`
- job id: `d84jbq00bvlc73d4krr0`
- packet id: `qrope-hardware-73c61893576297ff`
- frozen rows: `16`
- shots per row: `4096`
- submitted at UTC: `2026-05-17T03:28:38Z`
- completed at UTC: `2026-05-17T03:29:05Z`
- calibration metadata captured: yes
- backend properties available: yes
- qubits reported: `156`

## IBM Metrics

| Variant | MAE | Rank Corr |
| --- | ---: | ---: |
| witness | 0.018382 | 0.876558 |
| control | 0.217262 | -0.176940 |

## IBM Gates

- metadata complete: `true`
- comparability pass: `true`
- hardware direction positive: `true`
- noisy-simulator direction positive: `true`
- direction agreement: `true`
- fail reasons: none

## IBM Offline Verification

- verifier: `scripts/verify_stage4_hardware_packet.py`
- input packet: `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- input execution: `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- no hardware submission: `true`
- verifier result: `pass`
- output: `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`

## Boundary

These are bounded real-noisy-hardware results for frozen Stage 4 packets on IBM `ibm_fez` and Amazon Braket/Rigetti `Cepheus-1-108Q`. They support the Stage 4 claim boundary produced by the automated ladder: bounded real-noisy-hardware packets. They do not generalize beyond the frozen packets, backends, dates, calibration windows, and declared metrics.

## Evidence

- `logs/automated_stage_gates/stage4_hardware_packet/summary.json`
- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/preflight.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `docs/research/q-rope-stage4-hardware-packet-v1.md`
