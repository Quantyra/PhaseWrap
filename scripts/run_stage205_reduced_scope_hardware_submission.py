from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage205_reduced_scope_hardware_submission import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE203_RESULTS,
    DEFAULT_STAGE204_RESULTS,
    print_stage205_summary,
    run_stage205_reduced_scope_hardware_submission,
    write_stage205_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Submit reduced-scope IBM Runtime templates after all approval/readiness gates.")
    parser.add_argument("--stage204-results", type=Path, default=DEFAULT_STAGE204_RESULTS)
    parser.add_argument("--stage203-results", type=Path, default=DEFAULT_STAGE203_RESULTS)
    parser.add_argument("--allow-live-submit", action="store_true")
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage205_reduced_scope_hardware_submission(
        stage204_results_path=args.stage204_results,
        stage203_results_path=args.stage203_results,
        allow_live_submit=args.allow_live_submit,
        load_dotenv=args.load_dotenv,
    )
    paths = write_stage205_outputs(result, args.output_dir)
    print_stage205_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
