from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage175_first_provider_preresult_readiness_synthesis import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE160_RESULTS,
    DEFAULT_STAGE163_RESULTS,
    DEFAULT_STAGE170_RESULTS,
    DEFAULT_STAGE171_RESULTS,
    DEFAULT_STAGE172_RESULTS,
    DEFAULT_STAGE173_RESULTS,
    DEFAULT_STAGE174_RESULTS,
    print_stage175_summary,
    run_stage175_preresult_readiness_synthesis,
    write_stage175_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize first-provider pre-result readiness without submitting hardware.")
    parser.add_argument("--stage160-results", type=Path, default=DEFAULT_STAGE160_RESULTS)
    parser.add_argument("--stage163-results", type=Path, default=DEFAULT_STAGE163_RESULTS)
    parser.add_argument("--stage170-results", type=Path, default=DEFAULT_STAGE170_RESULTS)
    parser.add_argument("--stage171-results", type=Path, default=DEFAULT_STAGE171_RESULTS)
    parser.add_argument("--stage172-results", type=Path, default=DEFAULT_STAGE172_RESULTS)
    parser.add_argument("--stage173-results", type=Path, default=DEFAULT_STAGE173_RESULTS)
    parser.add_argument("--stage174-results", type=Path, default=DEFAULT_STAGE174_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage175_preresult_readiness_synthesis(
        stage160_results_path=args.stage160_results,
        stage163_results_path=args.stage163_results,
        stage170_results_path=args.stage170_results,
        stage171_results_path=args.stage171_results,
        stage172_results_path=args.stage172_results,
        stage173_results_path=args.stage173_results,
        stage174_results_path=args.stage174_results,
    )
    paths = write_stage175_outputs(result, args.output_dir)
    print_stage175_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
