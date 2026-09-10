from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat as nbf
import pandas as pd

from src.analyze import summarize_deposition_conditions
from src.load_sources import load_project2, load_project3


COLORS = ["#2563EB", "#F97316", "#16A34A"]


def _finish_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()


def select_fixed_recipe_group(conditions: pd.DataFrame) -> pd.DataFrame:
    """Select the comparable 400 W, 400 C, 30 s recipe group."""
    selected = conditions.loc[
        (conditions["power"] == 400)
        & (conditions["temperature"] == 400)
        & (conditions["time_sec"] == 30)
        & ~conditions["recipe"].str.contains("Pre", case=False, na=False)
    ]
    return selected.sort_values(["si2h6_flow", "recipe"]).reset_index(drop=True)


def create_charts(
    sensor_detail: pd.DataFrame,
    conditions: pd.DataFrame,
    wafer: pd.DataFrame,
    images_dir: Path,
) -> None:
    images_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(9, 5))
    for color, (run, group) in zip(COLORS, sensor_detail.groupby("run", sort=True)):
        ax.plot(group["process_time"], group["si2h6_flow"], marker="o", markersize=3, label=run, color=color)
    ax.axhline(sensor_detail["target"].dropna().median(), color="#111827", linestyle="--", linewidth=1.2, label="Target")
    ax.axvspan(sensor_detail["process_time"].min(), 3, color="#CBD5E1", alpha=0.45, label="Ramp-up excluded")
    ax.set(title="Si2H6 flow stability by run", xlabel="Process time (s)", ylabel="Flow (sccm)")
    ax.legend(ncol=2, frameon=True)
    _finish_figure(images_dir / "sensor_stability_by_run.png")

    ordered = conditions.sort_values("si2h6_flow")
    comparable = select_fixed_recipe_group(conditions)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(comparable["si2h6_flow"], comparable["average_thickness"], s=65, color=COLORS[0])
    trend = comparable.groupby("si2h6_flow", as_index=False)["average_thickness"].mean()
    ax.plot(trend["si2h6_flow"], trend["average_thickness"], color=COLORS[0], alpha=0.7)
    ax.set(title="Si2H6 flow and mean film thickness\n400 W, 400 C, 30 s", xlabel="Si2H6 flow (sccm)", ylabel="Mean thickness (a.u.)")
    _finish_figure(images_dir / "gas_flow_vs_thickness.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.errorbar(
        ordered["si2h6_flow"],
        ordered["average_thickness"],
        yerr=ordered["standard_deviation"],
        fmt="o",
        capsize=4,
        color=COLORS[1],
    )
    ax.set(title="Process-condition variation", xlabel="Si2H6 flow (sccm)", ylabel="Mean thickness ± 1 SD (a.u.)")
    _finish_figure(images_dir / "process_condition_variation.png")

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    points = ax.scatter(
        wafer["x_mm"], wafer["y_mm"], c=wafer["thickness"], s=125, cmap="viridis", edgecolor="white", linewidth=0.5
    )
    fig.colorbar(points, ax=ax, label="Thickness (a.u.)")
    ax.set_aspect("equal")
    ax.set(title="Representative wafer thickness map", xlabel="x (mm)", ylabel="y (mm)")
    _finish_figure(images_dir / "wafer_uniformity_map.png")


