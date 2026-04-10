"""Project constants and baseline laboratory values."""

from hybrid_rocket.models import ExperimentRecord, RegressionLaw

STANDARD_GRAVITY_M_S2 = 9.80665
BAR_TO_PA = 100_000.0
MM_TO_M = 1e-3
SLPM_TO_M3_S = 1e-3 / 60.0
GRAM_TO_KG = 1e-3

DEFAULT_EXPERIMENT = ExperimentRecord(
    test_id="LAB-001",
    oxidizer_flow_slpm=197.0,
    oxidizer_density_g_per_l=1.842,
    initial_fuel_mass_g=100.8,
    final_fuel_mass_g=67.86,
    burn_time_s=5.0,
    initial_port_diameter_mm=10.0,
    grain_length_mm=100.0,
    paraffin_density_kg_m3=900.0,
    throat_diameter_mm=6.0,
    chamber_pressure_bar_exp=4.0293,
    thrust_n_exp=21.943,
    cstar_exp_m_s=912.96,
    cstar_theo_m_s=1048.2,
    cf=1.4294,
    isp_equiv_m_s_exp=1498.3,
)

# The baseline regression rate coefficient is calibrated from the supplied
# laboratory test using a commonly used form r_dot = a * G_ox^n, with n fixed
# to 0.5 for simplicity in undergraduate analysis.
DEFAULT_REGRESSION_LAW = RegressionLaw(a=1.5749799449567343e-4, n=0.5)
