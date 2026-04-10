"""Tests for core hybrid rocket calculations."""

from __future__ import annotations

import math

import pytest

from hybrid_rocket.calculations import (
    combustion_efficiency,
    cstar_experimental_m_s,
    final_port_diameter_m,
    fuel_mass_flow_kg_s,
    isp_seconds,
    of_ratio,
    oxidizer_mass_flow_kg_s,
    regression_rate_m_s,
    throat_area_m2,
)
from hybrid_rocket.constants import DEFAULT_EXPERIMENT, STANDARD_GRAVITY_M_S2
from hybrid_rocket.validation import baseline_regression_rate_law, predict_performance


def test_oxidizer_mass_flow_matches_lab_value() -> None:
    mass_flow = oxidizer_mass_flow_kg_s(197.0, 1.842)
    assert mass_flow == pytest.approx(0.0060479, rel=1e-4)


def test_fuel_mass_flow_matches_mass_loss() -> None:
    mass_flow = fuel_mass_flow_kg_s(100.8, 67.86, 5.0)
    assert mass_flow == pytest.approx(0.006588, rel=1e-4)


def test_final_port_and_regression_rate_are_positive() -> None:
    final_port = final_port_diameter_m(100.8, 67.86, 900.0, 100.0, 10.0)
    regression = regression_rate_m_s(final_port, 10.0, 5.0)
    assert final_port == pytest.approx(0.023793, rel=1e-3)
    assert regression == pytest.approx(0.001379, rel=1e-3)


def test_of_ratio_and_throat_area_are_reasonable() -> None:
    ox = oxidizer_mass_flow_kg_s(197.0, 1.842)
    fuel = fuel_mass_flow_kg_s(100.8, 67.86, 5.0)
    assert of_ratio(ox, fuel) == pytest.approx(0.918, rel=1e-3)
    assert throat_area_m2(6.0) == pytest.approx(math.pi * (0.003**2), rel=1e-12)


def test_cstar_and_efficiency_follow_given_reference_values() -> None:
    total_mass_flow = oxidizer_mass_flow_kg_s(197.0, 1.842) + fuel_mass_flow_kg_s(100.8, 67.86, 5.0)
    cstar = cstar_experimental_m_s(4.0293, throat_area_m2(6.0), total_mass_flow)
    efficiency = combustion_efficiency(912.96, 1048.2)
    assert cstar == pytest.approx(901.55, rel=2e-2)
    assert efficiency == pytest.approx(0.871, rel=1e-3)


def test_prediction_outputs_are_positive_and_consistent() -> None:
    prediction = predict_performance(
        oxidizer_flow_slpm=DEFAULT_EXPERIMENT.oxidizer_flow_slpm,
        regression_law=baseline_regression_rate_law(),
        record=DEFAULT_EXPERIMENT,
    )
    assert prediction.chamber_pressure_bar > 0
    assert prediction.thrust_n > 0
    assert prediction.isp_s > 0
    assert prediction.chamber_pressure_bar == pytest.approx(4.628, rel=3e-2)
    assert prediction.thrust_n == pytest.approx(18.70, rel=3e-2)
    assert prediction.isp_s == pytest.approx(151.0, rel=3e-2)


def test_isp_seconds_definition() -> None:
    total_mass_flow = 0.0125
    thrust = 18.39
    assert isp_seconds(thrust, total_mass_flow) == pytest.approx(thrust / (total_mass_flow * STANDARD_GRAVITY_M_S2))
