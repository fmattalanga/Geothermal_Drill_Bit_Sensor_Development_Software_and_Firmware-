"""
AT/10/TB IEPE Accelerometer Signal Chain Simulation
Sensitivity: 10 mV/g  |  Range: ±500 g  |  Max Temp: 165°C
Signal chain: ICP source → AC couple → 1.65V offset → 4.8kHz AA filter → ADC
"""
import numpy as np
from scipy.signal import butter, sosfilt

SENSITIVITY_V_PER_G = 0.010   # 10 mV/g
RANGE_G             = 500.0   # ±500 g
DC_OFFSET_V         = 1.65    # Summed bias to centre signal in 0–3.3 V window
ADC_REF_V           = 3.3     # dsPIC33AK ADC reference
ADC_BITS            = 12      # 12-bit ADC
AA_CUTOFF_HZ        = 4800.0  # Anti-alias filter cutoff
SAMPLE_RATE_HZ      = 50000   # 50 kSa/s

def butter_lowpass(cutoff, fs, order=4):
    nyq = fs / 2.0
    normal_cutoff = cutoff / nyq
    return butter(order, normal_cutoff, btype='low', analog=False, output='sos')

def generate_vibration(freq_hz=1000.0, amplitude_g=10.0, duration_s=0.01,
                        noise_g_rms=0.05, fs=SAMPLE_RATE_HZ):
    """Generate synthetic vibration signal in g-units."""
    t = np.arange(0, duration_s, 1.0/fs)
    signal_g = amplitude_g * np.sin(2 * np.pi * freq_hz * t)
    noise    = np.random.normal(0, noise_g_rms, len(t))
    return t, signal_g + noise

def apply_signal_chain(signal_g, fs=SAMPLE_RATE_HZ):
    """
    Apply full AT/10/TB signal chain.
    Returns voltage array at ADC input (0 to 3.3 V).
    """
    # Step 1: Convert g to voltage (sensitivity)
    v_ac = signal_g * SENSITIVITY_V_PER_G

    # Step 2: AC coupling — remove any DC (tantalum cap model: high-pass at ~0.016 Hz)
    # For simulation we assume perfect DC rejection; signal is already AC
    v_ac_coupled = v_ac

    # Step 3: Add 1.65 V DC offset (OPA333AQ summing stage)
    v_offset = v_ac_coupled + DC_OFFSET_V

    # Step 4: Anti-alias Butterworth filter (4.8 kHz, 4th order)
    sos = butter_lowpass(AA_CUTOFF_HZ, fs, order=4)
    v_filtered = sosfilt(sos, v_offset)

    # Step 5: Clamp to ADC rail (0–3.3 V)
    v_clamped = np.clip(v_filtered, 0.0, ADC_REF_V)
    return v_clamped

def voltage_to_counts(v_array):
    """Convert voltage array to 12-bit ADC counts."""
    counts = (v_array / ADC_REF_V) * (2**ADC_BITS - 1)
    return np.round(counts).astype(int)

def counts_to_g(counts):
    """Reverse: ADC counts → g-units (for firmware validation)."""
    v = (counts / (2**ADC_BITS - 1)) * ADC_REF_V
    return (v - DC_OFFSET_V) / SENSITIVITY_V_PER_G
