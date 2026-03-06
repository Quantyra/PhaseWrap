from pathlib import Path

from qrope.stats_report import main as stats_main


def test_stats_report_generates_outputs(tmp_path: Path, monkeypatch) -> None:
    input_csv = tmp_path / "summary_v1.csv"
    input_csv.write_text(
        "\n".join(
            [
                "run_id,variant,dataset,seed,backend,accuracy,f1,train_loss_final,eval_loss,qubit_count,gate_count_total,circuit_depth,shot_count,noise_model,wall_time_sec,timestamp_utc,dry_run,run_mode,data_mode",
                "r1,V0,yelp,42,sim_local,0.2,0.1,1,1,8,100,10,2048,none,0.1,2026-03-06T00:00:00Z,False,real,local_jsonl",
                "r2,V0,yelp,123,sim_local,0.4,0.3,1,1,8,100,10,2048,none,0.1,2026-03-06T00:00:01Z,False,real,local_jsonl",
                "r3,V3,yelp,42,sim_local,0.7,0.6,1,1,8,120,14,2048,none,0.1,2026-03-06T00:00:02Z,False,real,local_jsonl",
                "r4,V3,yelp,123,sim_local,0.9,0.8,1,1,8,120,14,2048,none,0.1,2026-03-06T00:00:03Z,False,real,local_jsonl",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    summary_v2 = tmp_path / "summary_v2.csv"
    report_v2 = tmp_path / "report_v2.md"

    monkeypatch.setattr(
        "sys.argv",
        [
            "stats_report",
            "--input",
            str(input_csv),
            "--summary-output",
            str(summary_v2),
            "--report-output",
            str(report_v2),
        ],
    )
    stats_main()

    report_text = report_v2.read_text(encoding="utf-8")
    assert "## V3 Comparison" in report_text
    assert "| yelp | V0 |" in report_text
    assert "Canonical phase-1 matrix (`backend=sim_local`) only." in report_text
    assert summary_v2.exists()
