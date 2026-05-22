from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage172_objective_evidence_gap_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE103_RESULTS,
    DEFAULT_STAGE137_RESULTS,
    DEFAULT_STAGE138_RESULTS,
    DEFAULT_STAGE148_RESULTS,
    DEFAULT_STAGE170_RESULTS,
    DEFAULT_STAGE171_RESULTS,
    print_stage172_summary,
    run_stage172_objective_evidence_gap_audit,
    write_stage172_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit remaining evidence gaps for the noisy-hardware objective.")
    parser.add_argument("--stage103-results", type=Path, default=DEFAULT_STAGE103_RESULTS)
    parser.add_argument("--stage137-results", type=Path, default=DEFAULT_STAGE137_RESULTS)
    parser.add_argument("--stage138-results", type=Path, default=DEFAULT_STAGE138_RESULTS)
    parser.add_argument("--stage148-results", type=Path, default=DEFAULT_STAGE148_RESULTS)
    parser.add_argument("--stage170-results", type=Path, default=DEFAULT_STAGE170_RESULTS)
    parser.add_argument("--stage171-results", type=Path, default=DEFAULT_STAGE171_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage172_objective_evidence_gap_audit(
        stage103_results_path=args.stage103_results,
        stage137_results_path=args.stage137_results,
        stage138_results_path=args.stage138_results,
        stage148_results_path=args.stage148_results,
        stage170_results_path=args.stage170_results,
        stage171_results_path=args.stage171_results,
    )
    paths = write_stage172_outputs(result, args.output_dir)
    print_stage172_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
