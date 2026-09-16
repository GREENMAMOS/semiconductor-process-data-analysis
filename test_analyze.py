import pandas as pd
import pytest

from src.analyze import summarize_deposition_conditions, summarize_sensor_runs


def test_sensor_summary_excludes_ramp_up_and_uses_sample_std():
    data = pd.DataFrame(
        {
            "run": ["Run1"] * 5,
            "process_time": [1, 2, 3, 4, 5],
            "si2h6_flow": [10.0, 20.0, 100.0, 102.0, 104.0],
            "target": [100.0] * 5,
        }
    )

    result = summarize_sensor_runs(data, ramp_up_rows=2).iloc[0]

    assert result["sample_count"] == 3
    assert result["mean_flow"] == pytest.approx(102.0)
    assert result["standard_deviation"] == pytest.approx(2.0)
    assert result["lower_3sigma"] == pytest.approx(96.0)
    assert result["upper_3sigma"] == pytest.approx(108.0)


def test_deposition_summary_calculates_condition_statistics():
    parameters = pd.DataFrame(
        {
            "recipe": ["R1", "R2"],
            "si2h6_flow": [200, 205],
            "power": [400, 400],
            "temperature": [400, 400],
            "time_sec": [30, 30],
        }
    )
    measurements = pd.DataFrame(
        {
            "recipe": ["R1", "R1", "R1", "R2", "R2"],
            "thickness": [90.0, 100.0, 110.0, 100.0, 104.0],
        }
    )

    result = summarize_deposition_conditions(parameters, measurements)

    r1 = result.loc[result["recipe"] == "R1"].iloc[0]
    assert r1["average_thickness"] == pytest.approx(100.0)
    assert r1["min_thickness"] == pytest.approx(90.0)
    assert r1["max_thickness"] == pytest.approx(110.0)
    assert r1["range"] == pytest.approx(20.0)
    assert r1["standard_deviation"] == pytest.approx(10.0)


def test_deposition_summary_preserves_precalculated_source_statistics():
    parameters = pd.DataFrame(
        {
            "recipe": ["R1"],
            "si2h6_flow": [200],
            "power": [400],
            "temperature": [400],
            "time_sec": [30],
            "average_thickness": [101.25],
            "min_thickness": [95.0],
            "max_thickness": [108.0],
            "range": [13.0],
            "standard_deviation": [3.5],
        }
    )

    result = summarize_deposition_conditions(parameters)

    assert result.iloc[0]["average_thickness"] == pytest.approx(101.25)
    assert result.iloc[0]["standard_deviation"] == pytest.approx(3.5)
