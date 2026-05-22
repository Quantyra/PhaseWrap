from __future__ import annotations

import sys
from pathlib import Path


RUNNER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNNER_DIR))

from runner_guard import run_guarded_provider_runner  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_guarded_provider_runner("amazon_braket"))
