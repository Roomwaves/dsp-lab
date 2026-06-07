import numpy as np
import scipy.signal


def compute_psd(signal: np.ndarray, fs: float, n_segments: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Densidad Espectral de Potencia (PSD) de una señal.
    Retorna (frecuencias, Gxx).
    """
    n = len(signal)
    nperseg = max(1, n // n_segments)
    freqs, Gxx = scipy.signal.welch(signal, fs=fs, nperseg=nperseg, noverlap=nperseg//2, scaling='density')
    return freqs, Gxx

def compute_cpsd(x: np.ndarray, y: np.ndarray, fs: float, n_segments: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Densidad Espectral de Potencia Cruzada (CPSD) entre dos señales.
    Retorna (frecuencias, Gxy_complejo).
    """
    n = len(x)
    nperseg = max(1, n // n_segments)
    freqs, Gxy = scipy.signal.csd(x, y, fs=fs, nperseg=nperseg, noverlap=nperseg//2, scaling='density')
    return freqs, Gxy

def compute_coherence(x: np.ndarray, y: np.ndarray, fs: float, n_segments: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la coherencia cuadrática entre dos señales.
    Retorna (frecuencias, coherencia_cuadratica).
    """
    n = len(x)
    nperseg = max(1, n // n_segments)
    freqs, coh = scipy.signal.coherence(x, y, fs=fs, nperseg=nperseg, noverlap=nperseg//2)
    return freqs, coh
