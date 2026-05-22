from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage200_reduced_scope_attestation_intake import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE199_RESULTS,
    print_stage200_summary,
    run_stage200_reduced_scope_attestation_intake,
    write_stage200_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake exact reduced-scope credit attestation phrase without submitting hardware.")
    parser.add_argument("--stage199-results", type=Path, default=DEFAULT_STAGE199_RESULTS)
    parser.add_argument("--provided-attestation-phrase", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage200_reduced_scope_attestation_intake(
        stage199_results_path=args.stage199_results,
        provided_attestation_phrase=args.provided_attestation_phrase,
    )
    paths = write_stage200_outputs(result, args.output_dir)
    print_stage200_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
