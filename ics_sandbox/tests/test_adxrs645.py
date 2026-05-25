"""pytest tests for ADXRS645 gyroscope simulation"""
import numpy as np
from simulation.models.adxrs645_model import (
    rate_to_voltage, voltage_to_rate,
    integrate_rate_to_angle, NULL_RATE_V, SENSITIVITY_V_DPS
)

V_TOL    = 0.050  # ±50 mV
RATE_TOL = 5.0    # ±5 °/s round-trip tolerance
ANGLE_TOL = 2.0   # ±2° integration tolerance over 1 second

class TestADXRS645:

    def test_zero_rate_midpoint(self):
        """At 0 °/s, RATEOUT must be VRATIO/2 = 2.5 V"""
        v = rate_to_voltage(0.0, noise=False)
        assert abs(v - NULL_RATE_V) < V_TOL

    def test_positive_rate_voltage(self):
        """At +100 °/s, output = 2.5 + 100 * 0.0125 = 3.75 V"""
        expected = NULL_RATE_V + 100.0 * SENSITIVITY_V_DPS
        v = rate_to_voltage(100.0, noise=False)
        assert abs(v - expected) < V_TOL

    def test_negative_rate_voltage(self):
        """At −100 °/s, output = 2.5 − 1.25 = 1.25 V"""
        expected = NULL_RATE_V - 100.0 * SENSITIVITY_V_DPS
        v = rate_to_voltage(-100.0, noise=False)
        assert abs(v - expected) < V_TOL

    def test_round_trip_rate_accuracy(self):
        """voltage_to_rate(rate_to_voltage(r)) ≈ r"""
        rates = np.array([-2000, -500, -100, 0, 100, 500, 2000], dtype=float)
        for r in rates:
            v = rate_to_voltage(r, noise=False)
            recovered = voltage_to_rate(v)
            assert abs(recovered - r) < RATE_TOL, f"Rate {r} °/s failed round-trip"

    def test_integrate_constant_rate(self):
        """Integrating 90 °/s for 1 second must yield ~90 degrees."""
        dt = 0.001  # 1 ms sample interval
        N  = int(1.0 / dt)
        rates = np.full(N, 90.0)
        angles = integrate_rate_to_angle(rates, dt)
        assert abs(angles[-1] - 90.0) < ANGLE_TOL

    def test_temperature_null_shift(self):
        """At 175°C, null shift must move 0 °/s reading by ~2.25 V equivalent"""
        v_25  = rate_to_voltage(0.0, temp_c=25.0,  noise=False)
        v_175 = rate_to_voltage(0.0, temp_c=175.0, noise=False)
        from simulation.models.adxrs645_model import TEMP_COEFF_NULL
        expected_shift_v = TEMP_COEFF_NULL * (175.0 - 25.0) * SENSITIVITY_V_DPS
        assert abs((v_175 - v_25) - expected_shift_v) < V_TOL
