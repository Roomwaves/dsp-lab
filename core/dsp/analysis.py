import numpy as np


def compute_fft(signal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Transformada de Fourier Discreta de una señal.
    Retorna (frecuencias, magnitudes).
    """
    raise NotImplementedError("Implementar en Issue #5")

def compute_frequency_response(x: np.ndarray, y: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la respuesta en frecuencia H(w) = Y(w) / X(w).
    Retorna (frecuencias, H_complejo).
    """
    raise NotImplementedError("Implementar en Issue #6")

def compute_magnitude_db(H: np.ndarray) -> np.ndarray:
    """
    Calcula el módulo de la respuesta en frecuencia en dB.
    """
    raise NotImplementedError("Implementar en Issue #6")

def compute_phase(H: np.ndarray) -> np.ndarray:
    """
    Calcula la fase de la respuesta en frecuencia en radianes.
    """
    raise NotImplementedError("Implementar en Issue #6")

def convolve_time(signal: np.ndarray, h: np.ndarray) -> np.ndarray:
    """
    Realiza la convolución en el dominio del tiempo.
    """
    raise NotImplementedError("Implementar en Issue #7")

def convolve_frequency(signal: np.ndarray, h: np.ndarray) -> np.ndarray:
    """
    Realiza la convolución circular en el dominio de la frecuencia.
    """
    raise NotImplementedError("Implementar en Issue #7")
