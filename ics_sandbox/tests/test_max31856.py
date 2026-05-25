"""pytest tests for MAX31856 mock"""
import pytest
from simulation.models.max31856_mock import (
    MAX31856Mock, REG_CJTH, REG_LTCBH, REG_SR,
    FAULT_OPEN, FAULT_TC_HIGH, FAULT_CJ_HIGH,
    TC_RESOLUTION, CJ_RESOLUTION
)

TC_TOLERANCE_C = 0.05   # 5× resolution as round-trip tolerance
CJ_TOLERANCE_C = 0.03

class TestMAX31856:

    def test_tc_25c_round_trip(self):
        """Inject TC=25°C → parse LTCB bytes → recover ~25°C"""
        m = MAX31856Mock()
        m.set_tc_temperature(25.0)
        b = m.spi_read_register(REG_LTCBH)
        result = m.parse_tc_temperature(*b)
        assert abs(result - 25.0) < TC_TOLERANCE_C

    def test_tc_high_temperature(self):
        """Inject TC=1200°C (high geothermal) → round-trip"""
        m = MAX31856Mock()
        m.set_tc_temperature(1200.0)
        b = m.spi_read_register(REG_LTCBH)
        result = m.parse_tc_temperature(*b)
        assert abs(result - 1200.0) < TC_TOLERANCE_C

    def test_tc_negative_temperature(self):
        """Inject TC=−200°C → round-trip negative value"""
        m = MAX31856Mock()
        m.set_tc_temperature(-200.0)
        b = m.spi_read_register(REG_LTCBH)
        result = m.parse_tc_temperature(*b)
        assert abs(result - (-200.0)) < TC_TOLERANCE_C

    def test_cj_temperature_round_trip(self):
        """CJ at 85°C (hot electronics) → parse back correctly"""
        m = MAX31856Mock()
        m.set_cj_temperature(85.0)
        b = m.spi_read_register(REG_CJTH)
        result = m.parse_cj_temperature(*b)
        assert abs(result - 85.0) < CJ_TOLERANCE_C

    def test_cj_out_of_range_raises(self):
        """CJ temperature above 125°C must raise ValueError"""
        m = MAX31856Mock()
        with pytest.raises(ValueError):
            m.set_cj_temperature(130.0)

    def test_fault_open_circuit_detection(self):
        """Inject FAULT_OPEN bit → SR register must report it"""
        m = MAX31856Mock()
        m.inject_fault(FAULT_OPEN)
        sr = m.spi_read_register(REG_SR)[0]
        assert sr & FAULT_OPEN, "Open circuit fault not reported in SR"

    def test_fault_tc_high_detection(self):
        """Inject FAULT_TC_HIGH → SR register must report it"""
        m = MAX31856Mock()
        m.inject_fault(FAULT_TC_HIGH)
        sr = m.spi_read_register(REG_SR)[0]
        assert sr & FAULT_TC_HIGH

    def test_no_fault_clear_sr(self):
        """Normal operation → SR must be 0x00 (no faults)"""
        m = MAX31856Mock()
        sr = m.spi_read_register(REG_SR)[0]
        assert sr == 0x00

    def test_geothermal_temperature_sweep(self):
        """Sweep TC from 0 to 800°C in 50°C steps — all must round-trip within tolerance"""
        m = MAX31856Mock()
        for t in range(0, 850, 50):
            m.set_tc_temperature(float(t))
            b = m.spi_read_register(REG_LTCBH)
            result = m.parse_tc_temperature(*b)
            assert abs(result - t) < TC_TOLERANCE_C, \
                f"FAILED at {t}°C: got {result:.4f}°C"

    def test_resolution_accuracy(self):
        """Resolution must be 0.0078125°C — adjacent codes must differ by this amount"""
        m = MAX31856Mock()
        m.set_tc_temperature(100.0)
        b1 = m.spi_read_register(REG_LTCBH)
        r1 = m.parse_tc_temperature(*b1)
        m.set_tc_temperature(100.0 + TC_RESOLUTION)
        b2 = m.spi_read_register(REG_LTCBH)
        r2 = m.parse_tc_temperature(*b2)
        assert abs((r2 - r1) - TC_RESOLUTION) < 0.0001
