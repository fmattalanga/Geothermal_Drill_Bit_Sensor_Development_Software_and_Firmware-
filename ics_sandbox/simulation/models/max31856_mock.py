"""
MAX31856 Thermocouple-to-Digital Converter Mock (Type K)
TC Range: −270°C to 1800°C  |  CJC Range: −40°C to 125°C
Resolution: 0.0078125°C (19-bit)  |  Interface: SPI 4-wire
"""
import numpy as np

# Register map (addresses match MAX31856 datasheet Table 1)
REG_CR0   = 0x00  # Config register 0
REG_CR1   = 0x01  # Config register 1 (thermocouple type)
REG_MASK  = 0x02  # Fault mask
REG_CJHF  = 0x03  # CJ high fault threshold
REG_CJLF  = 0x04  # CJ low fault threshold
REG_LTHFTH= 0x05  # LTC high fault MSB
REG_LTHFTL= 0x06  # LTC high fault LSB
REG_LTLFTH= 0x07  # LTC low fault MSB
REG_LTLFTL= 0x08  # LTC low fault LSB
REG_CJTO  = 0x09  # CJ temperature offset
REG_CJTH  = 0x0A  # CJ temperature MSB
REG_CJTL  = 0x0B  # CJ temperature LSB
REG_LTCBH = 0x0C  # Linearised TC temperature MSB
REG_LTCBM = 0x0D  # Linearised TC temperature mid
REG_LTCBL = 0x0E  # Linearised TC temperature LSB
REG_SR    = 0x0F  # Fault status register

# Fault bits (SR register)
FAULT_CJ_RANGE  = 0x80
FAULT_TC_RANGE  = 0x40
FAULT_CJ_HIGH   = 0x20
FAULT_CJ_LOW    = 0x10
FAULT_TC_HIGH   = 0x08
FAULT_TC_LOW    = 0x04
FAULT_OV_UV     = 0x02
FAULT_OPEN      = 0x01

TC_RESOLUTION   = 0.0078125  # °C per LSB (19-bit)
CJ_RESOLUTION   = 0.015625   # °C per LSB (14-bit)


def seebeck_voltage_uv(temp_c):
    """
    Approximate Type K Seebeck voltage (µV) relative to 0°C reference.
    Uses piecewise polynomial approximation (ITS-90 data).
    """
    t = temp_c
    if t < 0:
        return (38.74052e0 * t + 3.329941e-2 * t**2 + 2.061824e-4 * t**3 +
                -2.188225e-6 * t**4)
    else:
        return (39.45013e0 * t - 4.371092e-3 * t**2 + 1.517342e-5 * t**3 +
                -1.028760e-7 * t**4)


class MAX31856Mock:
    """
    Full register-map simulation of MAX31856.
    Inject tc_temp_c and cj_temp_c, call spi_read_register() to get formatted bytes
    exactly as the real chip would return over SPI.
    """
    def __init__(self):
        self._tc_temp_c   = 25.0    # Injected thermocouple temperature
        self._cj_temp_c   = 25.0    # Injected cold-junction temperature
        self._fault_inject = 0x00   # Inject fault bits for fault-detection testing
        self._registers   = {
            REG_CR0: 0x00, REG_CR1: 0x03,  # CR1: Type K default
            REG_MASK: 0xFF, REG_SR: 0x00,
        }

    def set_tc_temperature(self, temp_c):
        """Inject thermocouple (external) temperature."""
        self._tc_temp_c = temp_c

    def set_cj_temperature(self, temp_c):
        """Inject cold-junction (board-level) temperature."""
        if not (-40.0 <= temp_c <= 125.0):
            raise ValueError(f"CJ temp {temp_c}°C out of MAX31856 CJ range")
        self._cj_temp_c = temp_c

    def inject_fault(self, fault_bits):
        """Set fault bits to test fault detection logic in firmware."""
        self._fault_inject = fault_bits

    def _tc_raw(self):
        """Return 19-bit signed integer for TC temperature register."""
        raw = int(round(self._tc_temp_c / TC_RESOLUTION))
        return max(-1 * 2**18, min(2**18 - 1, raw))

    def _cj_raw(self):
        """Return 14-bit signed integer for CJ temperature register."""
        raw = int(round(self._cj_temp_c / CJ_RESOLUTION))
        return max(-1 * 2**13, min(2**13 - 1, raw))

    def spi_read_register(self, reg_addr):
        """
        Return the byte(s) the MAX31856 outputs for a given register read.
        Multi-byte registers return list of bytes (MSB first).
        """
        if reg_addr == REG_CJTH:
            raw = self._cj_raw()
            msb = (raw >> 6) & 0xFF
            lsb = (raw & 0x3F) << 2
            return [msb, lsb]

        elif reg_addr == REG_LTCBH:
            raw = self._tc_raw()
            # 19-bit: bits [18:11] in byte0, [10:3] in byte1, [2:0] in byte2 top bits
            b0 = (raw >> 11) & 0xFF
            b1 = (raw >> 3)  & 0xFF
            b2 = (raw & 0x07) << 5
            return [b0, b1, b2]

        elif reg_addr == REG_SR:
            return [self._fault_inject]

        return [self._registers.get(reg_addr, 0x00)]

    def parse_tc_temperature(self, b0, b1, b2):
        """Parse three LTCB bytes back to temperature (°C)."""
        raw = ((b0 << 11) | (b1 << 3) | (b2 >> 5))
        if raw & (1 << 18):  # Sign bit
            raw -= (1 << 19)
        return raw * TC_RESOLUTION

    def parse_cj_temperature(self, msb, lsb):
        """Parse CJ register bytes to temperature (°C)."""
        raw = ((msb << 6) | (lsb >> 2))
        if raw & (1 << 13):  # Sign bit
            raw -= (1 << 14)
        return raw * CJ_RESOLUTION
