from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage148_first_provider_statistical_interpretation_gate import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE107_WINDOW_PLANS,
    DEFAULT_STAGE146_RESULTS,
    DEFAULT_STAGE147_RESULTS,
    print_stage148_summary,
    run_stage148_gate,
    write_stage148_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate first-provider statistical interpretation before claim wording.")
    parser.add_argument("--stage107-window-plans", type=Path, default=DEFAULT_STAGE107_WINDOW_PLANS)
    parser.add_argument("--stage146-results", type=Path, default=DEFAULT_STAGE146_RESULTS)
    parser.add_argument("--stage147-results", type=Path, default=DEFAULT_STAGE147_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage148_gate(
        stage107_window_plans_path=args.stage107_window_plans,
        stage146_results_path=args.stage146_results,
        stage147_results_path=args.stage147_results,
    )
    paths = write_stage148_outputs(result, args.output_dir)
    print_stage148_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
