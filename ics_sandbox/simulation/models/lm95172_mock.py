"""
LM95172 SPI Digital Temperature Sensor Mock
Range: −40°C to 200°C  |  Resolution: 13–16 bit  |  Interface: SPI 3-wire
Simulates full register map for firmware SPI driver testing.
"""
import struct

# Register addresses
REG_TEMP   = 0x00   # Temperature register (read)
REG_CONFIG = 0x01   # Configuration register (read/write)

# Configuration bits
CFG_RESOLUTION_13 = 0b00  # 13-bit: 0.0625°C/LSB
CFG_RESOLUTION_14 = 0b01
CFG_RESOLUTION_15 = 0b10
CFG_RESOLUTION_16 = 0b11  # 16-bit: 0.0078125°C/LSB

RESOLUTION_LSB = {
    CFG_RESOLUTION_13: 0.0625,
    CFG_RESOLUTION_14: 0.03125,
    CFG_RESOLUTION_15: 0.015625,
    CFG_RESOLUTION_16: 0.0078125,
}

TEMP_MIN_C = -40.0
TEMP_MAX_C = 200.0
ACCURACY_C = 1.0    # ±1°C (datasheet)


class LM95172Mock:
    """
    Software mock of LM95172 temperature sensor.
    Inject temperature via set_temperature().
    Call spi_read() to get formatted 16-bit SPI word as firmware would see it.
    """
    def __init__(self, resolution=CFG_RESOLUTION_13):
        self._temp_c    = 25.0
        self._config    = resolution
        self._fault     = False

    def set_temperature(self, temp_c):
        """Inject a known temperature for test validation."""
        if not (TEMP_MIN_C <= temp_c <= TEMP_MAX_C):
            raise ValueError(f"Temperature {temp_c}°C out of sensor range")
        self._temp_c = temp_c

    def spi_read_temperature(self):
        """
        Return 16-bit SPI word as the LM95172 would output.
        Bits [15:3] = temperature (two's complement, left-aligned at 13-bit).
        Bit [2]     = conversion complete flag (1 = ready).
        """
        lsb = RESOLUTION_LSB[self._config]
        raw_int = int(round(self._temp_c / lsb))
        # Clamp to 13-bit signed range
        raw_int = max(-4096, min(4095, raw_int))
        # Left-align in 16-bit word (shift left by 3 for 13-bit mode)
        shift = {0b00: 3, 0b01: 2, 0b10: 1, 0b11: 0}[self._config]
        word = (raw_int << shift) & 0xFFFF
        word |= 0x0004  # Conversion complete bit
        return word

    def parse_temperature(self, spi_word):
        """
        Parse a 16-bit SPI word back to temperature (°C).
        Mirrors what firmware would do after reading from the sensor.
        """
        shift = {0b00: 3, 0b01: 2, 0b10: 1, 0b11: 0}[self._config]
        raw = (spi_word >> shift) & 0x1FFF  # 13 bits
        if raw & 0x1000:  # Sign bit
            raw -= 0x2000
        lsb = RESOLUTION_LSB[self._config]
        return raw * lsb
