from pathlib import Path

from qrope.report import main as report_main


def test_report_includes_run_mode_counts(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "summary.csv"
    csv_path.write_text(
        "\n".join(
            [
                "run_id,variant,dataset,seed,backend,accuracy,f1,train_loss_final,eval_loss,qubit_count,gate_count_total,circuit_depth,shot_count,noise_model,wall_time_sec,timestamp_utc,dry_run,run_mode,data_mode",
                "r1,V0,yelp,42,sim_local,0.1,0.2,1.0,1.1,8,100,10,2048,none,0.1,2026-03-06T00:00:00Z,True,dry,local_jsonl",
                "r2,V3,yelp,42,sim_local,0.8,0.7,0.9,1.0,8,120,14,2048,none,0.2,2026-03-06T00:00:01Z,False,real,local_jsonl",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.md"

    monkeypatch.setattr(
        "sys.argv",
        ["report", "--input", str(csv_path), "--output", str(report_path)],
    )
    report_main()

    text = report_path.read_text(encoding="utf-8")
    assert "## Run Mode Counts" in text
    assert "| real | 1 |" in text
    assert "| dry | 1 |" in text
    assert "Canonical phase-1 matrix (`backend=sim_local`) only." in text
