from qrope.qsim import build_branch_state, explicit_interference_score, parity_readout


def test_branch_state_symmetry_for_identical_inputs() -> None:
    state_a = build_branch_state(token="A", position=4, seed=42)
    state_b = build_branch_state(token="A", position=4, seed=42)
    assert (state_a == state_b).all()


def test_parity_readout_of_branch_state_is_bounded() -> None:
    state = build_branch_state(token="B", position=2, seed=42)
    score = parity_readout(state, n_qubits=3)
    assert 0.0 <= score <= 1.0


def test_explicit_interference_score_changes_with_offset() -> None:
    score_pos = explicit_interference_score("lt:A rt:C lp:2 rp:5 off:+3", seed=42)
    score_neg = explicit_interference_score("lt:A rt:C lp:5 rp:2 off:-3", seed=42)
    assert score_pos != score_neg
