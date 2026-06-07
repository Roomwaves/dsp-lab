import numpy as np


def generate_pure_tones(frequencies: list[float], amplitudes: list[float], fs: float, duration: float) -> np.ndarray:
    """
    Genera una señal suma de tonos puros.
    """
    if len(frequencies) != len(amplitudes):
        raise ValueError("frequencies and amplitudes must have the same length")
    num_samples = int(fs * duration)
    t = np.arange(num_samples) / fs
    signal = np.zeros(num_samples)
    for f, a in zip(frequencies, amplitudes):
        signal += a * np.sin(2 * np.pi * f * t)
    return signal

def add_white_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Agrega ruido blanco a la señal para alcanzar una SNR especificada en dB.
    """
    p_signal = np.mean(signal ** 2)
    if p_signal == 0:
        return signal.copy()
    p_noise = p_signal / (10 ** (snr_db / 10.0))
    sigma = np.sqrt(p_noise)
    noise = np.random.normal(0.0, sigma, len(signal))
    return signal + noise

def generate_impulse(length: int, delay: int = 0) -> np.ndarray:
    """
    Genera un impulso unitario (delta de Dirac discreta).
    """
    if delay < 0 or delay >= length:
        raise ValueError("delay must satisfy 0 <= delay < length")
    y = np.zeros(length, dtype=float)
    y[delay] = 1.0
    return y
