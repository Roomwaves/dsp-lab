import numpy as np
import soundfile as sf


def load_audio(filepath: str) -> tuple[np.ndarray, float]:
    """
    Carga un archivo de audio (.wav).
    Retorna (signal, fs).
    """
    signal, fs = sf.read(filepath)
    return signal, float(fs)

def save_audio(filepath: str, signal: np.ndarray, fs: float) -> None:
    """
    Guarda una señal como archivo de audio (.wav).
    """
    sf.write(filepath, signal, int(fs))

def load_fir_coefficients(filepath: str) -> np.ndarray:
    """
    Carga coeficientes de un filtro FIR desde un archivo .npy.
    """
    return np.load(filepath)
