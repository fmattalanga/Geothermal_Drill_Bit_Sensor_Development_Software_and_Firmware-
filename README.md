# ICS Core — Geothermal Downhole Sensor Pipeline

**University of Bath · GBDP Group 27 · Sensor IC Design**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter)](https://jupyter.org/)
[![pytest](https://img.shields.io/badge/tests-pytest-brightgreen?logo=pytest)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Full firmware simulation and analytics pipeline for the **ICS (Integrated Chip Sensor)** geothermal downhole tool — from sensor model validation through MCU firmware emulation to interactive post-run analytics.

> **Reference:** `G27_Shokrani_GeothermalSensorPackage_TR_Part5of6.pdf` · `ICS_Core_Pipeline_Technical_Reference.docx`

---

## Pipeline Overview

```
FW0: Assembly Validation
  └─ Writes sensor models to ics_sandbox/, runs pytest suite

FW1: Initialisation & Calibration  (dsPIC33AK256MC205-H/M7)
  └─ Boot sequence, NVM constants, static zero-cal, R-matrix, T-coeff cal

FW2: Data Generation  (dsPIC33AK256MC205-H/M7)
  └─ Simulates raw sensor streams → ICS_FW2_GEN_*_data_returns.json

FW3: Inertial Processing & CSV Export  (CC2642R1TWFRTCRQ1)
  └─ Kinematic artefact removal, inclination validity, rolling RMS → 100 Hz + 1 Hz CSVs

Analytics: GeoTorpedo Dashboard
  └─ 11 interactive Plotly figures, HTML operator report, live Grafana-style dashboard
```

---

## Repository Structure

```
.
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── .gitattributes                        # Git LFS rules for large files
│
├── ── Firmware Pipeline Notebooks ──
│
├── ICS_Core_Firmware0_Sensor IC_Assembly_Validation.ipynb
│   └─ Writes all sensor models to ics_sandbox/, runs full pytest validation
│
├── ICS_Core_Firmware1_dsPIC33AK256MC205_Initilisation_Calibration_.ipynb
│   └─ FW1: boot, NVM constants, static zero-cal, geometry cal, T-coeff cal
│
├── ICS_Core_Firmware2_dsPIC33AK256MC205_DataGeneration.ipynb
│   └─ FW2: simulates raw sensor data streams for all five sensors
│
├── ICS_Core_Firmware3_CC2642R1TWFRTCRQ1_inertialcAndCSV.ipynb
│   └─ FW3: kinematic correction, inclination validity, RMS, CSV export
│
├── Downhole_Drilling_Analytics_GeoTorpedo_v3.ipynb
│   └─ Post-run analytics — 11 plots, HTML report, live dashboard
│
├── ── Reference Documents ──
│
├── G27_Shokrani_GeothermalSensorPackage_TR_Part5of6.pdf
├── ICS_Core_Pipeline_Technical_Reference.docx
│
├── ── Sensor Simulation Package ──
│
├── ics_sandbox/
│   ├── simulation/
│   │   └── models/
│   │       ├── adxl206_model.py          # ADXL206HDZ dual-axis accelerometer (±5 g)
│   │       ├── adxrs645_model.py         # ADXRS645HDYZ rate gyroscope (±2000 dps)
│   │       ├── at10tb_model.py           # AT/10/TB IEPE accelerometer (±500 g, 50 kHz)
│   │       ├── lm95172_mock.py           # LM95172 SPI temperature sensor mock
│   │       └── max31856_mock.py          # MAX31856 thermocouple mock (Type K)
│   └── tests/
│       ├── test_adxl206.py
│       ├── test_adxrs645.py
│       ├── test_at10tb.py
│       ├── test_lm95172.py
│       └── test_max31856.py
│
├── ── Sample Data ──
│
├── ICS_SIM_20260401_120000_100Hz.csv     # Simulation run — 100 Hz HF data
├── ICS_SIM_20260401_120000_1Hz.csv       # Simulation run — 1 Hz LF data
│
├── ics_output/                           # Calibration run outputs (FW1)
│   ├── ICS_FW1_CAL_*_100Hz.csv
│   ├── ICS_FW1_CAL_*_1Hz.csv
│   └── ICS_FW1_CAL_*_nvm.json
│
├── ics_gen_output/                       # Generator run outputs (FW2)
│   └── ICS_FW2_GEN_*_data_returns.json
│
├── Bath Uni project 2026/                # Supplementary sampled data
│   ├── 100Hz Sampled.csv                 # ⚠ 21 MB
│   ├── 1Hz Sampled.csv
│   └── output.json
│
└── data/
    └── README.md                         # CSV schema & column definitions
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/<your-username>/ics-core-sensor-pipeline.git
cd ics-core-sensor-pipeline

# Pull Git LFS objects (large data files)
git lfs pull
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run sensor validation tests

```bash
cd ics_sandbox
pytest tests/ -v
```

Expected output: all 5 test modules pass.

### 4. Run the firmware pipeline (in order)

Open each notebook in Jupyter and run all cells top-to-bottom:

| Order | Notebook | Purpose |
|---|---|---|
| 0 | `ICS_Core_Firmware0_Sensor IC_Assembly_Validation.ipynb` | Writes models, runs pytest |
| 1 | `ICS_Core_Firmware1_dsPIC33AK256MC205_Initilisation_Calibration_.ipynb` | Boot & calibration |
| 2 | `ICS_Core_Firmware2_dsPIC33AK256MC205_DataGeneration.ipynb` | Raw data generation |
| 3 | `ICS_Core_Firmware3_CC2642R1TWFRTCRQ1_inertialcAndCSV.ipynb` | Processing & CSV export |
| 4 | `Downhole_Drilling_Analytics_GeoTorpedo_v3.ipynb` | Analytics & dashboards |

> FW2 writes `ics_gen_output/ICS_FW2_GEN_*_data_returns.json`. FW3 reads this file — run FW2 before FW3.

### 5. Run analytics on sample data

In `Downhole_Drilling_Analytics_GeoTorpedo_v3.ipynb`, Cell 2, uncomment the fallback paths:

```python
HF_PATH = "ICS_SIM_20260401_120000_100Hz.csv"
LF_PATH = "ICS_SIM_20260401_120000_1Hz.csv"
```

---

## Sensor Models (`ics_sandbox/simulation/models/`)

| Model | Sensor | Role | Key Specs |
|---|---|---|---|
| `adxl206_model.py` | ADXL206HDZ | Inclination accelerometer | ±5 g, 328 mV/g, 175°C |
| `adxrs645_model.py` | ADXRS645HDYZ | RPM / rotation gyroscope | ±2000 dps, 12.5 mV/dps, 175°C |
| `at10tb_model.py` | AT/10/TB IEPE | High-g vibration | ±500 g, 10 mV/g, 4.8 kHz AA, 12-bit ADC |
| `lm95172_mock.py` | LM95172 | Internal temperature (SPI) | −40 to 200°C, 13–16 bit |
| `max31856_mock.py` | MAX31856 | Thermocouple interface (SPI) | Type K, −270 to 1800°C |

All models include temperature-coefficient corrections from manufacturer datasheets. See [`ics_sandbox/README.md`](ics_sandbox/README.md) for details.

---

## Data Format

See [`data/README.md`](data/README.md) for full column definitions.

CSV files use `#` comment header lines for run metadata:

```
# ICS Core 100 Hz CSV | Run: ICS_SIM_20260401_120000
# Generated: 2026-04-10T18:23:51Z
# vib_*_raw_g: T-compensated, NO kinematic correction applied
# vib_*_corr_g: T-compensated + Euler + Coriolis + R-matrix
elapsed_time_s, vib_x_raw_g, vib_y_raw_g, ...
```

---

## Running Tests

```bash
cd ics_sandbox
pytest tests/ -v --tb=short
```

To regenerate the test report:

```bash
pytest tests/ -v --json-report --json-report-file=reports/results.json
```

*(Requires `pytest-json-report`: `pip install pytest-json-report`)*

---

## Dependencies

| Package | Use |
|---|---|
| `pandas`, `numpy` | Data loading and processing |
| `scipy` | Signal processing (FFT, filters, spectrograms) |
| `plotly` | Interactive figures |
| `ipywidgets` | File selector UI in notebooks |
| `kaleido` | Static image export for HTML reports |
| `jupyter`, `nbconvert` | Notebook environment |
| `pytest` | Sensor model test suite |

Full pinned list: [`requirements.txt`](requirements.txt)

---

## Git LFS

`Bath Uni project 2026/100Hz Sampled_converted.json` (91 MB) is tracked via Git LFS. Run `git lfs install` on a new machine before cloning, or pull LFS objects after:

```bash
git lfs install
git lfs pull
```

See [PUSH_TO_GITHUB.md](PUSH_TO_GITHUB.md) for the full setup sequence.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Strip notebook outputs with `nbstripout` before committing.

---

## License

MIT — see [LICENSE](LICENSE).

---

*University of Bath · ME32013 MEng Group Business Project · 2025–2026 · Group 27*
