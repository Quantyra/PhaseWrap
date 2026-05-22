# PhaseWrap-RoPE Stage 106 Hardware Execution Preflight v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 106 adds a no-submission operational preflight before any Stage 101 calibration or Stage 104 matched-packet hardware execution is attempted.

The noisy-hardware protocol now has matched packets, calibration templates, metric rules, packet execution templates, and an independent rerun protocol. Stage 106 checks whether the environment is configured to run that protocol without recording secret values or submitting hardware jobs.

## Reviewer Command

```bash
python scripts/run_stage106_hardware_execution_preflight.py --load-dotenv
```

This writes:

- `logs/automated_stage_gates/stage106_hardware_execution_preflight/manifest.json`
- `logs/automated_stage_gates/stage106_hardware_execution_preflight/results.json`
- `logs/automated_stage_gates/stage106_hardware_execution_preflight/summary.csv`

## Result

Current decision:

`HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED`

This is expected in a no-credential planning state. Stage 106 records which environment variables are present, but never records secret values.

## Required Configuration

Common:

- `QROPE_HARDWARE_BUDGET_USD_CAP`
- `QROPE_HARDWARE_QUEUE_DEPTH_CAP`

IBM Runtime:

- `IBM_QUANTUM_TOKEN` or `QISKIT_IBM_TOKEN`
- `QROPE_IBM_BACKEND` or `QROPE_HARDWARE_BACKEND`
- `IBM_QUANTUM_INSTANCE_CRN`

Amazon Braket:

- `AWS_ACCESS_KEY_ID` or `AWS_PROFILE`
- `QROPE_BRAKET_DEVICE_ARN` or `QROPE_BRAKET_DEVICE_ARNS`
- `QROPE_BRAKET_OUTPUT_S3_BUCKET`
- `QROPE_BRAKET_AWS_REGION` or `AWS_REGION`

## Claim Boundary

Supported:

- a no-submission hardware execution configuration preflight for the Stage 105 rerun protocol;
- provider-level readiness/blocker reporting without recording secret values;
- a gate preventing ad hoc hardware attempts without backend, budget, queue, and artifact destination configuration.

Excluded:

- backend availability discovery;
- real hardware submission;
- completed calibration or matched packet execution;
- a noisy-hardware robustness result.

## Next Gate

Set provider credentials, backend selections, budget caps, queue caps, and artifact destinations; rerun Stage 106, then execute Stage 101 and Stage 104 only if the preflight is ready.
