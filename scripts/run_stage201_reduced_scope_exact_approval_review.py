from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage201_reduced_scope_exact_approval_review import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE200_RESULTS,
    print_stage201_summary,
    run_stage201_reduced_scope_exact_approval_review,
    write_stage201_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review exact reduced-scope live approval phrase without submitting hardware.")
    parser.add_argument("--stage200-results", type=Path, default=DEFAULT_STAGE200_RESULTS)
    parser.add_argument("--provided-approval-phrase", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage201_reduced_scope_exact_approval_review(
        stage200_results_path=args.stage200_results,
        provided_approval_phrase=args.provided_approval_phrase,
    )
    paths = write_stage201_outputs(result, args.output_dir)
    print_stage201_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
