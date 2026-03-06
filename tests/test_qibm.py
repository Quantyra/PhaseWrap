from qrope.qibm import derive_ibm_angles


def test_ibm_angles_are_deterministic_and_positive() -> None:
    feature_angle, phase_angle = derive_ibm_angles("good food and quick service", variant="V3", seed=42)
    assert 0.0 <= feature_angle <= 3.141592653589793
    assert phase_angle > 0.0

    feature_angle_2, phase_angle_2 = derive_ibm_angles("good food and quick service", variant="V3", seed=42)
    assert (feature_angle, phase_angle) == (feature_angle_2, phase_angle_2)
