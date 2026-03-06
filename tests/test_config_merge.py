from qrope.config_utils import apply_set, deep_merge


def test_deep_merge_and_set() -> None:
    base = {"run": {"seed": 42}, "model": {"quantum": {"qubits": 8}}}
    override = {"run": {"epochs": 10}, "model": {"quantum": {"shots": 1024}}}

    merged = deep_merge(base, override)
    apply_set(merged, "run.id", "test-run")

    assert merged["run"]["seed"] == 42
    assert merged["run"]["epochs"] == 10
    assert merged["model"]["quantum"]["qubits"] == 8
    assert merged["model"]["quantum"]["shots"] == 1024
    assert merged["run"]["id"] == "test-run"
