from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build markdown report from aggregated metrics")
    parser.add_argument("--input", required=True, help="Input summary CSV")
    parser.add_argument("--output", required=True, help="Output markdown path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    supplemental_rows: list[dict[str, str]] = []
    mode_counts: dict[str, int] = defaultdict(int)
    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if _is_canonical_phase1_row(row):
                grouped[(row["variant"], row["dataset"])].append(row)
            else:
                supplemental_rows.append(row)
            mode = row.get("run_mode")
            if not mode:
                dry_flag = row.get("dry_run", "").strip().lower()
                if dry_flag == "true":
                    mode = "dry"
                elif dry_flag == "false":
                    mode = "real"
                else:
                    mode = "unknown"
            mode_counts[mode] += 1

    lines: list[str] = [
        "# Q-RoPE Ablation Report",
        "",
        "## Summary Table",
        "",
        "Canonical phase-1 matrix (`backend=sim_local`) only.",
        "",
        "| Variant | Dataset | Runs | Mean Accuracy | Mean F1 |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for (variant, dataset), rows in sorted(grouped.items()):
        runs = len(rows)
        mean_acc = _mean([_to_float(r["accuracy"]) for r in rows])
        mean_f1 = _mean([_to_float(r["f1"]) for r in rows])
        lines.append(f"| {variant} | {dataset} | {runs} | {mean_acc:.4f} | {mean_f1:.4f} |")

    lines.extend(
        [
            "",
            "## Run Mode Counts",
            "",
            "| Run Mode | Count |",
            "| --- | ---: |",
            f"| real | {mode_counts.get('real', 0)} |",
            f"| dry | {mode_counts.get('dry', 0)} |",
        ]
    )

    if supplemental_rows:
        lines.extend(
            [
                "",
                "## Supplemental Backend Runs",
                "",
                "| Run ID | Variant | Dataset | Backend | Accuracy | F1 | Data Mode |",
                "| --- | --- | --- | --- | ---: | ---: | --- |",
            ]
        )
        for row in sorted(supplemental_rows, key=lambda item: item["run_id"]):
            lines.append(
                f"| {row['run_id']} | {row['variant']} | {row['dataset']} | {row['backend']} | {_to_float(row['accuracy']):.4f} | {_to_float(row['f1']):.4f} | {row.get('data_mode', 'n/a')} |"
            )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote report: {output_path}")


def _to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _is_canonical_phase1_row(row: dict[str, str]) -> bool:
    run_id = row.get("run_id", "")
    backend = row.get("backend", "")
    supplemental_markers = ("-local-", "-real-", "-qsim-", "-aer-", "-quandela-")
    return backend == "sim_local" and not any(marker in run_id for marker in supplemental_markers)


if __name__ == "__main__":
    main()
