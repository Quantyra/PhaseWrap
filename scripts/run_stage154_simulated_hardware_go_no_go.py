from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage154_simulated_hardware_go_no_go import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE153_RESULTS,
    print_stage154_summary,
    run_stage154_go_no_go,
    write_stage154_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Interpret simulated-noise results as a hardware go/no-go screen.")
    parser.add_argument("--stage153-results", type=Path, default=DEFAULT_STAGE153_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage154_go_no_go(stage153_results_path=args.stage153_results)
    paths = write_stage154_outputs(result, args.output_dir)
    print_stage154_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
