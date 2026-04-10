"""Command line interface for the hybrid rocket project."""

from __future__ import annotations

from pathlib import Path

import typer

from hybrid_rocket.constants import DEFAULT_EXPERIMENT
from hybrid_rocket.validation import baseline_regression_rate_law, predict_performance, run_validation

app = typer.Typer(add_completion=False, help="Hybrid rocket performance prediction and validation.")


@app.command()
def run() -> None:
    """Run a single baseline prediction and print the main outputs."""
    prediction = predict_performance(
        oxidizer_flow_slpm=DEFAULT_EXPERIMENT.oxidizer_flow_slpm,
        regression_law=baseline_regression_rate_law(),
        record=DEFAULT_EXPERIMENT,
    )
    typer.echo(f"Test ID: {prediction.test_id}")
    typer.echo(f"Predicted chamber pressure: {prediction.chamber_pressure_bar:.4f} bar")
    typer.echo(f"Predicted thrust: {prediction.thrust_n:.3f} N")
    typer.echo(f"Predicted Isp: {prediction.isp_s:.3f} s")
    typer.echo(f"Predicted O/F ratio: {prediction.of_ratio:.3f}")
    typer.echo(f"Predicted regression rate: {prediction.regression_rate_m_s * 1e3:.3f} mm/s")


@app.command()
def validate(
    data_path: Path = Path("data/experimental_data.csv"),
    output_path: Path = Path("outputs/validation_summary.csv"),
) -> None:
    """Run validation against the experimental CSV and save a summary."""
    results = run_validation(data_path, output_path)
    typer.echo(f"Validated {len(results)} record(s).")
    typer.echo(f"Saved validation summary to {output_path}")


@app.command()
def plot(
    data_path: Path = Path("data/experimental_data.csv"),
    output_dir: Path = Path("outputs"),
) -> None:
    """Generate project plots."""
    from hybrid_rocket.plots import generate_plots

    generate_plots(data_path, output_dir)
    typer.echo(f"Saved plots to {output_dir}")


if __name__ == "__main__":
    app()
