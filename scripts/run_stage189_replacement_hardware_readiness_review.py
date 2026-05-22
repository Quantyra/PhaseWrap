from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage189_replacement_hardware_readiness_review import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE176_RESULTS,
    DEFAULT_STAGE188_RESULTS,
    print_stage189_summary,
    run_stage189_replacement_hardware_readiness_review,
    write_stage189_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review replacement-semantics hardware readiness after Stage188.")
    parser.add_argument("--stage188-results", type=Path, default=DEFAULT_STAGE188_RESULTS)
    parser.add_argument("--stage176-results", type=Path, default=DEFAULT_STAGE176_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage189_replacement_hardware_readiness_review(
        stage188_results_path=args.stage188_results,
        stage176_results_path=args.stage176_results,
    )
    paths = write_stage189_outputs(result, args.output_dir)
    print_stage189_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
