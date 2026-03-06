from __future__ import annotations

import os
import sys
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    token = os.environ.get("IBM_QUANTUM_TOKEN", "").strip()
    instance = os.environ.get("IBM_QUANTUM_INSTANCE_CRN", "").strip()
    if not token:
        print("IBM_QUANTUM_TOKEN is missing.")
        return 1

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except Exception as exc:
        print(f"Failed to import qiskit_ibm_runtime: {exc}")
        return 1

    kwargs = {"channel": "ibm_cloud", "token": token}
    if instance:
        kwargs["instance"] = instance

    try:
        service = QiskitRuntimeService(**kwargs)
    except Exception as exc:
        print(f"Failed to initialize QiskitRuntimeService: {exc}")
        return 2

    print("IBM Runtime connection initialized.")
    print(f"Instance provided: {'yes' if instance else 'no'}")

    try:
        backend_names = [backend.name for backend in service.backends()]
        print(f"Backend count: {len(backend_names)}")
        for name in backend_names[:10]:
            print(f"backend: {name}")
    except Exception as exc:
        print(f"Connected, but failed to list backends: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
