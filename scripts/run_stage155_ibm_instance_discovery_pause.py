from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage155_ibm_instance_discovery_pause import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE140_RESULTS,
    DEFAULT_STAGE154_RESULTS,
    print_stage155_summary,
    run_stage155_ibm_instance_discovery_pause,
    write_stage155_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pause after simulated GO and check IBM instance discovery.")
    parser.add_argument("--stage154-results", type=Path, default=DEFAULT_STAGE154_RESULTS)
    parser.add_argument("--stage140-results", type=Path, default=DEFAULT_STAGE140_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--allow-live-discovery", action="store_true")
    args = parser.parse_args(argv)

    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage155_ibm_instance_discovery_pause(
        stage154_results_path=args.stage154_results,
        stage140_results_path=args.stage140_results,
        allow_live_discovery=args.allow_live_discovery,
    )
    paths = write_stage155_outputs(result, args.output_dir)
    print_stage155_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
