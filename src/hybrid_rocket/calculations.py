"""Core engineering calculations for a simple hybrid rocket model."""

from __future__ import annotations

import math

from hybrid_rocket.constants import BAR_TO_PA, GRAM_TO_KG, MM_TO_M, SLPM_TO_M3_S, STANDARD_GRAVITY_M_S2


def _require_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value!r}.")


def oxidizer_mass_flow_kg_s(flow_slpm: float, density_g_per_l: float) -> float:
    """Convert oxidizer volumetric flow in SLPM to mass flow rate in kg/s."""
    _require_positive(flow_slpm, "flow_slpm")
    _require_positive(density_g_per_l, "density_g_per_l")
    volumetric_flow_m3_s = flow_slpm * SLPM_TO_M3_S
    density_kg_m3 = density_g_per_l
    return volumetric_flow_m3_s * density_kg_m3


def fuel_mass_flow_kg_s(initial_fuel_mass_g: float, final_fuel_mass_g: float, burn_time_s: float) -> float:
    """Compute average fuel mass flow from the measured mass loss."""
    _require_positive(initial_fuel_mass_g, "initial_fuel_mass_g")
    _require_positive(final_fuel_mass_g, "final_fuel_mass_g")
    _require_positive(burn_time_s, "burn_time_s")
    if final_fuel_mass_g >= initial_fuel_mass_g:
        raise ValueError("final_fuel_mass_g must be less than initial_fuel_mass_g.")
    return (initial_fuel_mass_g - final_fuel_mass_g) * GRAM_TO_KG / burn_time_s


def final_port_diameter_m(
    initial_fuel_mass_g: float,
    final_fuel_mass_g: float,
    paraffin_density_kg_m3: float,
    grain_length_mm: float,
    initial_port_diameter_mm: float,
) -> float:
    """Estimate the final port diameter from the burnt fuel volume."""
    _require_positive(paraffin_density_kg_m3, "paraffin_density_kg_m3")
    _require_positive(grain_length_mm, "grain_length_mm")
    _require_positive(initial_port_diameter_mm, "initial_port_diameter_mm")
    burnt_mass_kg = (initial_fuel_mass_g - final_fuel_mass_g) * GRAM_TO_KG
    if burnt_mass_kg <= 0:
        raise ValueError("Burnt fuel mass must be positive.")
    burnt_volume_m3 = burnt_mass_kg / paraffin_density_kg_m3
    grain_length_m = grain_length_mm * MM_TO_M
    initial_radius_m = initial_port_diameter_mm * MM_TO_M / 2.0
    final_radius_squared = initial_radius_m**2 + burnt_volume_m3 / (math.pi * grain_length_m)
    return 2.0 * math.sqrt(final_radius_squared)


def regression_rate_m_s(final_port_diameter_m: float, initial_port_diameter_mm: float, burn_time_s: float) -> float:
    """Average radial regression rate based on the change in port radius."""
    _require_positive(final_port_diameter_m, "final_port_diameter_m")
    _require_positive(initial_port_diameter_mm, "initial_port_diameter_mm")
    _require_positive(burn_time_s, "burn_time_s")
    initial_radius_m = initial_port_diameter_mm * MM_TO_M / 2.0
    final_radius_m = final_port_diameter_m / 2.0
    if final_radius_m <= initial_radius_m:
        raise ValueError("Final port radius must be larger than initial port radius.")
    return (final_radius_m - initial_radius_m) / burn_time_s


def of_ratio(oxidizer_mass_flow_kg_s_value: float, fuel_mass_flow_kg_s_value: float) -> float:
    """Compute oxidizer-to-fuel ratio."""
    _require_positive(oxidizer_mass_flow_kg_s_value, "oxidizer_mass_flow_kg_s_value")
    _require_positive(fuel_mass_flow_kg_s_value, "fuel_mass_flow_kg_s_value")
    return oxidizer_mass_flow_kg_s_value / fuel_mass_flow_kg_s_value


def throat_area_m2(throat_diameter_mm: float) -> float:
    """Compute nozzle throat area from throat diameter."""
    _require_positive(throat_diameter_mm, "throat_diameter_mm")
    throat_radius_m = throat_diameter_mm * MM_TO_M / 2.0
    return math.pi * throat_radius_m**2


def cstar_experimental_m_s(
    chamber_pressure_bar: float,
    throat_area_m2_value: float,
    total_mass_flow_kg_s: float,
) -> float:
    """Characteristic velocity estimated from measured chamber pressure."""
    _require_positive(chamber_pressure_bar, "chamber_pressure_bar")
    _require_positive(throat_area_m2_value, "throat_area_m2_value")
    _require_positive(total_mass_flow_kg_s, "total_mass_flow_kg_s")
    chamber_pressure_pa = chamber_pressure_bar * BAR_TO_PA
    return chamber_pressure_pa * throat_area_m2_value / total_mass_flow_kg_s


def thrust_theoretical_n(cf: float, chamber_pressure_bar: float, throat_area_m2_value: float) -> float:
    """Ideal thrust from thrust coefficient and chamber pressure."""
    _require_positive(cf, "cf")
    _require_positive(chamber_pressure_bar, "chamber_pressure_bar")
    _require_positive(throat_area_m2_value, "throat_area_m2_value")
    chamber_pressure_pa = chamber_pressure_bar * BAR_TO_PA
    return cf * chamber_pressure_pa * throat_area_m2_value


def isp_seconds(thrust_n: float, total_mass_flow_kg_s: float) -> float:
    """Specific impulse in seconds."""
    _require_positive(thrust_n, "thrust_n")
    _require_positive(total_mass_flow_kg_s, "total_mass_flow_kg_s")
    return thrust_n / (total_mass_flow_kg_s * STANDARD_GRAVITY_M_S2)


def combustion_efficiency(cstar_exp_m_s: float, cstar_theo_m_s: float) -> float:
    """Simple combustion efficiency based on characteristic velocity."""
    _require_positive(cstar_exp_m_s, "cstar_exp_m_s")
    _require_positive(cstar_theo_m_s, "cstar_theo_m_s")
    return cstar_exp_m_s / cstar_theo_m_s

