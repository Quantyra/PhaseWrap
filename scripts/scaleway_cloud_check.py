from __future__ import annotations

import os
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

    project_id = os.environ.get("SCALEWAY_PROJECT_ID", "").strip()
    token = os.environ.get("SCALEWAY_SECRET_KEY", "").strip()
    platform_name = os.environ.get("SCALEWAY_QAAS_PLATFORM", "").strip() or "sim:sampling:h100"

    if not project_id:
        print("SCALEWAY_PROJECT_ID is missing.")
        return 1
    if not token:
        print("SCALEWAY_SECRET_KEY is missing.")
        return 1

    try:
        from perceval.providers.scaleway import Session as ScalewaySession
    except Exception as exc:
        print(f"Failed to import ScalewaySession: {exc}")
        return 1

    try:
        session = ScalewaySession(platform_name=platform_name, project_id=project_id, token=token)
        processor = session.build_remote_processor()
        print("Scaleway Perceval connectivity initialized.")
        print(f"Platform: {platform_name}")
        try:
            print(f"Processor name: {processor.name}")
        except Exception:
            pass
    except Exception as exc:
        print(f"Failed to initialize Scaleway Perceval path: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
