from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage173_locked_result_ingestion_contract_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE114_MANIFEST,
    DEFAULT_STAGE114_SCHEMA,
    DEFAULT_STAGE163_RESULTS,
    DEFAULT_STAGE172_RESULTS,
    print_stage173_summary,
    run_stage173_locked_ingestion_audit,
    write_stage173_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit locked result-ingestion contract readiness before provider results exist.")
    parser.add_argument("--stage114-manifest", type=Path, default=DEFAULT_STAGE114_MANIFEST)
    parser.add_argument("--stage114-schema", type=Path, default=DEFAULT_STAGE114_SCHEMA)
    parser.add_argument("--stage163-results", type=Path, default=DEFAULT_STAGE163_RESULTS)
    parser.add_argument("--stage172-results", type=Path, default=DEFAULT_STAGE172_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage173_locked_ingestion_audit(
        stage114_manifest_path=args.stage114_manifest,
        stage114_schema_path=args.stage114_schema,
        stage163_results_path=args.stage163_results,
        stage172_results_path=args.stage172_results,
    )
    paths = write_stage173_outputs(result, args.output_dir)
    print_stage173_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
