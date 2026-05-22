from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage104_matched_packet_execution_package import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE101_RESULTS,
    DEFAULT_STAGE103_MANIFEST,
    DEFAULT_STAGE99_MANIFEST,
    print_stage104_summary,
    run_stage104_package,
    write_stage104_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare Stage 104 matched packet execution templates.")
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--stage101-results", type=Path, default=DEFAULT_STAGE101_RESULTS)
    parser.add_argument("--stage103-manifest", type=Path, default=DEFAULT_STAGE103_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage104_package(
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
        stage101_results_path=args.stage101_results,
        stage103_manifest_path=args.stage103_manifest,
    )
    paths = write_stage104_outputs(result, args.output_dir)
    print_stage104_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote templates under {paths['template_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
