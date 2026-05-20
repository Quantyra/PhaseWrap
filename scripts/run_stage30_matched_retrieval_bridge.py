from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage30_matched_retrieval_bridge import print_stage30_table, run_stage30_benchmark, write_stage30_outputs  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 30 matched feature-budget retrieval bridge benchmark.")
    parser.add_argument("--preflight", action="store_true", help="Run a tiny deterministic smoke benchmark.")
    args = parser.parse_args()

    if args.preflight:
        result = run_stage30_benchmark(
            data_seeds=(401,),
            model_seeds=(3001,),
            context_lengths=(128, 256, 512, 1024),
            examples_per_task_length=1,
            epochs=3,
            method_names=("rope_relative", "phasewrap_distance_adapter"),
        )
    else:
        result = run_stage30_benchmark()
    write_stage30_outputs(result)
    print_stage30_table(result)


if __name__ == "__main__":
    main()
