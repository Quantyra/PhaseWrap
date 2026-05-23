from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage214_full_replacement_result_collector import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE190_RESULTS,
    DEFAULT_STAGE212_RESULTS,
    print_stage214_summary,
    run_stage214_full_replacement_result_collector,
    write_stage214_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect counts for completed full replacement IBM Runtime jobs.")
    parser.add_argument("--stage212-results", type=Path, default=DEFAULT_STAGE212_RESULTS)
    parser.add_argument("--stage190-results", type=Path, default=DEFAULT_STAGE190_RESULTS)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage214_full_replacement_result_collector(
        stage212_results_path=args.stage212_results,
        stage190_results_path=args.stage190_results,
        load_dotenv=args.load_dotenv,
    )
    paths = write_stage214_outputs(result, args.output_dir)
    print_stage214_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
