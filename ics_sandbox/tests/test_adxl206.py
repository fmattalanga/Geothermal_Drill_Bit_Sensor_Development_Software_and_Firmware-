import pytest
import numpy as np
from simulation.models.adxl206_model import (
    acceleration_to_voltage,
    inclination_from_dual_axis,
    simulate_static_tilt,
    ZERO_G_OUTPUT_V,
    SENSITIVITY_V_G,
    VCC,
)

V_TOL = 0.015
ANG_TOL = 1.0


class TestADXL206:

    def test_zero_g_output(self):
        v = acceleration_to_voltage(0.0, noise=False)
        assert abs(v - ZERO_G_OUTPUT_V) < V_TOL

    def test_positive_1g_output(self):
        expected = ZERO_G_OUTPUT_V + 1.0 * SENSITIVITY_V_G
        v = acceleration_to_voltage(1.0, noise=False)
        assert abs(v - expected) < V_TOL

    def test_negative_1g_output(self):
        expected = ZERO_G_OUTPUT_V - 1.0 * SENSITIVITY_V_G
        v = acceleration_to_voltage(-1.0, noise=False)
        assert abs(v - expected) < V_TOL

    def test_full_scale_positive(self):
        v = acceleration_to_voltage(5.0, noise=False)
        assert v <= VCC and v >= 0.0

    def test_over_range_clamps(self):
        v_over = acceleration_to_voltage(10.0, noise=False)
        v_max = acceleration_to_voltage(5.0, noise=False)
        assert abs(v_over - v_max) < V_TOL

    def test_temperature_sensitivity_shift(self):
        from simulation.models.adxl206_model import sensitivity_at_temp, TEMP_COEFF_SENS
        s25 = sensitivity_at_temp(25.0)
        s175 = sensitivity_at_temp(175.0)
        expected_ratio = 1.0 + TEMP_COEFF_SENS * (175.0 - 25.0)
        assert abs(s175 / s25 - expected_ratio) < 0.005

    def test_inclination_45_degrees(self):
        vx, vy = simulate_static_tilt(pitch_deg=45.0, roll_deg=0.0)
        x_g = (vx - ZERO_G_OUTPUT_V) / SENSITIVITY_V_G
        y_g = (vy - ZERO_G_OUTPUT_V) / SENSITIVITY_V_G
        pitch, _ = inclination_from_dual_axis(x_g, y_g)
        assert abs(pitch - 45.0) < ANG_TOL

    def test_level_gives_zero_inclination(self):
        vx, vy = simulate_static_tilt(0.0, 0.0)
        x_g = (vx - ZERO_G_OUTPUT_V) / SENSITIVITY_V_G
        y_g = (vy - ZERO_G_OUTPUT_V) / SENSITIVITY_V_G
        pitch, roll = inclination_from_dual_axis(x_g, y_g)
        assert abs(pitch) < ANG_TOL and abs(roll) < ANG_TOL
