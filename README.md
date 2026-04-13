# Hybrid Rocket Performance Prediction Model

This project is a lightweight Python 3.14 package for an undergraduate hybrid rocket propulsion lab. It predicts chamber pressure, thrust, and specific impulse from oxidizer flow and a simple regression-rate law, then compares those predictions with experimental-style data from a paraffin/N2O hybrid motor test.

## Project Aim

Build a clear and explainable performance model for a laboratory-scale hybrid rocket motor using standard propulsion relations instead of CFD or black-box fitting.

## Problem Statement

In a hybrid rocket, oxidizer enters the port, fuel regresses from the solid grain wall, and the total mass flow through the nozzle determines chamber pressure and thrust. The challenge is to estimate the main performance parameters from a small set of measurable lab inputs:

- oxidizer volumetric flow rate
- oxidizer density
- fuel mass loss
- grain geometry
- nozzle throat diameter
- burn time

## Physics and Formulas Used

The code uses the following simple engineering relations.

1. Oxidizer mass flow:

```text
mdot_ox = Q_ox * rho_ox
```

where `Q_ox` is oxidizer volumetric flow rate and `rho_ox` is oxidizer density.

2. Fuel mass flow from experimental mass loss:

```text
mdot_f = (m_f,initial - m_f,final) / t_b
```

3. Final port diameter from burnt fuel volume:

```text
V_burnt = (m_f,initial - m_f,final) / rho_f
V_burnt = pi * L * (r_f^2 - r_i^2)
```

4. Average regression rate:

```text
rdot = (r_f - r_i) / t_b
```

5. Regression-rate law used for prediction:

```text
rdot = a * G_ox^n
```

where `G_ox = mdot_ox / A_port`.

6. Fuel mass flow used in prediction:

```text
mdot_f,pred = rho_f * A_burn * rdot
A_burn = 2 * pi * r_avg * L
```

7. O/F ratio:

```text
O/F = mdot_ox / mdot_f
```

8. Characteristic velocity:

```text
C* = Pc * At / mdot_total
```

9. Chamber pressure prediction:

```text
Pc = mdot_total * C*_theoretical / At
```

10. Thrust:

```text
F = Cf * Pc * At
```

11. Specific impulse:

```text
Isp = F / (mdot_total * g0)
```

## Assumptions

- The grain port is cylindrical and regresses uniformly along the entire grain length.
- Regression follows a simple power law `rdot = a G_ox^n`.
- The exponent `n` is fixed at `0.5`, which is a common classroom-level simplification.
- The coefficient `a` is calibrated from the supplied baseline experiment.
- Flow properties and nozzle coefficient `Cf` are treated as constant during the short burn.
- Chamber pressure is estimated from the characteristic-velocity relation using the provided theoretical `C*`.
- The model is intentionally low-order and presentation-friendly, not a full transient combustion simulation.

## Laboratory Data Used

Baseline values included in `data/experimental_data.csv`:

- fuel grain length = 100 mm
- initial port diameter = 10 mm
- outer diameter = 40 mm
- initial fuel mass = 100.8 g
- final fuel mass = 67.86 g
- oxidizer volumetric flow rate = 197 SLPM
- N2O density at ambient = 1.842 g/L
- paraffin density = 900 kg/m^3
- throat diameter = 6 mm
- motor run time = 5 s
- average chamber pressure ≈ 4.0293 bar
- experimental `C*` ≈ 912.96 m/s
- theoretical `C*` ≈ 1048.2 m/s
- thrust coefficient `Cf` ≈ 1.4294
- reference thrust ≈ 21.943 N
- `Isp` equivalent exhaust velocity input ≈ 1498.3 m/s

## Folder Structure

```text
.
├── data/
│   └── experimental_data.csv
├── outputs/
├── src/
│   └── hybrid_rocket/
│       ├── __init__.py
│       ├── calculations.py
│       ├── cli.py
│       ├── constants.py
│       ├── models.py
│       ├── plots.py
│       └── validation.py
├── tests/
│   └── test_calculations.py
├── pyproject.toml
└── README.md
```

## Setup Guide

This project requires Python `3.14` as defined in `pyproject.toml`.

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd project
```

### 2. Install `uv` or use `pip`

Option A: install `uv` (recommended)

```bash
pip install uv
```

If `pip` is not available on your machine, install Python first and then verify:

```bash
python --version
python -m pip --version
```

Option B: use standard `pip` only

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install project dependencies

Using `uv`:

```bash
uv venv --python 3.14 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Using `pip`:

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file installs the project plus its required libraries such as `matplotlib`, `typer`, and `pytest`.

