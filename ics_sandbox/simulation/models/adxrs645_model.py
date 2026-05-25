"""
ADXRS645HDYZ MEMS Rate Gyroscope Simulation
Sensitivity: ~12.5 mV/(°/s)  |  Range: ±2000°/s  |  VRATIO: 5.0 V
Max Temp: 175°C
"""
import numpy as np

VRATIO             = 5.0
SENSITIVITY_MV_DPS = 12.5           # mV per degree per second
SENSITIVITY_V_DPS  = SENSITIVITY_MV_DPS / 1000.0
NULL_RATE_V        = VRATIO / 2.0   # 2.5 V at 0 °/s
RANGE_DPS          = 2000.0
NOISE_DPS_RMS      = 0.5            # Typical noise floor
BIAS_DPS           = 0.0            # Can be set to simulate bias error

# Temperature coefficient of null: 0.015 °/s/°C
TEMP_COEFF_NULL    = 0.015


def rate_to_voltage(rate_dps, temp_c=25.0, noise=True):
    """
    Convert angular rate (°/s) to ADXRS645 RATEOUT voltage.
    Includes bias, temperature-dependent null shift, and noise.
    """
    rate_dps = np.clip(rate_dps, -RANGE_DPS, RANGE_DPS)
    null_shift = TEMP_COEFF_NULL * (temp_c - 25.0)
    effective_rate = rate_dps + BIAS_DPS + null_shift
    v_out = NULL_RATE_V + effective_rate * SENSITIVITY_V_DPS
    if noise:
        n = np.random.normal(0, NOISE_DPS_RMS * SENSITIVITY_V_DPS,
                              np.asarray(rate_dps).shape or (1,))
        v_out += n
    return v_out

def voltage_to_rate(v_out, temp_c=25.0):
    """Reverse: voltage → angular rate (°/s), with temperature null correction."""
    null_shift = TEMP_COEFF_NULL * (temp_c - 25.0)
    return (v_out - NULL_RATE_V) / SENSITIVITY_V_DPS - null_shift

def integrate_rate_to_angle(rate_dps_array, dt_s):
    """Integrate angular rate to give angle (degrees). Simple Euler integration."""
    return np.cumsum(rate_dps_array) * dt_s
