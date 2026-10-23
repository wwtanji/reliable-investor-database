import pytest

from investor_db.metrics import format_proportion, proportion, wilson_interval


def test_wilson_interval_matches_reference_values() -> None:
    low, high = wilson_interval(28, 30)
    assert low == pytest.approx(0.7868, abs=1e-3)
    assert high == pytest.approx(0.9815, abs=1e-3)


def test_wilson_interval_is_bounded_at_extremes() -> None:
    low, high = wilson_interval(30, 30)
    assert high == pytest.approx(1.0)
    assert low == pytest.approx(0.8865, abs=1e-3)
    low, _ = wilson_interval(0, 10)
    assert low == 0.0


def test_wilson_interval_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        wilson_interval(1, 0)
    with pytest.raises(ValueError):
        wilson_interval(5, 4)


def test_proportion_handles_empty_and_formats() -> None:
    assert proportion(0, 0).value is None
    assert format_proportion(proportion(0, 0)) == "n/a (0 checked)"
    assert format_proportion(proportion(28, 30)) == "93.3% (28/30, 95% CI 78.7%-98.2%)"
