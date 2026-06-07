import matplotlib.pyplot as plt
import numpy as np


def plot_signal(signal: np.ndarray, fs: float, title: str = "Signal", ax=None) -> plt.Figure:
    """
    Grafica una señal en el tiempo.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    t = np.arange(len(signal)) / fs
    ax.plot(t, signal)
    ax.set_title(title)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.grid(True)
    return fig

def plot_spectrum(frequencies: np.ndarray, magnitudes: np.ndarray, title: str = "Spectrum", ax=None, db: bool = False) -> plt.Figure:
    """
    Grafica el espectro de amplitud de una señal.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    
    y_val = 20 * np.log10(np.clip(magnitudes, 1e-15, None)) if db else magnitudes
    ax.plot(frequencies, y_val)
    ax.set_xscale('log')
    ax.set_title(title)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Magnitude [dB]" if db else "Magnitude")
    ax.grid(True, which='both')
    return fig

def plot_frequency_response(frequencies: np.ndarray, H: np.ndarray, title: str = "Frequency Response", fig=None) -> plt.Figure:
    """
    Grafica la respuesta en frecuencia (Módulo en dB y Fase).
    """
    if fig is None:
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    else:
        axes = fig.get_axes()
        if len(axes) >= 2:
            ax1, ax2 = axes[0], axes[1]
        else:
            ax1, ax2 = fig.subplots(2, 1, sharex=True)

    mag_db = 20 * np.log10(np.clip(np.abs(H), 1e-15, None))
    phase = np.angle(H)

    ax1.plot(frequencies, mag_db)
    ax1.set_xscale('log')
    ax1.set_ylabel("Magnitude [dB]")
    ax1.grid(True, which='both')
    ax1.set_title(title)

    ax2.plot(frequencies, phase)
    ax2.set_xscale('log')
    ax2.set_xlabel("Frequency [Hz]")
    ax2.set_ylabel("Phase [rad]")
    ax2.grid(True, which='both')

    return fig

def plot_coherence(frequencies: np.ndarray, coherence: np.ndarray, title: str = "Coherence", ax=None) -> plt.Figure:
    """
    Grafica la coherencia cuadrática.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    
    ax.plot(frequencies, coherence)
    ax.set_xscale('log')
    ax.set_title(title)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Coherence")
    ax.grid(True, which='both')
    return fig
