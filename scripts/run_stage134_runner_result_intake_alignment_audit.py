from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage134_runner_result_intake_alignment_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE115_RESULTS,
    DEFAULT_STAGE133_RESULTS,
    print_stage134_summary,
    run_stage134_audit,
    write_stage134_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Stage 133 runner outputs against Stage 115 intake shards.")
    parser.add_argument("--stage115-results", type=Path, default=DEFAULT_STAGE115_RESULTS)
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage134_audit(stage115_results_path=args.stage115_results, stage133_results_path=args.stage133_results)
    paths = write_stage134_outputs(result, args.output_dir)
    print_stage134_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
