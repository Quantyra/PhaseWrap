from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage139_provider_action_readiness_checklist import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE130_RESULTS,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE138_RESULTS,
    print_stage139_summary,
    run_stage139_checklist,
    write_stage139_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a provider action checklist before live runner execution.")
    parser.add_argument("--stage130-results", type=Path, default=DEFAULT_STAGE130_RESULTS)
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage138-results", type=Path, default=DEFAULT_STAGE138_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage139_checklist(
        stage130_results_path=args.stage130_results,
        stage133_results_path=args.stage133_results,
        stage138_results_path=args.stage138_results,
    )
    paths = write_stage139_outputs(result, args.output_dir)
    print_stage139_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
