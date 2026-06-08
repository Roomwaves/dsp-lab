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

def plot_frequency_response(
    frequencies: np.ndarray,
    H: np.ndarray,
    title: str = "Respuesta en Frecuencia",
    fig=None
) -> plt.Figure:
    """
    Grafica la respuesta en frecuencia de un sistema (Módulo en dB y Fase en
    radianes). Aplica desenrollado de fase automático para un análisis
    riguroso de la linealidad de fase.
    """
    if fig is None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    else:
        axes = fig.get_axes()
        ax1, ax2 = axes[0], axes[1]

    # Cómputo de Magnitud en dB resguardando estabilidad numérico-gráfica
    mag_db = 20 * np.log10(np.clip(np.abs(H), 1e-12, None))
    
    # Desenvolvimiento de fase (unwrap) para revelar fase lineal y retardo
    # de grupo
    phase_unwrapped = np.unwrap(np.angle(H))

    # --- Subplot 1: Magnitud ---
    ax1.semilogx(
        frequencies,
        mag_db,
        color='#1f77b4',
        linewidth=1.8,
        label=r'$|H(\omega)|$'
    )
    ax1.set_ylabel("Magnitud [dB]", fontsize=11, fontweight='bold')
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)
    ax1.grid(True, which='minor', linestyle=':', alpha=0.2)
    ax1.set_title(title, fontsize=13, fontweight='bold', pad=12)
    ax1.legend(loc='upper right')
    
    # Línea de referencia típica a -3 dB si es pertinente al gráfico
    if np.max(mag_db) >= 0 and np.min(mag_db) <= -3:
        ax1.axhline(-3, color='r', linestyle=':', alpha=0.7, label='-3 dB')

    # --- Subplot 2: Fase ---
    ax2.semilogx(
        frequencies,
        phase_unwrapped,
        color='#ff7f0e',
        linewidth=1.8,
        label=r'$\theta(\omega)$'
    )
    ax2.set_xlabel("Frecuencia [Hz]", fontsize=11, fontweight='bold')
    ax2.set_ylabel("Fase [rad]", fontsize=11, fontweight='bold')
    ax2.grid(True, which='both', linestyle='--', alpha=0.5)
    ax2.grid(True, which='minor', linestyle=':', alpha=0.2)
    ax2.legend(loc='upper right')

    # Ajuste fino de márgenes internos
    plt.tight_layout()
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
