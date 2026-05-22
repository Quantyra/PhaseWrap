from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage144_post_configuration_rerun_chain_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE106_RESULTS,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE128_RESULTS,
    DEFAULT_STAGE129_RESULTS,
    DEFAULT_STAGE130_RESULTS,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE138_RESULTS,
    DEFAULT_STAGE139_RESULTS,
    DEFAULT_STAGE140_RESULTS,
    DEFAULT_STAGE141_RESULTS,
    DEFAULT_STAGE142_RESULTS,
    DEFAULT_STAGE143_RESULTS,
    print_stage144_summary,
    run_stage144_audit,
    write_stage144_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the first-provider post-configuration rerun chain.")
    parser.add_argument("--stage106-results", type=Path, default=DEFAULT_STAGE106_RESULTS)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage128-results", type=Path, default=DEFAULT_STAGE128_RESULTS)
    parser.add_argument("--stage129-results", type=Path, default=DEFAULT_STAGE129_RESULTS)
    parser.add_argument("--stage130-results", type=Path, default=DEFAULT_STAGE130_RESULTS)
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage138-results", type=Path, default=DEFAULT_STAGE138_RESULTS)
    parser.add_argument("--stage139-results", type=Path, default=DEFAULT_STAGE139_RESULTS)
    parser.add_argument("--stage140-results", type=Path, default=DEFAULT_STAGE140_RESULTS)
    parser.add_argument("--stage141-results", type=Path, default=DEFAULT_STAGE141_RESULTS)
    parser.add_argument("--stage142-results", type=Path, default=DEFAULT_STAGE142_RESULTS)
    parser.add_argument("--stage143-results", type=Path, default=DEFAULT_STAGE143_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage144_audit(
        stage106_results_path=args.stage106_results,
        stage111_results_path=args.stage111_results,
        stage128_results_path=args.stage128_results,
        stage129_results_path=args.stage129_results,
        stage130_results_path=args.stage130_results,
        stage133_results_path=args.stage133_results,
        stage138_results_path=args.stage138_results,
        stage139_results_path=args.stage139_results,
        stage140_results_path=args.stage140_results,
        stage141_results_path=args.stage141_results,
        stage142_results_path=args.stage142_results,
        stage143_results_path=args.stage143_results,
    )
    paths = write_stage144_outputs(result, args.output_dir)
    print_stage144_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
