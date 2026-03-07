from qrope.synthetic import generate_signed_offset_binary_bundle


def test_signed_offset_bundle_is_deterministic() -> None:
    bundle_a = generate_signed_offset_binary_bundle(seed=42)
    bundle_b = generate_signed_offset_binary_bundle(seed=42)
    assert bundle_a.train == bundle_b.train
    assert bundle_a.validation == bundle_b.validation
    assert bundle_a.test == bundle_b.test
    assert bundle_a.diagnostics == bundle_b.diagnostics


def test_signed_offset_bundle_has_expected_sizes() -> None:
    bundle = generate_signed_offset_binary_bundle(seed=42)
    assert len(bundle.train) == 256
    assert len(bundle.validation) == 128
    assert len(bundle.test) == 128


def test_signed_offset_bundle_is_balanced() -> None:
    bundle = generate_signed_offset_binary_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["class_balance_ok"] is True
        assert summary["offset_abs_balance_ok"] is True
        assert summary["token_pair_balance_ok"] is True


def test_signed_offset_labels_match_rendered_offsets() -> None:
    bundle = generate_signed_offset_binary_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    for text, label in rows:
        offset = int(text.split("off:", 1)[1])
        assert label == (1 if offset > 0 else 0)
