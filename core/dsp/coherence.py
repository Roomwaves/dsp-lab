import numpy as np

def compute_psd(signal: np.ndarray, fs: float, n_segments: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Densidad Espectral de Potencia (PSD) de una señal.
    Retorna (frecuencias, Gxx).
    """
    raise NotImplementedError("Implementar en Issue #8")

def compute_cpsd(x: np.ndarray, y: np.ndarray, fs: float, n_segments: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Densidad Espectral de Potencia Cruzada (CPSD) entre dos señales.
    Retorna (frecuencias, Gxy_complejo).
    """
    raise NotImplementedError("Implementar en Issue #8")

def compute_coherence(x: np.ndarray, y: np.ndarray, fs: float, n_segments: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la coherencia cuadrática entre dos señales.
    Retorna (frecuencias, coherencia_cuadratica).
    """
    raise NotImplementedError("Implementar en Issue #9")
