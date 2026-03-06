from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Q-RoPE statistical summary/report")
    parser.add_argument("--input", required=True, help="Input summary_v1 CSV")
    parser.add_argument("--summary-output", required=True, help="Output summary_v2 CSV")
    parser.add_argument("--report-output", required=True, help="Output report_v2 markdown")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    summary_output = Path(args.summary_output)
    report_output = Path(args.report_output)
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.parent.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    supplemental_rows: list[dict[str, str]] = []
    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if _is_canonical_phase1_row(row):
                grouped[(row["variant"], row["dataset"])].append(row)
            else:
                supplemental_rows.append(row)

    rows_out: list[dict[str, str | float | int]] = []
    for (variant, dataset), rows in sorted(grouped.items()):
        accs = [_to_float(r["accuracy"]) for r in rows]
        f1s = [_to_float(r["f1"]) for r in rows]
        rows_out.append(
            {
                "variant": variant,
                "dataset": dataset,
                "runs": len(rows),
                "mean_accuracy": _mean(accs),
                "std_accuracy": _std(accs),
                "ci95_accuracy": _ci95(accs),
                "mean_f1": _mean(f1s),
                "std_f1": _std(f1s),
                "ci95_f1": _ci95(f1s),
                "mean_gate_count_total": _mean([_to_float(r["gate_count_total"]) for r in rows]),
                "mean_circuit_depth": _mean([_to_float(r["circuit_depth"]) for r in rows]),
                "real_run_count": sum(1 for r in rows if _run_mode(r) == "real"),
                "dry_run_count": sum(1 for r in rows if _run_mode(r) == "dry"),
            }
        )

    fieldnames = [
        "variant",
        "dataset",
        "runs",
        "mean_accuracy",
        "std_accuracy",
        "ci95_accuracy",
        "mean_f1",
        "std_f1",
        "ci95_f1",
        "mean_gate_count_total",
        "mean_circuit_depth",
        "real_run_count",
        "dry_run_count",
    ]
    with summary_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    by_dataset: dict[str, dict[str, dict[str, str | float | int]]] = defaultdict(dict)
    for row in rows_out:
        by_dataset[str(row["dataset"])][str(row["variant"])] = row

    lines = [
        "# Q-RoPE Statistical Report v2",
        "",
        "## Dataset Summary",
        "",
        "Canonical phase-1 matrix (`backend=sim_local`) only.",
        "",
        "| Dataset | Variant | Runs | Mean Acc | Acc CI95 | Mean F1 | F1 CI95 | Mean Gates | Mean Depth |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dataset, variants in sorted(by_dataset.items()):
        for variant, row in sorted(variants.items()):
            lines.append(
                f"| {dataset} | {variant} | {row['runs']} | {float(row['mean_accuracy']):.4f} | {float(row['ci95_accuracy']):.4f} | {float(row['mean_f1']):.4f} | {float(row['ci95_f1']):.4f} | {float(row['mean_gate_count_total']):.1f} | {float(row['mean_circuit_depth']):.1f} |"
            )

    lines.extend(
        [
            "",
            "## V3 Comparison",
            "",
            "| Dataset | Comparator | Delta Acc (V3 - comp) | Delta F1 (V3 - comp) |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for dataset, variants in sorted(by_dataset.items()):
        if "V3" not in variants:
            continue
        base = variants["V3"]
        for comparator in ("V2", "V1", "V0"):
            if comparator not in variants:
                continue
            comp = variants[comparator]
            lines.append(
                f"| {dataset} | {comparator} | {float(base['mean_accuracy']) - float(comp['mean_accuracy']):.4f} | {float(base['mean_f1']) - float(comp['mean_f1']):.4f} |"
            )

    lines.extend(
        [
            "",
            "## Quantitative Gaps",
            "",
            "- Confidence intervals are based on small run counts and should be treated as provisional.",
            "- Local handcrafted datasets remain the main external-validity limitation.",
            "- Supplemental hardware/cloud-style backend rows are tracked separately and are not folded into the canonical baseline table above.",
        ]
    )

    if supplemental_rows:
        lines.extend(
            [
                "",
                "## Supplemental Backend Rows",
                "",
                "| Run ID | Backend | Variant | Dataset | Accuracy | F1 | Notes |",
                "| --- | --- | --- | --- | ---: | ---: | --- |",
            ]
        )
        for row in sorted(supplemental_rows, key=lambda item: item["run_id"]):
            lines.append(
                f"| {row['run_id']} | {row['backend']} | {row['variant']} | {row['dataset']} | {_to_float(row['accuracy']):.4f} | {_to_float(row['f1']):.4f} | {row.get('data_mode', 'n/a')} |"
            )

    report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote statistical summary: {summary_output}")
    print(f"Wrote statistical report: {report_output}")


def _to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean = _mean(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1))


def _ci95(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    return 1.96 * (_std(values) / math.sqrt(n))


def _run_mode(row: dict[str, str]) -> str:
    mode = row.get("run_mode")
    if mode:
        return mode
    dry_flag = row.get("dry_run", "").strip().lower()
    if dry_flag == "true":
        return "dry"
    if dry_flag == "false":
        return "real"
    return "unknown"


def _is_canonical_phase1_row(row: dict[str, str]) -> bool:
    run_id = row.get("run_id", "")
    backend = row.get("backend", "")
    supplemental_markers = ("-local-", "-real-", "-qsim-", "-aer-", "-quandela-")
    return backend == "sim_local" and not any(marker in run_id for marker in supplemental_markers)


if __name__ == "__main__":
    main()
