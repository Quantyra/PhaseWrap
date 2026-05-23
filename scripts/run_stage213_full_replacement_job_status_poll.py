from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage213_full_replacement_job_status_poll import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE212_RESULTS,
    print_stage213_summary,
    run_stage213_full_replacement_job_status_poll,
    write_stage213_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Poll submitted full replacement IBM Runtime job statuses.")
    parser.add_argument("--stage212-results", type=Path, default=DEFAULT_STAGE212_RESULTS)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage213_full_replacement_job_status_poll(stage212_results_path=args.stage212_results, load_dotenv=args.load_dotenv)
    paths = write_stage213_outputs(result, args.output_dir)
    print_stage213_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
