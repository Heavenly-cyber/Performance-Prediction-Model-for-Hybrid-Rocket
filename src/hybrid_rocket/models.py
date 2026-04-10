"""Data models for hybrid rocket calculations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExperimentRecord:
    """Single experimental record used for validation and baseline setup."""

    test_id: str
    oxidizer_flow_slpm: float
    oxidizer_density_g_per_l: float
    initial_fuel_mass_g: float
    final_fuel_mass_g: float
    burn_time_s: float
    initial_port_diameter_mm: float
    grain_length_mm: float
    paraffin_density_kg_m3: float
    throat_diameter_mm: float
    chamber_pressure_bar_exp: float
    thrust_n_exp: float
    cstar_exp_m_s: float
    cstar_theo_m_s: float
    cf: float
    isp_equiv_m_s_exp: float


@dataclass(slots=True)
class RegressionLaw:
    """Regression rate law coefficients in r_dot = a * G_ox^n."""

    a: float
    n: float


@dataclass(slots=True)
class PredictionResult:
    """Predicted rocket performance values for one operating point."""

    test_id: str
    oxidizer_mass_flow_kg_s: float
    fuel_mass_flow_kg_s: float
    total_mass_flow_kg_s: float
    oxidizer_mass_flux_kg_m2_s: float
    regression_rate_m_s: float
    final_port_diameter_m: float
    of_ratio: float
    chamber_pressure_pa: float
    chamber_pressure_bar: float
    thrust_n: float
    isp_s: float
    cstar_used_m_s: float
    combustion_efficiency: float


@dataclass(slots=True)
class ValidationResult:
    """Comparison between predicted and experimental values."""

    test_id: str
    chamber_pressure_bar_pred: float
    chamber_pressure_bar_exp: float
    chamber_pressure_abs_error: float
    chamber_pressure_pct_error: float
    thrust_n_pred: float
    thrust_n_exp: float
    thrust_abs_error: float
    thrust_pct_error: float
    isp_s_pred: float
    isp_s_exp: float
    isp_abs_error: float
    isp_pct_error: float
