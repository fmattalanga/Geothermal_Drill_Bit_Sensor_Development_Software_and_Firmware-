# Data Directory

Sample sensor data files for the GeoTorpedo ICS analytics notebook.

---

## File Naming Convention

```
ICS_<firmware>_<run-type>_<YYYYMMDD>_<HHMMSS>_<rate>.csv
```

| Token | Example | Meaning |
|---|---|---|
| `firmware` | `FW1`, `FW2`, `SIM` | Firmware version or simulation |
| `run-type` | `CAL` (calibration), `GEN` (generator), `SIM` (simulation) | Run type |
| `YYYYMMDD` | `20260401` | Run date |
| `HHMMSS` | `120000` | Run start time (UTC) |
| `rate` | `100Hz`, `1Hz` | Sample rate |

---

## File Format

All CSV files begin with `#` comment lines that embed run metadata:

```
# ICS Core 100 Hz CSV | Run: ICS_SIM_20260401_120000
# Generated: 2026-04-10T18:23:51.129714Z
# Temp compensation: LM95172 reference, per-component polynomial models
# vib_*_raw_g: T-compensated, NO kinematic correction applied
# vib_*_corr_g: T-compensated + Euler + Coriolis + R-matrix
elapsed_time_s, vib_x_raw_g, ...
```

The notebook parser (`load_csv_with_meta`) reads these automatically.

---

## 100 Hz High-Frequency Columns

| Column | Unit | Description |
|---|---|---|
| `elapsed_time_s` | s | Time since run start |
| `vib_x_raw_g` | g | X-axis vibration — temperature-compensated, no kinematic correction |
| `vib_y_raw_g` | g | Y-axis vibration — temperature-compensated, no kinematic correction |
| `vib_z_raw_g` | g | Z-axis vibration — temperature-compensated, no kinematic correction |
| `vib_x_corr_g` | g | X-axis vibration — T-compensated + Euler + Coriolis + R-matrix |
| `vib_y_corr_g` | g | Y-axis vibration — fully corrected |
| `vib_z_corr_g` | g | Z-axis vibration — fully corrected |
| `vib_magnitude_corr_g` | g | Corrected 3-axis vibration magnitude |
| `vib_x_rms_g` | g | X-axis RMS vibration |
| `vib_y_rms_g` | g | Y-axis RMS vibration |
| `vib_z_rms_g` | g | Z-axis RMS vibration |
| `rpm` | RPM | Drill string rotational speed |
| `omega_z_dps` | deg/s | Z-axis angular velocity |
| `rpm_source` | — | Source algorithm for RPM estimate |
| `drill_condition` | — | Detected drill condition label |
| `condition_severity` | — | Severity score of detected condition |

---

## 1 Hz Low-Frequency Columns

| Column | Unit | Description |
|---|---|---|
| `elapsed_time_s` | s | Time since run start |
| `inclination_deg` | deg | Borehole inclination angle |
| `toolface_deg` | deg | Tool face orientation |
| `inclination_valid` | bool | 1 = static (valid), 0 = rotating (suppressed) |
| `inclination_source` | — | Source: `static_accel` or `gyro_integrated` |
| `temp_internal_c` | °C | Internal PCB temperature (LM95172) |
| `temp_external_c` | °C | External formation temperature (ADXL206HDZ reference) |
| `thermal_status` | — | `NORMAL`, `WARN`, or `CRITICAL` |
| `rpm_1hz` | RPM | 1 Hz averaged RPM |
| `depth_m` | m | Estimated drill depth |

---

## Sample Files in This Directory

| File | Rate | Rows | Description |
|---|---|---|---|
| `ICS_SIM_20260401_120000_100Hz.csv` | 100 Hz | ~16,000 | Simulated 160-second HF run |
| `ICS_SIM_20260401_120000_1Hz.csv` | 1 Hz | ~160 | Matching simulated LF run |

---

## Dysfunction Detection

The notebook derives additional channels from the above columns and flags the following drilling dysfunctions automatically:

| Dysfunction | Detection Method |
|---|---|
| Bit Bounce | Z-axis peak-to-peak vibration threshold |
| Lateral Whirl | X/Y vibration energy ratio + RPM correlation |
| Stick-Slip | RPM coefficient of variation over rolling window |
| High Shock | Instantaneous vibration magnitude threshold |
