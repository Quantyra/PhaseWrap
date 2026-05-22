from __future__ import annotations

from typing import Any

from qrope.provider_adapters.common import ProviderAdapterBlocked, ProviderAdapterStatus, env_present, module_available


PROVIDER = "ibm_runtime"
SUBMITTER_IMPORT_PATH = "qrope.provider_adapters.ibm_runtime:submit"
REQUIRED_ENV = ("IBM_QUANTUM_TOKEN", "IBM_QUANTUM_INSTANCE_CRN", "QROPE_IBM_BACKEND")


def adapter_status() -> dict[str, Any]:
    return ProviderAdapterStatus(
        provider=PROVIDER,
        submitter_import_path=SUBMITTER_IMPORT_PATH,
        sdk_modules={
            "qiskit": module_available("qiskit"),
            "qiskit_ibm_runtime": module_available("qiskit_ibm_runtime"),
        },
        required_env=REQUIRED_ENV,
        required_env_present=env_present(REQUIRED_ENV),
        live_submission_implemented=False,
        no_hardware_submission=True,
    ).as_dict()


def submit(*, provider: str, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if provider != PROVIDER:
        raise ProviderAdapterBlocked(f"IBM Runtime adapter received provider={provider!r}")
    if len(jobs) != len(payloads):
        raise ProviderAdapterBlocked("job/payload count mismatch before IBM Runtime submission")
    status = adapter_status()
    raise ProviderAdapterBlocked(
        "IBM Runtime live submission adapter is intentionally blocked; "
        f"blockers={', '.join(status['blockers'])}"
    )

