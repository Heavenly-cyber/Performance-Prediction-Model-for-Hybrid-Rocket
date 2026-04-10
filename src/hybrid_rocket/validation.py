"""Validation and prediction workflow for the hybrid rocket model."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from hybrid_rocket.calculations import (
    combustion_efficiency,
    final_port_diameter_m,
    fuel_mass_flow_kg_s,
    isp_seconds,
    of_ratio,
    oxidizer_mass_flow_kg_s,
    regression_rate_m_s,
    throat_area_m2,
)
from hybrid_rocket.constants import BAR_TO_PA, DEFAULT_EXPERIMENT, DEFAULT_REGRESSION_LAW, MM_TO_M, STANDARD_GRAVITY_M_S2
from hybrid_rocket.models import ExperimentRecord, PredictionResult, RegressionLaw, ValidationResult


def load_experimental_data(csv_path: Path) -> list[ExperimentRecord]:
    """Load the experimental dataset from CSV."""
    records: list[ExperimentRecord] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                ExperimentRecord(
                    test_id=row["test_id"],
                    oxidizer_flow_slpm=float(row["oxidizer_flow_slpm"]),
                    oxidizer_density_g_per_l=float(row["oxidizer_density_g_per_l"]),
                    initial_fuel_mass_g=float(row["initial_fuel_mass_g"]),
                    final_fuel_mass_g=float(row["final_fuel_mass_g"]),
                    burn_time_s=float(row["burn_time_s"]),
                    initial_port_diameter_mm=float(row["initial_port_diameter_mm"]),
                    grain_length_mm=float(row["grain_length_mm"]),
                    paraffin_density_kg_m3=float(row["paraffin_density_kg_m3"]),
                    throat_diameter_mm=float(row["throat_diameter_mm"]),
                    chamber_pressure_bar_exp=float(row["chamber_pressure_bar_exp"]),
                    thrust_n_exp=float(row["thrust_n_exp"]),
                    cstar_exp_m_s=float(row["cstar_exp_m_s"]),
                    cstar_theo_m_s=float(row["cstar_theo_m_s"]),
                    cf=float(row["cf"]),
                    isp_equiv_m_s_exp=float(row["isp_equiv_m_s_exp"]),
                )
            )
    return records


def baseline_regression_rate_law(record: ExperimentRecord = DEFAULT_EXPERIMENT) -> RegressionLaw:
    """Calibrate the default regression law coefficient from the baseline test."""
    oxidizer_flow = oxidizer_mass_flow_kg_s(record.oxidizer_flow_slpm, record.oxidizer_density_g_per_l)
    initial_port_area = 3.141592653589793 * (record.initial_port_diameter_mm * MM_TO_M / 2.0) ** 2
    oxidizer_mass_flux = oxidizer_flow / initial_port_area
    final_port = final_port_diameter_m(
        record.initial_fuel_mass_g,
        record.final_fuel_mass_g,
        record.paraffin_density_kg_m3,
        record.grain_length_mm,
        record.initial_port_diameter_mm,
    )
    measured_regression_rate = regression_rate_m_s(final_port, record.initial_port_diameter_mm, record.burn_time_s)
    law_n = DEFAULT_REGRESSION_LAW.n
    law_a = measured_regression_rate / (oxidizer_mass_flux**law_n)
    return RegressionLaw(a=law_a, n=law_n)


def predict_performance(
    oxidizer_flow_slpm: float,
    regression_law: RegressionLaw,
    record: ExperimentRecord = DEFAULT_EXPERIMENT,
) -> PredictionResult:
    """Predict chamber pressure, thrust, and Isp from a simple engineering model.

    Assumptions:
    1. Port geometry is cylindrical and regresses uniformly along the grain length.
    2. Regression follows r_dot = a * G_ox^n using the initial oxidizer mass flux.
    3. Fuel mass flow is based on the average burning surface area over the burn.
    4. C* efficiency is taken from the baseline experiment and reused for prediction.
    5. Thrust coefficient is treated as constant for the operating window of interest.
    """
    oxidizer_mass_flow = oxidizer_mass_flow_kg_s(oxidizer_flow_slpm, record.oxidizer_density_g_per_l)
    initial_radius_m = record.initial_port_diameter_mm * MM_TO_M / 2.0
    initial_port_area_m2 = 3.141592653589793 * initial_radius_m**2
    oxidizer_mass_flux = oxidizer_mass_flow / initial_port_area_m2
    regression_rate = regression_law.a * (oxidizer_mass_flux**regression_law.n)
    final_port_diameter = record.initial_port_diameter_mm * MM_TO_M + 2.0 * regression_rate * record.burn_time_s
    final_radius_m = final_port_diameter / 2.0
    average_radius_m = 0.5 * (initial_radius_m + final_radius_m)
    burning_area_m2 = 2.0 * 3.141592653589793 * average_radius_m * (record.grain_length_mm * MM_TO_M)
    fuel_mass_flow = record.paraffin_density_kg_m3 * burning_area_m2 * regression_rate
    total_mass_flow = oxidizer_mass_flow + fuel_mass_flow
    chamber_pressure_pa = total_mass_flow * record.cstar_theo_m_s / throat_area_m2(record.throat_diameter_mm)
    chamber_pressure_bar = chamber_pressure_pa / BAR_TO_PA
    thrust_n = record.cf * chamber_pressure_pa * throat_area_m2(record.throat_diameter_mm)
    isp_s = isp_seconds(thrust_n, total_mass_flow)
    cstar_used = record.cstar_theo_m_s
    efficiency = combustion_efficiency(record.cstar_exp_m_s, record.cstar_theo_m_s)
    return PredictionResult(
        test_id=record.test_id,
        oxidizer_mass_flow_kg_s=oxidizer_mass_flow,
        fuel_mass_flow_kg_s=fuel_mass_flow,
        total_mass_flow_kg_s=total_mass_flow,
        oxidizer_mass_flux_kg_m2_s=oxidizer_mass_flux,
        regression_rate_m_s=regression_rate,
        final_port_diameter_m=final_port_diameter,
        of_ratio=of_ratio(oxidizer_mass_flow, fuel_mass_flow),
        chamber_pressure_pa=chamber_pressure_pa,
        chamber_pressure_bar=chamber_pressure_bar,
        thrust_n=thrust_n,
        isp_s=isp_s,
        cstar_used_m_s=cstar_used,
        combustion_efficiency=efficiency,
    )


def compare_prediction(record: ExperimentRecord, prediction: PredictionResult) -> ValidationResult:
    """Compare predicted values with experimental measurements."""
    isp_exp_s = record.isp_equiv_m_s_exp / STANDARD_GRAVITY_M_S2
    pressure_abs = abs(prediction.chamber_pressure_bar - record.chamber_pressure_bar_exp)
    thrust_abs = abs(prediction.thrust_n - record.thrust_n_exp)
    isp_abs = abs(prediction.isp_s - isp_exp_s)
    return ValidationResult(
        test_id=record.test_id,
        chamber_pressure_bar_pred=prediction.chamber_pressure_bar,
        chamber_pressure_bar_exp=record.chamber_pressure_bar_exp,
        chamber_pressure_abs_error=pressure_abs,
        chamber_pressure_pct_error=100.0 * pressure_abs / record.chamber_pressure_bar_exp,
        thrust_n_pred=prediction.thrust_n,
        thrust_n_exp=record.thrust_n_exp,
        thrust_abs_error=thrust_abs,
        thrust_pct_error=100.0 * thrust_abs / record.thrust_n_exp,
        isp_s_pred=prediction.isp_s,
        isp_s_exp=isp_exp_s,
        isp_abs_error=isp_abs,
        isp_pct_error=100.0 * isp_abs / isp_exp_s,
    )


def save_validation_summary(results: list[ValidationResult], output_path: Path) -> None:
    """Write the validation summary CSV to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "test_id",
                "chamber_pressure_bar_pred",
                "chamber_pressure_bar_exp",
                "chamber_pressure_abs_error",
                "chamber_pressure_pct_error",
                "thrust_n_pred",
                "thrust_n_exp",
                "thrust_abs_error",
                "thrust_pct_error",
                "isp_s_pred",
                "isp_s_exp",
                "isp_abs_error",
                "isp_pct_error",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def run_validation(data_path: Path, output_path: Path) -> list[ValidationResult]:
    """Execute the validation workflow for the full dataset."""
    records = load_experimental_data(data_path)
    law = baseline_regression_rate_law()
    results = [compare_prediction(record, predict_performance(record.oxidizer_flow_slpm, law, record)) for record in records]
    save_validation_summary(results, output_path)
    return results