def create_notebooks(analysis_dir: Path) -> None:
    analysis_dir.mkdir(parents=True, exist_ok=True)

    sensor = nbf.v4.new_notebook()
    sensor.cells = [
        nbf.v4.new_markdown_cell(
            "# Process sensor stability\n\nThis notebook compares three Si2H6 flow runs and excludes the initial ramp-up interval before calculating stability statistics."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\ndata = pd.read_csv('../data/process_sensor_summary.csv')\ndata.head()"
        ),
        nbf.v4.new_code_cell(
            "stable = data.loc[data['stable_interval']].copy()\nsummary = stable.groupby('run')['si2h6_flow'].agg(['count','mean','std'])\nsummary['lower_3sigma'] = summary['mean'] - 3 * summary['std']\nsummary['upper_3sigma'] = summary['mean'] + 3 * summary['std']\nsummary.round(4)"
        ),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(9,5))\nfor run, group in data.groupby('run'):\n    ax.plot(group['process_time'], group['si2h6_flow'], marker='o', markersize=3, label=run)\nax.axhline(data['target'].median(), color='black', linestyle='--', label='Target')\nax.axvspan(data['process_time'].min(), 3, color='lightgray', alpha=.5, label='Ramp-up excluded')\nax.set(title='Si2H6 flow stability by run', xlabel='Process time (s)', ylabel='Flow (sccm)')\nax.legend(ncol=2)\nfig.tight_layout()\nfig.savefig('../images/sensor_stability_by_run.png', dpi=180, bbox_inches='tight')\nplt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## Interpretation\n\nThe first three observations are treated as ramp-up, not steady-state evidence. Stability is assessed from the remaining samples using the sample mean, sample standard deviation, and an empirical mean ± 3σ band. This is a comparative exercise, not a validated production control limit."
        ),
    ]
    nbf.write(sensor, analysis_dir / "01_process_sensor_stability.ipynb")

    deposition = nbf.v4.new_notebook()
    deposition.cells = [
        nbf.v4.new_markdown_cell(
            "# Deposition parameter analysis\n\nThis notebook compares film-thickness statistics as Si2H6 flow changes while the other listed recipe settings remain fixed."
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\nimport matplotlib.pyplot as plt\n\nconditions = pd.read_csv('../data/deposition_condition_summary.csv')\nwafer = pd.read_csv('../data/wafer_uniformity_sample.csv')\nconditions.head()"
        ),
        nbf.v4.new_code_cell(
            "ordered = conditions.sort_values('si2h6_flow')\ncomparable = ordered[(ordered['power'] == 400) & (ordered['temperature'] == 400) & (ordered['time_sec'] == 30) & ~ordered['recipe'].str.contains('Pre')]\ntrend = comparable.groupby('si2h6_flow', as_index=False)['average_thickness'].mean()\nfig, ax = plt.subplots(figsize=(8,5))\nax.scatter(comparable['si2h6_flow'], comparable['average_thickness'], s=65)\nax.plot(trend['si2h6_flow'], trend['average_thickness'], alpha=.7)\nax.set(title='Si2H6 flow and mean film thickness\\n400 W, 400 C, 30 s', xlabel='Si2H6 flow (sccm)', ylabel='Mean thickness (a.u.)')\nfig.tight_layout()\nfig.savefig('../images/gas_flow_vs_thickness.png', dpi=180, bbox_inches='tight')\nplt.show()"
        ),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(9,5))\nax.errorbar(ordered['si2h6_flow'], ordered['average_thickness'], yerr=ordered['standard_deviation'], fmt='o', capsize=4)\nax.set(title='Process-condition variation', xlabel='Si2H6 flow (sccm)', ylabel='Mean thickness ± 1 SD (a.u.)')\nfig.tight_layout()\nfig.savefig('../images/process_condition_variation.png', dpi=180, bbox_inches='tight')\nplt.show()"
        ),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(6.5,5.5))\npoints = ax.scatter(wafer['x_mm'], wafer['y_mm'], c=wafer['thickness'], s=125, cmap='viridis', edgecolor='white', linewidth=.5)\nfig.colorbar(points, ax=ax, label='Thickness (a.u.)')\nax.set_aspect('equal')\nax.set(title='Representative wafer thickness map', xlabel='x (mm)', ylabel='y (mm)')\nfig.tight_layout()\nfig.savefig('../images/wafer_uniformity_map.png', dpi=180, bbox_inches='tight')\nplt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## Interpretation and limits\n\nThe plots show association, not proof of causality. Results come from an educational dataset and should be interpreted as a structured comparison of recipe conditions. Production decisions would require repeat runs, measurement-system checks, and confirmed specification limits."
        ),
    ]
    nbf.write(deposition, analysis_dir / "02_deposition_parameter_analysis.ipynb")


def build(project2_path: Path, project3_path: Path, repository: Path) -> None:
    sensor_detail = load_project2(project2_path)
    sensor_detail["stable_interval"] = sensor_detail["process_time"] > 3
    conditions_source, wafer = load_project3(project3_path)
    conditions = summarize_deposition_conditions(conditions_source)

    data_dir = repository / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    sensor_detail.round(4).to_csv(data_dir / "process_sensor_summary.csv", index=False)
    conditions.round(4).to_csv(data_dir / "deposition_condition_summary.csv", index=False)
    wafer.round(4).to_csv(data_dir / "wafer_uniformity_sample.csv", index=False)
    create_charts(sensor_detail, conditions, wafer, repository / "images")
    create_notebooks(repository / "analysis")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project2", type=Path)
    parser.add_argument("project3", type=Path)
    parser.add_argument("repository", type=Path)
    args = parser.parse_args()
    build(args.project2, args.project3, args.repository)


if __name__ == "__main__":
    main()
