import pandas as pd


def summarize_sensor_runs(data: pd.DataFrame, ramp_up_rows: int = 3) -> pd.DataFrame:
    """Summarize each run after excluding its initial ramp-up samples."""
    rows = []
    for run, group in data.sort_values(["run", "process_time"]).groupby("run", sort=True):
        stable = group.iloc[ramp_up_rows:]
        if stable.empty:
            raise ValueError(f"run {run} has no samples after ramp-up exclusion")
        mean = stable["si2h6_flow"].mean()
        std = stable["si2h6_flow"].std(ddof=1)
        rows.append(
            {
                "run": run,
                "sample_count": len(stable),
                "mean_flow": mean,
                "standard_deviation": std,
                "lower_3sigma": mean - 3 * std,
                "upper_3sigma": mean + 3 * std,
                "target": stable["target"].dropna().median(),
            }
        )
    return pd.DataFrame(rows)


def summarize_deposition_conditions(
    parameters: pd.DataFrame, measurements: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Return condition statistics from raw measurements or source summaries."""
    keys = ["recipe", "si2h6_flow", "power", "temperature", "time_sec"]
    stats = ["average_thickness", "min_thickness", "max_thickness", "range", "standard_deviation"]
    if measurements is None:
        return parameters[keys + stats].copy().sort_values("si2h6_flow").reset_index(drop=True)

    grouped = measurements.groupby("recipe")["thickness"].agg(
        average_thickness="mean",
        min_thickness="min",
        max_thickness="max",
        standard_deviation="std",
    )
    grouped["range"] = grouped["max_thickness"] - grouped["min_thickness"]
    result = parameters[keys].merge(grouped.reset_index(), on="recipe", how="inner")
    return result[keys + stats].sort_values("si2h6_flow").reset_index(drop=True)
