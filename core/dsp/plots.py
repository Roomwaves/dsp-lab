import matplotlib.pyplot as plt
import numpy as np


def plot_signal(signal: np.ndarray, fs: float, title: str = "Signal", ax=None) -> plt.Figure:
    """
    Grafica una señal en el tiempo.
    """
    raise NotImplementedError("Implementar en Issue #10")

def plot_spectrum(frequencies: np.ndarray, magnitudes: np.ndarray, title: str = "Spectrum", ax=None, db: bool = False) -> plt.Figure:
    """
    Grafica el espectro de amplitud de una señal.
    """
    raise NotImplementedError("Implementar en Issue #10")

def plot_frequency_response(frequencies: np.ndarray, H: np.ndarray, title: str = "Frequency Response", fig=None) -> plt.Figure:
    """
    Grafica la respuesta en frecuencia (Módulo en dB y Fase).
    """
    raise NotImplementedError("Implementar en Issue #10")

def plot_coherence(frequencies: np.ndarray, coherence: np.ndarray, title: str = "Coherence", ax=None) -> plt.Figure:
    """
    Grafica la coherencia cuadrática.
    """
    raise NotImplementedError("Implementar en Issue #10")
