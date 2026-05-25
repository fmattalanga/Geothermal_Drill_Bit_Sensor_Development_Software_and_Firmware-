"""pytest test suite for AT/10/TB simulation model"""
import pytest
import numpy as np
from simulation.models.at10tb_model import (
    generate_vibration, apply_signal_chain,
    voltage_to_counts, counts_to_g,
    SENSITIVITY_V_PER_G, DC_OFFSET_V, ADC_REF_V
)

TOLERANCE_G     = 2.0   # ±2 g round-trip tolerance
VOLTAGE_TOL_V   = 0.05  # ±50 mV voltage tolerance

class TestAT10TBSignalChain:

    def test_zero_g_gives_midpoint_voltage(self):
        """At 0 g input the ADC voltage must equal DC_OFFSET_V (1.65 V)"""
        signal_g = np.zeros(1000)
        v = apply_signal_chain(signal_g)
        assert abs(np.mean(v) - DC_OFFSET_V) < VOLTAGE_TOL_V, (
            f"Expected ~{DC_OFFSET_V} V at 0 g, got {np.mean(v):.4f} V")

    def test_positive_peak_voltage(self):
        """100 g peak → voltage peak near 1.65 + (100*0.010) = 2.65 V"""
        _, sig = generate_vibration(freq_hz=100, amplitude_g=100, noise_g_rms=0)
        v = apply_signal_chain(sig)
        expected_peak = DC_OFFSET_V + 100 * SENSITIVITY_V_PER_G
        assert abs(np.max(v) - expected_peak) < VOLTAGE_TOL_V, (
            f"Expected peak ~{expected_peak:.3f} V, got {np.max(v):.4f} V")

    def test_negative_peak_voltage(self):
        """−100 g peak → voltage trough near 1.65 − 1.0 = 0.65 V"""
        _, sig = generate_vibration(freq_hz=100, amplitude_g=100, noise_g_rms=0)
        v = apply_signal_chain(sig)
        expected_trough = DC_OFFSET_V - 100 * SENSITIVITY_V_PER_G
        assert abs(np.min(v) - expected_trough) < VOLTAGE_TOL_V

    def test_max_range_does_not_clip(self):
        """±500 g must NOT saturate the 0–3.3 V ADC rail"""
        _, sig = generate_vibration(freq_hz=100, amplitude_g=500, noise_g_rms=0)
        v = apply_signal_chain(sig)
        assert np.max(v) <= ADC_REF_V + 0.001
        assert np.min(v) >= -0.001

    def test_round_trip_g_accuracy(self):
        """counts_to_g(voltage_to_counts(apply_signal_chain(sig))) ≈ input g"""
        amp_g = 50.0
        _, sig = generate_vibration(freq_hz=200, amplitude_g=amp_g, noise_g_rms=0)
        v   = apply_signal_chain(sig)
        cnt = voltage_to_counts(v)
        recovered = counts_to_g(cnt)
        error = np.max(np.abs(recovered - sig))
        assert error < TOLERANCE_G, f"Round-trip error {error:.2f} g exceeds {TOLERANCE_G} g"

    def test_antialiasing_filter_attenuates_above_cutoff(self):
        """Signal at 20 kHz (above 4.8 kHz cutoff) must be attenuated by >20 dB"""
        _, sig_pass  = generate_vibration(freq_hz=100,   amplitude_g=50, noise_g_rms=0)
        _, sig_alias = generate_vibration(freq_hz=20000, amplitude_g=50, noise_g_rms=0)
        v_pass  = apply_signal_chain(sig_pass)
        v_alias = apply_signal_chain(sig_alias)
        rms_pass  = np.sqrt(np.mean((v_pass - np.mean(v_pass))**2))
        rms_alias = np.sqrt(np.mean((v_alias - np.mean(v_alias))**2))
        ratio_db = 20 * np.log10(rms_alias / (rms_pass + 1e-12))
        assert ratio_db < -20, f"AA filter attenuation only {-ratio_db:.1f} dB at 20 kHz"
