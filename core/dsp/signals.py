import numpy as np

def generate_pure_tones(frequencies: list[float], amplitudes: list[float],
                        fs: float, duration: float) -> np.ndarray:
    """Generate pure tones."""
    raise NotImplementedError

def add_white_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """Add white noise to a signal."""
    raise NotImplementedError