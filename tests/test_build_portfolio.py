from pathlib import Path

import pandas as pd

from src.build_portfolio import create_charts, create_notebooks, select_fixed_recipe_group


def test_fixed_recipe_group_excludes_other_settings_and_pre_runs():
    conditions = pd.DataFrame(
        {
            "recipe": ["Pre", "R1", "R2", "R3"],
            "si2h6_flow": [200, 200, 205, 210],
            "power": [400, 400, 400, 300],
            "temperature": [400, 400, 400, 400],
            "time_sec": [30, 30, 30, 30],
        }
    )

    result = select_fixed_recipe_group(conditions)

    assert result["recipe"].tolist() == ["R1", "R2"]


def test_create_charts_writes_four_nonempty_pngs(tmp_path: Path):
    sensor_detail = pd.DataFrame(
        {
            "run": ["Run1"] * 4 + ["Run2"] * 4,
            "process_time": [1, 2, 3, 4] * 2,
            "si2h6_flow": [20, 90, 100, 101, 10, 80, 99, 100],
            "target": [100] * 8,
        }
    )
    conditions = pd.DataFrame(
        {
            "recipe": ["R1", "R2"],
            "si2h6_flow": [200, 205],
            "power": [400, 400],
            "temperature": [400, 400],
            "time_sec": [30, 30],
            "average_thickness": [100, 105],
            "min_thickness": [90, 95],
            "max_thickness": [110, 115],
            "range": [20, 20],
            "standard_deviation": [5, 6],
        }
    )
    wafer = pd.DataFrame(
        {"point": [1, 2, 3], "x_mm": [0, 50, -50], "y_mm": [0, 0, 0], "thickness": [100, 105, 95]}
    )

    create_charts(sensor_detail, conditions, wafer, tmp_path)

    expected = {
        "sensor_stability_by_run.png",
        "gas_flow_vs_thickness.png",
        "process_condition_variation.png",
        "wafer_uniformity_map.png",
    }
    assert {p.name for p in tmp_path.glob("*.png")} == expected
    assert all((tmp_path / name).stat().st_size > 10_000 for name in expected)


def test_create_notebooks_uses_only_repository_relative_inputs(tmp_path: Path):
    analysis_dir = tmp_path / "analysis"
    create_notebooks(analysis_dir)

    notebooks = sorted(analysis_dir.glob("*.ipynb"))
    assert [p.name for p in notebooks] == [
        "01_process_sensor_stability.ipynb",
        "02_deposition_parameter_analysis.ipynb",
    ]
    text = "\n".join(p.read_text(encoding="utf-8") for p in notebooks)
    assert "../data/" in text
    assert "C:\\\\Users" not in text
    assert "jwy" + "oo" not in text.lower()
