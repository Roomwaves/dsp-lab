import numpy as np

def generate_pure_tones(frequencies: list[float], amplitudes: list[float], fs: float, duration: float) -> np.ndarray:
    """
    Genera una señal suma de tonos puros.
    """
    raise NotImplementedError("Implementar en Issue #4")

def add_white_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Agrega ruido blanco a la señal para alcanzar una SNR especificada en dB.
    """
    raise NotImplementedError("Implementar en Issue #4")
