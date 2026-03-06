# Cloud Account Onboarding Checklist (Human-in-the-Loop)

## Purpose
Track account setup steps that require user action for cloud quantum services.

## Status legend
- `TODO` not started
- `WAITING_USER` requires user action
- `DONE` complete

## IBM Quantum
1. Create or confirm IBM Quantum account at `https://quantum.cloud.ibm.com` (`DONE`).
2. Retrieve API token from IBM Quantum account/dashboard per `https://docs.quantum.ibm.com/guides/setup-channel` (`DONE`).
3. Share token securely for local env setup (`DONE`).
4. Set local environment variable:
- `IBM_QUANTUM_TOKEN=<token>` (`DONE`)
5. `IBM_QUANTUM_INSTANCE_CRN` is optional for initial connectivity; leave blank if unknown (`DONE`).
6. Run connectivity check script `scripts/ibm_runtime_check.py` (`DONE`).

## Quandela / Perceval Cloud
1. Create or confirm Quandela cloud account at `https://cloud.quandela.com` (`DONE`).
2. Generate cloud token from the account page per `https://perceval.quandela.net/docs/v1.1/notebooks/Remote_Computation_Tutorial.html` (`DONE`).
3. Share token securely for local env setup (`DONE`).
4. Set local environment variable:
- `QUANDELA_CLOUD_TOKEN=<token>` (`DONE`)
5. Optional platform selector:
- `QUANDELA_PLATFORM=sim:slos` (`DONE`)
6. Run connectivity check script `scripts/quandela_cloud_check.py` (`DONE`).

## Scaleway QaaS / Perceval Fallback
1. Create or confirm Scaleway account at `https://console.scaleway.com` (`TODO`).
2. Create or identify the target Scaleway project and copy its project UUID per `https://www.scaleway.com/en/docs/quantum-computing/quickstart/` (`TODO`).
3. Create an API key / secret key with sufficient IAM permissions per `https://www.scaleway.com/en/docs/iam/how-to/create-api-keys` (`TODO`).
4. Set local environment variables:
- `SCALEWAY_PROJECT_ID=<project-uuid>` (`TODO`)
- `SCALEWAY_SECRET_KEY=<secret-key>` (`TODO`)
5. Optional Perceval platform selector:
- `SCALEWAY_QAAS_PLATFORM=sim:sampling:h100` (`TODO`)
6. Run connectivity check script `scripts/scaleway_cloud_check.py` (`TODO`).

## Xanadu Cloud
- Status: `DEFERRED`
- Rationale: user reports Xanadu Cloud is no longer available for this project path.
- Policy: do not block execution on Xanadu onboarding.
- If service availability changes later, re-open a dedicated onboarding story before adding credentials.

## Security notes
- Never commit tokens to source control.
- Prefer temporary session env vars for testing.
- Rotate tokens after initial validation if shared through insecure channels.
