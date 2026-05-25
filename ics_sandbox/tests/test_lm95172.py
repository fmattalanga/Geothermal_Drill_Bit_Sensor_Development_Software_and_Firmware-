import pytest
from simulation.models.lm95172_mock import (
    LM95172Mock,
    CFG_RESOLUTION_13,
    CFG_RESOLUTION_16,
    TEMP_MIN_C,
    TEMP_MAX_C,
    ACCURACY_C,
)

TEMP_TOLERANCE_C = 0.1


class TestLM95172:

    def test_25c_round_trip(self):
        sensor = LM95172Mock()
        sensor.set_temperature(25.0)
        word = sensor.spi_read_temperature()
        result = sensor.parse_temperature(word)
        assert abs(result - 25.0) < TEMP_TOLERANCE_C

    def test_negative_temperature(self):
        sensor = LM95172Mock()
        sensor.set_temperature(-40.0)
        word = sensor.spi_read_temperature()
        result = sensor.parse_temperature(word)
        assert abs(result - (-40.0)) < TEMP_TOLERANCE_C

    def test_max_temperature(self):
        sensor = LM95172Mock()
        sensor.set_temperature(200.0)
        word = sensor.spi_read_temperature()
        result = sensor.parse_temperature(word)
        assert abs(result - 200.0) < TEMP_TOLERANCE_C

    def test_conversion_complete_flag(self):
        sensor = LM95172Mock()
        sensor.set_temperature(100.0)
        word = sensor.spi_read_temperature()
        assert word & 0x0004

    def test_out_of_range_raises(self):
        sensor = LM95172Mock()
        with pytest.raises(ValueError):
            sensor.set_temperature(201.0)
        with pytest.raises(ValueError):
            sensor.set_temperature(-41.0)

    def test_16bit_resolution_finer(self):
        s13 = LM95172Mock(CFG_RESOLUTION_13)
        s16 = LM95172Mock(CFG_RESOLUTION_16)
        s13.set_temperature(50.03125)
        s16.set_temperature(50.03125)
        r13 = s13.parse_temperature(s13.spi_read_temperature())
        r16 = s16.parse_temperature(s16.spi_read_temperature())
        assert abs(r16 - 50.03125) <= abs(r13 - 50.03125)

    def test_geothermal_operating_range(self):
        sensor = LM95172Mock()
        test_points = [-40, -20, 0, 25, 50, 75, 100, 125, 150, 175, 200]
        for t in test_points:
            sensor.set_temperature(float(t))
            word = sensor.spi_read_temperature()
            result = sensor.parse_temperature(word)
            assert abs(result - t) < ACCURACY_C, f"FAILED at {t}C: got {result:.4f}C"
