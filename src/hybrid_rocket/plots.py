"""Plotting utilities for validation results."""

from __future__ import annotations

import os
from pathlib import Path

from hybrid_rocket.constants import DEFAULT_EXPERIMENT, DEFAULT_REGRESSION_LAW, MM_TO_M, STANDARD_GRAVITY_M_S2
from hybrid_rocket.models import ExperimentRecord
from hybrid_rocket.validation import baseline_regression_rate_law, load_experimental_data, predict_performance


def _import_pyplot():
    output_config_dir = Path("outputs/.mplconfig").resolve()
    output_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(output_config_dir))
    import matplotlib.pyplot as plt

    return plt


def _save_single_point_plot(
    experimental: list[float],
    predicted: list[float],
    ylabel: str,
    title: str,
    output_path: Path,
) -> None:
    plt = _import_pyplot()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(experimental, predicted, color="#1f77b4", s=80)
    lower = min(experimental + predicted) * 0.95
    upper = max(experimental + predicted) * 1.05
    ax.plot([lower, upper], [lower, upper], linestyle="--", color="black", linewidth=1.0)
    ax.set_xlabel(f"Experimental {ylabel}")
    ax.set_ylabel(f"Predicted {ylabel}")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_validation_results(records: list[ExperimentRecord], output_dir: Path) -> None:
    """Create validation plots and save them to the outputs directory."""
    plt = _import_pyplot()
    output_dir.mkdir(parents=True, exist_ok=True)
    law = baseline_regression_rate_law()
    predictions = [predict_performance(record.oxidizer_flow_slpm, law, record) for record in records]

    _save_single_point_plot(
        experimental=[record.thrust_n_exp for record in records],
        predicted=[prediction.thrust_n for prediction in predictions],
        ylabel="Thrust (N)",
        title="Predicted vs Experimental Thrust",
        output_path=output_dir / "predicted_vs_experimental_thrust.png",
    )
    _save_single_point_plot(
        experimental=[record.chamber_pressure_bar_exp for record in records],
        predicted=[prediction.chamber_pressure_bar for prediction in predictions],
        ylabel="Chamber Pressure (bar)",
        title="Predicted vs Experimental Chamber Pressure",
        output_path=output_dir / "predicted_vs_experimental_pressure.png",
    )
    _save_single_point_plot(
        experimental=[record.isp_equiv_m_s_exp / STANDARD_GRAVITY_M_S2 for record in records],
        predicted=[prediction.isp_s for prediction in predictions],
        ylabel="Isp (s)",
        title="Predicted vs Experimental Isp",
        output_path=output_dir / "predicted_vs_experimental_isp.png",
    )

    base_record = records[0] if records else DEFAULT_EXPERIMENT
    initial_radius_m = base_record.initial_port_diameter_mm * MM_TO_M / 2.0
    port_area = 3.141592653589793 * initial_radius_m**2
    flow_values = [140.0, 160.0, 180.0, 197.0, 220.0, 240.0]
    mass_flux_values: list[float] = []
    regression_values: list[float] = []
    for flow_slpm in flow_values:
        prediction = predict_performance(flow_slpm, DEFAULT_REGRESSION_LAW, base_record)
        mass_flux_values.append(prediction.oxidizer_mass_flow_kg_s / port_area)
        regression_values.append(prediction.regression_rate_m_s * 1e3)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(mass_flux_values, regression_values, marker="o", color="#d62728")
    ax.set_xlabel("Oxidizer Mass Flux, Gox (kg/m^2/s)")
    ax.set_ylabel("Regression Rate (mm/s)")
    ax.set_title("Regression Rate vs Oxidizer Mass Flux")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "regression_rate_vs_oxidizer_mass_flux.png", dpi=200)
    plt.close(fig)


def generate_plots(data_path: Path, output_dir: Path) -> None:
    """Load data and generate all project plots."""
    plot_validation_results(load_experimental_data(data_path), output_dir)
