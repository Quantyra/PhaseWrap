from __future__ import annotations

from typing import Any

from qrope.provider_adapters.common import ProviderAdapterBlocked, ProviderAdapterStatus, env_present, module_available


PROVIDER = "amazon_braket"
SUBMITTER_IMPORT_PATH = "qrope.provider_adapters.amazon_braket:submit"
REQUIRED_ENV = ("QROPE_BRAKET_DEVICE_ARN", "QROPE_BRAKET_OUTPUT_S3_BUCKET", "QROPE_BRAKET_AWS_REGION")


def adapter_status() -> dict[str, Any]:
    return ProviderAdapterStatus(
        provider=PROVIDER,
        submitter_import_path=SUBMITTER_IMPORT_PATH,
        sdk_modules={
            "boto3": module_available("boto3"),
            "braket": module_available("braket"),
        },
        required_env=REQUIRED_ENV,
        required_env_present=env_present(REQUIRED_ENV),
        live_submission_implemented=False,
        no_hardware_submission=True,
    ).as_dict()


def submit(*, provider: str, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if provider != PROVIDER:
        raise ProviderAdapterBlocked(f"Amazon Braket adapter received provider={provider!r}")
    if len(jobs) != len(payloads):
        raise ProviderAdapterBlocked("job/payload count mismatch before Amazon Braket submission")
    status = adapter_status()
    raise ProviderAdapterBlocked(
        "Amazon Braket live submission adapter is intentionally blocked; "
        f"blockers={', '.join(status['blockers'])}"
    )