## How to Run It

### Executable entry point

This project does not ship a separate standalone executable file such as `run.sh` or `main.exe`.

The runnable entry point is the Python CLI module:

- `src/hybrid_rocket/cli.py`

You run it through Python as a module:

```bash
python -m hybrid_rocket.cli <command>
```

If you are using the local virtual environment without activation, you can also run:

```bash
.venv/bin/python -m hybrid_rocket.cli <command>
```

### Available commands

Run a baseline prediction:

```bash
python -m hybrid_rocket.cli run
```

Run validation and save the CSV summary:

```bash
python -m hybrid_rocket.cli validate
```

Generate plots:

```bash
python -m hybrid_rocket.cli plot
```

Run tests:

```bash
python -m pytest
```

### Custom input and output paths

The `validate` and `plot` commands accept file paths.

Use a custom input CSV for validation:

```bash
python -m hybrid_rocket.cli validate --data-path data/experimental_data.csv
```

Save validation output to a custom file:

```bash
python -m hybrid_rocket.cli validate --output-path outputs/validation_summary.csv
```

Generate plots from a custom dataset and save them to a custom folder:

```bash
python -m hybrid_rocket.cli plot --data-path data/experimental_data.csv --output-dir outputs
```

## How to See the Results

### Where results are saved

By default, the generated results are saved inside the `outputs/` folder.

Validation output:

- `outputs/validation_summary.csv`

Plot outputs:

- `outputs/predicted_vs_experimental_thrust.png`
- `outputs/predicted_vs_experimental_pressure.png`
- `outputs/predicted_vs_experimental_isp.png`
- `outputs/regression_rate_vs_oxidizer_mass_flux.png`

Matplotlib may also create:

- `outputs/.mplconfig/`

### How to open the results

- Open `outputs/validation_summary.csv` in Excel, LibreOffice Calc, Google Sheets, or any CSV viewer.
- Open the `.png` files from the `outputs/` folder using any image viewer.

### How input data is provided

The main input file is:

- `data/experimental_data.csv`

The application reads this CSV file when you run `validate` or `plot`.

Current CSV columns:

- `test_id`
- `oxidizer_flow_slpm`
- `oxidizer_density_g_per_l`
- `initial_fuel_mass_g`
- `final_fuel_mass_g`
- `burn_time_s`
- `initial_port_diameter_mm`
- `grain_length_mm`
- `paraffin_density_kg_m3`
- `throat_diameter_mm`
- `chamber_pressure_bar_exp`
- `thrust_n_exp`
- `cstar_exp_m_s`
- `cstar_theo_m_s`
- `cf`
- `isp_equiv_m_s_exp`

To use your own data, add more rows to `data/experimental_data.csv` in the same format, or create another CSV file with the same column names and pass it using `--data-path`.

## Explanation of Each Plot

`predicted_vs_experimental_thrust.png`
- Compares model thrust with the reference lab value.
- The dashed 45 degree line represents perfect agreement.

`predicted_vs_experimental_pressure.png`
- Compares predicted chamber pressure with measured chamber pressure.
- Useful for checking whether the total mass-flow estimate is realistic.

`predicted_vs_experimental_isp.png`
- Compares predicted specific impulse with the reference value converted to seconds.
- Helps explain nozzle and combustion performance together.

`regression_rate_vs_oxidizer_mass_flux.png`
- Shows the effect of oxidizer mass flux on fuel regression rate.
- This plot is useful in viva because it directly connects injector flow to fuel consumption and thrust generation.

## How to Explain This in Viva / Presentation

You can present the model in four steps:

1. First convert oxidizer flow from SLPM into mass flow rate.
2. Then estimate how fast the paraffin surface regresses using `rdot = a G_ox^n`.
3. Add oxidizer and fuel mass flow to get total nozzle flow, then estimate chamber pressure from `Pc = mdot_total * C* / At`.
4. Finally compute thrust using `F = Cf * Pc * At` and Isp using `Isp = F / (mdot_total * g0)`.

A good viva statement is:

> “This is a first-order hybrid rocket model. It does not simulate detailed combustion chemistry, but it captures the main coupling between oxidizer flow, fuel regression, chamber pressure, thrust, and Isp using standard propulsion equations.”

## Notes on Validation

The current dataset contains one documented baseline lab-style test case. That is enough to demonstrate the prediction workflow, validation CSV generation, and plotting pipeline. Additional rows can be added later in the same format to extend the validation study.
