from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage120_live_runner_orchestration_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE116_RESULTS,
    DEFAULT_STAGE118_RESULTS,
    DEFAULT_STAGE119_RESULTS,
    print_stage120_summary,
    run_stage120_audit,
    write_stage120_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit guarded live runner orchestration before provider adapter implementation.")
    parser.add_argument("--stage116-results", type=Path, default=DEFAULT_STAGE116_RESULTS)
    parser.add_argument("--stage118-results", type=Path, default=DEFAULT_STAGE118_RESULTS)
    parser.add_argument("--stage119-results", type=Path, default=DEFAULT_STAGE119_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage120_audit(
        stage116_results_path=args.stage116_results,
        stage118_results_path=args.stage118_results,
        stage119_results_path=args.stage119_results,
    )
    paths = write_stage120_outputs(result, args.output_dir)
    print_stage120_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
