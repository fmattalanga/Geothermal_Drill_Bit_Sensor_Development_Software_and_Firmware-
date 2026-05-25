"""
ADXL206HDZ Dual-Axis MEMS Accelerometer Simulation
Sensitivity: 328 mV/g  |  Range: ±5 g  |  VCC: 5.0 V  |  Max Temp: 175°C
Output: XOUT, YOUT ratiometric to VCC
"""
import numpy as np
from scipy.signal import butter, sosfilt

VCC                = 5.0    # Supply voltage (V)
SENSITIVITY_MV_G   = 328.0  # mV/g at 5V (datasheet typical)
SENSITIVITY_V_G    = SENSITIVITY_MV_G / 1000.0
ZERO_G_OUTPUT_V    = VCC / 2.0   # 2.5 V at 0 g
RANGE_G            = 5.0
RESONANT_FREQ_HZ   = 5500.0  # Typical MEMS resonance for bandwidth set by Cx/Cy
DAMPING_RATIO      = 0.70    # Critical damping approximation

# Temperature coefficient of sensitivity: −0.01%/°C (datasheet)
TEMP_COEFF_SENS    = -0.0001
NOISE_FLOOR_G_RMS  = 0.001   # 1 mg noise floor (110 µg/√Hz × √(BW))


def sensitivity_at_temp(temp_c):
    """Return adjusted sensitivity (V/g) at a given temperature."""
    delta = 1.0 + TEMP_COEFF_SENS * (temp_c - 25.0)
    return SENSITIVITY_V_G * delta

def acceleration_to_voltage(accel_g, temp_c=25.0, noise=True):
    """
    Convert acceleration (g) to ADXL206 output voltage.
    Clamps to ±5 g. Adds noise floor if requested.
    Returns: voltage (V)
    """
    accel_g = np.clip(accel_g, -RANGE_G, RANGE_G)
    sens = sensitivity_at_temp(temp_c)
    v_out = ZERO_G_OUTPUT_V + accel_g * sens
    if noise:
        v_out += np.random.normal(0, NOISE_FLOOR_G_RMS * sens,
                                   np.asarray(accel_g).shape or (1,))
    return v_out

def inclination_from_dual_axis(x_g, y_g):
    """
    Compute inclination angle (degrees) from dual-axis reading.
    Uses arctangent. Returns (pitch, roll) in degrees.
    """
    pitch_rad = np.arctan2(x_g, np.sqrt(-y_g**2 + 1.0))
    roll_rad  = np.arctan2(y_g, np.sqrt(x_g**2 + 1.0))
    return np.degrees(pitch_rad), np.degrees(roll_rad)

def simulate_static_tilt(pitch_deg, roll_deg, temp_c=25.0):
    """
    Given a known tilt, return simulated XOUT/YOUT voltages.
    Converts angles to g-components via gravity projection.
    """
    x_g = np.sin(np.radians(pitch_deg))
    y_g = np.sin(np.radians(roll_deg))
    vx = acceleration_to_voltage(x_g, temp_c, noise=False)
    vy = acceleration_to_voltage(y_g, temp_c, noise=False)
    return vx, vy
