from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage194_replacement_credit_allowance_decision_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE191_RESULTS,
    DEFAULT_STAGE193_RESULTS,
    print_stage194_summary,
    run_stage194_replacement_credit_allowance_decision_packet,
    write_stage194_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build no-submit replacement-run IBM credit allowance decision packet.")
    parser.add_argument("--stage191-results", type=Path, default=DEFAULT_STAGE191_RESULTS)
    parser.add_argument("--stage193-results", type=Path, default=DEFAULT_STAGE193_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--human-credit-allowance-verified", action="store_true")
    args = parser.parse_args(argv)
    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage194_replacement_credit_allowance_decision_packet(
        stage191_results_path=args.stage191_results,
        stage193_results_path=args.stage193_results,
        human_credit_allowance_verified=args.human_credit_allowance_verified,
    )
    paths = write_stage194_outputs(result, args.output_dir)
    print_stage194_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
