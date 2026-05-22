from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage204_reduced_scope_guarded_runner_readiness import (  # noqa: E402
    DEFAULT_FRESH_STAGE193_RESULTS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE203_RESULTS,
    print_stage204_summary,
    run_stage204_reduced_scope_guarded_runner_readiness,
    write_stage204_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review reduced-scope guarded runner readiness without submitting hardware.")
    parser.add_argument("--stage203-results", type=Path, default=DEFAULT_STAGE203_RESULTS)
    parser.add_argument("--fresh-stage193-results", type=Path, default=DEFAULT_FRESH_STAGE193_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage204_reduced_scope_guarded_runner_readiness(
        stage203_results_path=args.stage203_results,
        fresh_stage193_results_path=args.fresh_stage193_results,
    )
    paths = write_stage204_outputs(result, args.output_dir)
    print_stage204_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
