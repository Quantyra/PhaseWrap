from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage161_first_provider_exposure_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE114_OUTPUT_DIR,
    DEFAULT_STAGE157_RESULTS,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE160_RESULTS,
    print_stage161_summary,
    run_stage161_exposure_packet,
    write_stage161_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize no-submit first-provider IBM job and shot exposure.")
    parser.add_argument("--stage157-results", type=Path, default=DEFAULT_STAGE157_RESULTS)
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage160-results", type=Path, default=DEFAULT_STAGE160_RESULTS)
    parser.add_argument("--stage114-output-dir", type=Path, default=DEFAULT_STAGE114_OUTPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage161_exposure_packet(
        stage157_results_path=args.stage157_results,
        stage159_results_path=args.stage159_results,
        stage160_results_path=args.stage160_results,
        stage114_output_dir=args.stage114_output_dir,
    )
    paths = write_stage161_outputs(result, args.output_dir)
    print_stage161_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
